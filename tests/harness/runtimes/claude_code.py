"""Claude Code adapter. The only file that knows Claude Code's tools, agent IDs,
models, and SDK. Runs one case and returns its event log."""
import re
from pathlib import Path

import anyio
import yaml
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, HookMatcher,
    ResultMessage, TextBlock, ToolResultBlock, ToolUseBlock, UserMessage,
)

from harness.core.cases import AgentCase
from harness.core.events import Event, RunOutcome
from harness.core.fixture import changed_files
from harness.core.score import settled
from harness.core.shell import split_shell

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
AGENT_MAX_TURNS = 40     # bounds an agent-mode session that never returns
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


def agent_file_stem(role: str) -> str:
    """The file under agents/ a role runs from: Fast -> executor-fast."""
    return ROLE_TO_AGENT[role].split(":", 1)[1]


def to_agent_event(tool_name: str, tool_input: dict) -> Event:
    """Like to_event, but keeps each call's target (file, search pattern, command):
    agent-mode checks match on it. Names no handoff: an agent-mode session has no helpers."""
    if tool_name in WRITE_TOOLS:
        return Event("write", tool_input.get("file_path", tool_name))
    if tool_name == "Read":
        return Event("read", tool_input.get("file_path", ""))
    if tool_name in ("Grep", "Glob"):
        return Event("read", " ".join(part for part in (tool_input.get("pattern", ""), tool_input.get("path", "")) if part))
    if tool_name == "WebFetch":
        return Event("read", tool_input.get("url", ""))
    if tool_name == "WebSearch":
        return Event("read", tool_input.get("query", ""))
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        writes = SHELL_WRITE.search(HARMLESS_REDIRECTS.sub("", command))
        return Event("write" if writes else "command", command)
    return Event("command", tool_name)


def to_agent_events(tool_name: str, tool_input: dict) -> list[Event]:
    """One event per call, except a shell call: that becomes one event per step of
    its command line (split on &&, ||, ; and newlines), each sorted into command or
    write on its own. A model that chains `capture && delete && start` in one call
    is then scored on the order of the steps, not on the call."""
    if tool_name == "Bash":
        steps = split_shell(tool_input.get("command", ""))
        if steps:
            return [to_agent_event("Bash", {"command": step}) for step in steps]
    return [to_agent_event(tool_name, tool_input)]


def agent_events_from(message) -> list[Event]:
    """The events one streamed message adds in agent mode, in the order the model produced them."""
    out: list[Event] = []
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                out.append(Event("say", block.text))
            elif isinstance(block, ToolUseBlock):
                out.extend(to_agent_events(block.name, dict(block.input)))
    elif isinstance(message, UserMessage) and isinstance(message.content, list):
        for block in message.content:
            if isinstance(block, ToolResultBlock) and is_refusal(bool(block.is_error), _text(block.content)):
                out.append(Event("refused", _text(block.content)[:120]))
    return out


def parse_agent_file(path: Path) -> tuple[dict, str]:
    """Split an agent file into its frontmatter (a dict) and its body. Only the
    first two `---` lines count, so a rule inside the body is left alone."""
    parts = Path(path).read_text().split("---\n", 2)
    if len(parts) != 3 or parts[0] != "":
        raise ValueError(f"{path}: no frontmatter between two '---' lines")
    return yaml.safe_load(parts[1]), parts[2]


# Agent mode lets the agent really run commands and write files, in a throwaway
# workdir with permissions bypassed. These are the cheap fences: the file tools
# may not write outside the workdir, and the shell may not reach out (network,
# privilege, push). This is not a sandbox: a shell command can still write
# outside the workdir. A run that hits a fence is recorded as `refused`, which
# scores VOID and is rerun, so a fence hit is visible rather than a quiet FAIL.
OUTWARD_SHELL = re.compile(r"\b(curl|wget|ssh|scp|sudo)\b|\bgit\s+push\b")


def confinement_problem(tool_name: str, tool_input: dict, workdir: Path) -> str | None:
    if tool_name in WRITE_TOOLS:
        target = Path(tool_input.get("file_path") or tool_input.get("notebook_path") or "").expanduser()
        if not target.is_absolute():
            target = Path(workdir) / target
        if not target.resolve().is_relative_to(Path(workdir).resolve()):
            return f"{tool_name} on {target} is outside the run's workdir"
    if tool_name == "Bash" and OUTWARD_SHELL.search(tool_input.get("command", "")):
        return "a shell command reaches outside the run (network, privilege, or push)"
    return None


def confine_hook(workdir: Path, events: list[Event]):
    """The one hook agent mode registers: this harness's own fence, never a hook from this repo."""
    async def hook(input_data, tool_use_id, context):
        why = confinement_problem(input_data.get("tool_name", ""), input_data.get("tool_input", {}), workdir)
        if why is None:
            return {}
        events.append(Event("refused", why))
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"maddog-test: {why}",
        }}
    return hook


def usage_from(raw: dict | None) -> dict | None:
    """Map the SDK's raw usage dict (Anthropic API field names) to the plain
    fields core records. None when the SDK gave us nothing."""
    if not raw:
        return None
    return {
        "input_tokens": raw.get("input_tokens"),
        "output_tokens": raw.get("output_tokens"),
        "cache_read_tokens": raw.get("cache_read_input_tokens"),
        "cache_creation_tokens": raw.get("cache_creation_input_tokens"),
    }


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

    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> RunOutcome:
        if isinstance(case, AgentCase):
            return anyio.run(self._run_agent, case, plugin_path, workdir, tier)
        return anyio.run(self._run, case, plugin_path, workdir, tier)

    def agent_options(self, case: AgentCase, plugin_path: Path, workdir: Path, tier: str,
                      events: list[Event]) -> ClaudeAgentOptions:
        """Run the agent file as the main session: its body is the system prompt,
        its frontmatter `tools:` line is the tool set and `effort:` line the effort.
        No plugin is loaded, so no hook from this repo can fire: the cases measure
        the agent text alone. The only hook is the harness's own fence
        (`confine_hook`). `plugin_path` only says where the agent file is read
        from (this tree for the branch, the worktree for main)."""
        meta, body = parse_agent_file(Path(plugin_path) / "agents" / f"{agent_file_stem(case.expect)}.md")
        return ClaudeAgentOptions(
            model=self.ladder[tier],
            cwd=str(workdir),
            system_prompt=body,
            tools=[name.strip() for name in meta["tools"].split(",")],
            effort=meta.get("effort"),
            setting_sources=[],       # explicit isolation: no user, project, or local settings
            strict_mcp_config=True,   # and no MCP server from anywhere
            permission_mode="bypassPermissions",
            max_turns=AGENT_MAX_TURNS,
            hooks={"PreToolUse": [HookMatcher(matcher="|".join(sorted(WRITE_TOOLS | {"Bash"})),
                                              hooks=[confine_hook(workdir, events)])]},
        )

    async def _run_agent(self, case, plugin_path, workdir, tier) -> RunOutcome:
        events: list[Event] = []
        cost_usd: float | None = None
        usage: dict | None = None
        options = self.agent_options(case, plugin_path, workdir, tier, events)
        # On timeout, move_on_after cancels the session; the events captured so
        # far still score (a run with no `final` event fails its return checks).
        with anyio.move_on_after(SESSION_TIMEOUT):
            async with ClaudeSDKClient(options=options) as client:
                await client.query(case.prompt)
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        cost_usd = message.total_cost_usd
                        usage = usage_from(message.usage)
                        last_say = next((e.detail for e in reversed(events) if e.kind == "say"), "")
                        events.append(Event("final", message.result or last_say))
                        break
                    events.extend(agent_events_from(message))
        # Whatever the session did, ask git what it left behind.
        events.extend(Event("changed", path) for path in changed_files(workdir))
        return RunOutcome(events, cost_usd, usage)

    async def _run(self, case, plugin_path, workdir, tier) -> RunOutcome:
        events: list[Event] = []
        cost_usd: float | None = None
        usage: dict | None = None
        options = ClaudeAgentOptions(
            model=self.ladder[tier],
            cwd=str(workdir),
            plugins=[{"type": "local", "path": str(plugin_path)}],
            setting_sources=[],  # explicit isolation: no user, project, or local settings
            permission_mode="bypassPermissions",
            max_turns=MAX_TURNS,
            hooks={"PreToolUse": [HookMatcher(matcher="|".join(sorted(STOP_TOOLS)), hooks=[_deny_stop_tools])]},
        )
        # On timeout, move_on_after cancels the session; we return whatever
        # we captured so far (with no handoff, the run scores FAIL "no
        # handoff"; cost/usage stay None, meaning "unavailable").
        with anyio.move_on_after(SESSION_TIMEOUT):
            async with ClaudeSDKClient(options=options) as client:
                await client.query(invocation(case))
                interrupted = False
                async for message in client.receive_response():
                    if isinstance(message, ResultMessage):
                        # The final message of the turn, carrying total cost and
                        # token usage. We keep reading for this even after
                        # interrupting, so cost is captured on every run.
                        cost_usd = message.total_cost_usd
                        usage = usage_from(message.usage)
                        break
                    if interrupted:
                        continue  # draining to the result message; nothing left to record
                    used_tool = False
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock):
                                events.append(to_event(block.name, dict(block.input)))
                                used_tool = True
                    elif isinstance(message, UserMessage) and isinstance(message.content, list):
                        for block in message.content:
                            if isinstance(block, ToolResultBlock) and is_refusal(bool(block.is_error), _text(block.content)):
                                events.append(Event("refused", _text(block.content)[:120]))
                    # Check settled() only once a tool call's result has been
                    # seen (used_tool is False on the result's own message),
                    # so a refusal on the settling call is still recorded.
                    if not used_tool and not interrupted and settled(events):
                        await client.interrupt()
                        interrupted = True
        return RunOutcome(events, cost_usd, usage)
