"""Agent mode in the Claude Code adapter: pure helpers and option building. No model."""
import anyio
import pytest
from claude_agent_sdk import AssistantMessage, TextBlock, ToolResultBlock, ToolUseBlock, UserMessage

from harness.core.cases import TESTS_DIR, AgentCase
from harness.core.events import Event
from harness.runtimes.claude_code import (
    AGENT_MAX_TURNS, ClaudeCodeAdapter, agent_events_from, agent_file_stem, confine_hook, confinement_problem,
    parse_agent_file, to_agent_event,
)

REPO = TESTS_DIR.parent


def make_case(role="Fast"):
    return AgentCase("X1", "do it", role, "fast-tier", ("TRANSFORM",), {"kind": ["read"], "target": "."}, {})


def test_to_agent_event_keeps_each_target():
    assert to_agent_event("Read", {"file_path": "/w/a.py"}) == Event("read", "/w/a.py")
    assert to_agent_event("Grep", {"pattern": "add_item", "path": "src"}) == Event("read", "add_item src")
    assert to_agent_event("Grep", {"pattern": "add_item"}) == Event("read", "add_item")
    assert to_agent_event("Glob", {"pattern": "**/*.py"}) == Event("read", "**/*.py")
    assert to_agent_event("WebFetch", {"url": "https://x.test"}) == Event("read", "https://x.test")
    assert to_agent_event("Edit", {"file_path": "/w/a.py"}) == Event("write", "/w/a.py")
    assert to_agent_event("Write", {"file_path": "/w/b.py"}) == Event("write", "/w/b.py")


def test_to_agent_event_sorts_shell_commands_into_command_and_write():
    assert to_agent_event("Bash", {"command": "python3 -m unittest tests.test_pricing 2>&1"}) == \
        Event("command", "python3 -m unittest tests.test_pricing 2>&1")
    assert to_agent_event("Bash", {"command": "rm var/app.lock"}).kind == "write"
    assert to_agent_event("Bash", {"command": "tail -n 3 var/service.log > var/crash.log"}).kind == "write"
    assert to_agent_event("Bash", {"command": "grep -rn add_item src 2>/dev/null"}).kind == "command"


def test_text_comes_before_the_call_in_one_message():
    message = AssistantMessage(
        content=[TextBlock("PATTERNS: SWEEP"), ToolUseBlock("t1", "Grep", {"pattern": "parse_money"})], model="m")
    assert agent_events_from(message) == [Event("say", "PATTERNS: SWEEP"), Event("read", "parse_money")]


def test_a_chained_shell_call_becomes_one_event_per_step():
    chain = "tail -n 3 var/service.log > var/crash.log && rm var/app.lock; sh bin/start.sh 2>&1 | tail -5"
    message = AssistantMessage(content=[ToolUseBlock("t1", "Bash", {"command": chain})], model="m")
    assert agent_events_from(message) == [
        Event("write", "tail -n 3 var/service.log > var/crash.log"),
        Event("write", "rm var/app.lock"),
        Event("command", "sh bin/start.sh 2>&1 | tail -5"),
    ]


def test_a_shell_call_with_nothing_in_it_still_makes_one_event():
    message = AssistantMessage(content=[ToolUseBlock("t1", "Bash", {"command": " ; "})], model="m")
    assert agent_events_from(message) == [Event("command", " ; ")]


def test_a_refused_tool_result_becomes_a_refused_event():
    message = UserMessage(content=[ToolResultBlock("t1", "Permission to use Bash has been denied.", True)])
    assert [e.kind for e in agent_events_from(message)] == ["refused"]


def test_parse_agent_file_splits_frontmatter_and_body(tmp_path):
    path = tmp_path / "a.md"
    path.write_text("---\nname: a\ntools: Read, Grep\n---\n## Role\n\nbody\n\n---\n\nmore body\n")
    meta, body = parse_agent_file(path)
    assert meta == {"name": "a", "tools": "Read, Grep"}
    assert body.startswith("## Role") and "\n---\n\nmore body" in body  # a rule in the body is kept


def test_parse_agent_file_rejects_a_file_without_frontmatter(tmp_path):
    path = tmp_path / "a.md"
    path.write_text("## Role\n")
    with pytest.raises(ValueError, match="no frontmatter"):
        parse_agent_file(path)


def test_a_role_maps_to_its_agent_file():
    assert agent_file_stem("Fast") == "executor-fast"
    assert agent_file_stem("Fast-Read") == "executor-fast-read"


@pytest.mark.parametrize("role, tools", [
    ("Fast", ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]),
    ("Fast-Read", ["Read", "Glob", "Grep", "WebSearch", "WebFetch"]),
])
def test_agent_options_run_the_agent_file_with_no_plugin_and_only_the_harness_fence(role, tools, tmp_path):
    options = ClaudeCodeAdapter({"low": "haiku-model"}).agent_options(make_case(role), REPO, tmp_path, "low", [])
    assert options.plugins == []                                 # no repo hook can fire
    assert list(options.hooks) == ["PreToolUse"]                 # only the harness's own fence
    assert "Bash" in options.hooks["PreToolUse"][0].matcher and "Read" not in options.hooks["PreToolUse"][0].matcher
    assert options.setting_sources == [] and options.strict_mcp_config is True
    assert options.tools == tools
    assert options.effort == "high"                              # from the agent file's frontmatter
    assert options.model == "haiku-model" and options.max_turns == AGENT_MAX_TURNS
    assert options.system_prompt.startswith("## Role")           # the body, not the frontmatter
    assert "You are EXECUTOR-" in options.system_prompt
    assert options.cwd == str(tmp_path)


def test_agent_options_read_the_agent_file_from_the_plugin_path_given(tmp_path):
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "executor-fast.md").write_text("---\ntools: Read\n---\nOLD BODY\n")
    options = ClaudeCodeAdapter({"low": "m"}).agent_options(make_case(), tmp_path, tmp_path, "low", [])
    assert options.system_prompt == "OLD BODY\n" and options.tools == ["Read"] and options.effort is None


# ---- the fence

def test_file_tools_may_write_inside_the_workdir_only(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    assert confinement_problem("Edit", {"file_path": str(work / "a.py")}, work) is None
    assert confinement_problem("Write", {"file_path": "src/b.py"}, work) is None            # relative: inside
    assert "outside" in confinement_problem("Write", {"file_path": str(tmp_path / "elsewhere.py")}, work)
    assert "outside" in confinement_problem("Edit", {"file_path": "../escape.py"}, work)
    assert "outside" in confinement_problem("Edit", {"file_path": "~/.zshrc"}, work)


def test_the_shell_may_not_reach_out_but_ordinary_commands_pass(tmp_path):
    for command in ("rm var/app.lock", "python3 -m unittest tests.test_pricing 2>&1", "sh bin/start.sh",
                    "tail -n 3 var/service.log > var/crash.log", "grep -rn curl_helper src"):
        assert confinement_problem("Bash", {"command": command}, tmp_path) is None, command
    for command in ("curl https://example.com", "wget x", "git push origin main", "sudo ls", "ssh host ls"):
        assert confinement_problem("Bash", {"command": command}, tmp_path) is not None, command


def test_the_hook_denies_and_records_a_refused_event(tmp_path):
    events = []
    hook = confine_hook(tmp_path, events)
    allowed = anyio.run(hook, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, None, None)
    denied = anyio.run(hook, {"tool_name": "Bash", "tool_input": {"command": "curl x"}}, None, None)
    assert allowed == {} and events == [Event("refused", "a shell command reaches outside the run (network, privilege, or push)")]
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"
