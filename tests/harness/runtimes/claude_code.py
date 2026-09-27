"""Claude Code adapter. The only file that knows Claude Code's tools, agent IDs,
models, and SDK. Runs one case and returns its event log."""
import re
from pathlib import Path

import anyio
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
    ToolResultBlock, ToolUseBlock, UserMessage,
)

from harness.core.events import Event

ROLE_TO_AGENT = {
    "Fast-Read": "maddog:executor-fast-read",
    "Fast": "maddog:executor-fast",
    "Smart": "maddog:executor-smart",
    "Judge": "maddog:executor-judge",
    "Lead": "maddog:executor-lead",
}
AGENT_TO_ROLE = {agent: role for role, agent in ROLE_TO_AGENT.items()}

HANDOFF_TOOLS = {"Agent", "Task"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob", "LS", "WebFetch", "WebSearch"}
SKILL_TOOLS = {"Skill"}
WORK_START_TOOLS = {"Workflow", "RemoteTrigger", "CronCreate", "ScheduleWakeup"}  # start work outside the session
STOP_TOOLS = HANDOFF_TOOLS | WRITE_TOOLS | WORK_START_TOOLS  # the session ends at the first of these

STOP_REASON = "maddog-test: session stopped here by the test harness"
MAX_TURNS = 20           # bounds a session that never hands off
SESSION_TIMEOUT = 600    # seconds; bounds a session that stalls without taking turns

# Shell commands that change files or git state count as the advisor doing the work.
SHELL_WRITE = re.compile(
    r"\bsed\s+-i|\bperl\s+-pi|\btee\b|\bmv\b|\brm\b|\bcp\b|\btouch\b|\bmkdir\b"
    r"|\bgit\s+(commit|apply|am|checkout|switch|merge|rebase|reset|restore|add|stash|cherry-pick)\b"
    r"|>"
)
HARMLESS_REDIRECTS = re.compile(r"\d?>\s*/dev/null|\d>&\d")


def to_event(tool_name: str, tool_input: dict) -> Event:
    if tool_name in HANDOFF_TOOLS:
        agent = tool_input.get("subagent_type", "")
        return Event("handoff", AGENT_TO_ROLE.get(agent, f"other:{agent}"))
    if tool_name in WRITE_TOOLS:
        return Event("write", tool_input.get("file_path", tool_name))
    if tool_name in READ_TOOLS:
        return Event("read", tool_name)
    if tool_name in SKILL_TOOLS:
        return Event("skill_load", tool_input.get("skill", ""))
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if SHELL_WRITE.search(HARMLESS_REDIRECTS.sub("", command)):
            return Event("write", command)
        return Event("command", command)
    return Event("command", tool_name)  # any other tool counts as a non-skill call


def is_refusal(is_error: bool, text: str) -> bool:
    if not is_error or STOP_REASON in text:
        return False
    lowered = text.lower()
    return "permission" in lowered and ("denied" in lowered or "not allowed" in lowered)


def invocation(case) -> str:
    if case.skill:
        return f"/maddog:{case.skill} {case.prompt}"
    return case.prompt


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
    return str(content or "")


async def _deny_stop_tools(input_data, tool_use_id, context):
    # Guarantees a helper never starts and no file is written, even if the
    # interrupt below arrives late.
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": STOP_REASON,
    }}


class ClaudeCodeAdapter:
    def __init__(self, ladder: dict[str, str]):
        self.ladder = ladder

    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> list[Event]:
        return anyio.run(self._run, case, plugin_path, workdir, tier)

    async def _run(self, case, plugin_path, workdir, tier) -> list[Event]:
        events: list[Event] = []
        options = ClaudeAgentOptions(
            model=self.ladder[tier],
            cwd=str(workdir),
            plugins=[{"type": "local", "path": str(plugin_path)}],
            setting_sources=[],  # explicit isolation: no user, project, or local settings
            permission_mode="bypassPermissions",
            max_turns=MAX_TURNS,
            hooks={"PreToolUse": [HookMatcher(matcher="|".join(sorted(STOP_TOOLS)), hooks=[_deny_stop_tools])]},
        )
        # On timeout, move_on_after cancels the session and we return the events so far;
        # with no handoff among them, the run scores FAIL "no handoff".
        with anyio.move_on_after(SESSION_TIMEOUT):
            async with ClaudeSDKClient(options=options) as client:
                await client.query(invocation(case))
                async for message in client.receive_response():
                    stop_now = False
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock):
                                events.append(to_event(block.name, dict(block.input)))
                                stop_now = stop_now or block.name in STOP_TOOLS
                    elif isinstance(message, UserMessage) and isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, ToolResultBlock) and is_refusal(bool(block.is_error), _text(block.content)):
                                events.append(Event("refused", _text(block.content)[:120]))
                    if stop_now or (events and events[-1].kind in ("handoff", "write")):
                        await client.interrupt()
                        break
        return events
