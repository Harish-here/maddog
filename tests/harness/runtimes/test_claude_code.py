from harness.core.cases import Case, load_ladders
from harness.runtimes import get_adapter
from harness.runtimes.claude_code import to_event, is_refusal, invocation, usage_from, STOP_REASON, ClaudeCodeAdapter


def test_handoff_maps_agent_id_to_role():
    assert to_event("Agent", {"subagent_type": "maddog:executor-fast-read"}).detail == "Fast-Read"
    assert to_event("Task", {"subagent_type": "maddog:executor-lead"}).detail == "Lead"


def test_unknown_agent_becomes_other():
    e = to_event("Agent", {"subagent_type": "general-purpose"})
    assert e.kind == "handoff" and e.detail == "other:general-purpose"


def test_missing_subagent_type_becomes_other():
    assert to_event("Agent", {}).detail == "other:"


def test_tool_kinds():
    assert to_event("Edit", {"file_path": "a.py"}).kind == "write"
    assert to_event("Write", {"file_path": "a.py"}).detail == "a.py"
    assert to_event("Read", {"file_path": "a.py"}).kind == "read"
    assert to_event("Grep", {"pattern": "x"}).kind == "read"
    assert to_event("Skill", {"skill": "maddog:efficient-md"}).kind == "skill_load"
    assert to_event("Bash", {"command": "git log"}).detail == "git log"
    assert to_event("AskUserQuestion", {}).kind == "command"


def test_shell_writes_count_as_writes():
    assert to_event("Bash", {"command": "sed -i 's/add_item/create_item/g' src/todo/store.py"}).kind == "write"
    assert to_event("Bash", {"command": "echo x > notes.txt"}).kind == "write"
    assert to_event("Bash", {"command": "git checkout feature/export"}).kind == "write"
    assert to_event("Bash", {"command": "git diff main feature/export 2>/dev/null"}).kind == "command"
    assert to_event("Bash", {"command": "pytest -q 2>&1"}).kind == "command"


def test_our_own_stop_is_not_a_refusal():
    assert not is_refusal(True, STOP_REASON)
    assert is_refusal(True, "Permission to use Bash has been denied.")
    assert not is_refusal(False, "permission denied")
    assert not is_refusal(True, "No such file or directory")


def test_invocation():
    with_skill = Case("a", "do it", "Fast", "none", "advisor-mode", "todo-app")
    plain = Case("a", "do it", "Fast", "none", None, "todo-app")
    assert invocation(with_skill) == "/maddog:advisor-mode do it"
    assert invocation(plain) == "do it"


def test_registry_builds_the_adapter_with_its_ladder():
    adapter = get_adapter("claude-code", load_ladders())
    assert isinstance(adapter, ClaudeCodeAdapter)
    assert adapter.ladder["low"] == "claude-haiku-4-5-20251001"


def test_work_starting_tools_stop_the_session():
    from harness.runtimes.claude_code import STOP_TOOLS
    for name in ("Workflow", "RemoteTrigger", "CronCreate", "ScheduleWakeup"):
        assert name in STOP_TOOLS
        assert to_event(name, {}).kind == "command"


def test_usage_from_maps_sdk_field_names():
    raw = {"input_tokens": 100, "output_tokens": 40, "cache_read_input_tokens": 5, "cache_creation_input_tokens": 2}
    assert usage_from(raw) == {
        "input_tokens": 100, "output_tokens": 40, "cache_read_tokens": 5, "cache_creation_tokens": 2,
    }


def test_usage_from_none_or_empty_is_none():
    assert usage_from(None) is None
    assert usage_from({}) is None


def test_usage_from_missing_keys_are_null_not_zero():
    assert usage_from({"input_tokens": 3}) == {
        "input_tokens": 3, "output_tokens": None, "cache_read_tokens": None, "cache_creation_tokens": None,
    }
