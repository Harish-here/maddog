"""Adapter registry. Adding a runtime means one entry in each table here, one adapter file,
and one ladder in ladders.yaml. Tests read these tables to know which words belong to a runtime."""
from pathlib import Path

ADAPTER_SOURCE = {"claude-code": Path(__file__).parent / "claude_code.py"}

# Every tool identifier the runtime's adapter maps or confines. harness/tests/test_runtime_names.py
# flags these as quoted strings outside this folder.
TOOL_IDENTIFIERS = {
    "claude-code": (
        "Agent", "Bash", "CronCreate", "Edit", "Glob", "Grep", "LS", "MultiEdit", "NotebookEdit", "Read",
        "RemoteTrigger", "ScheduleWakeup", "Skill", "Task", "WebFetch", "WebSearch", "Workflow", "Write",
    ),
}


def get_adapter(runtime: str, ladders: dict):
    if runtime == "claude-code":
        from harness.runtimes.claude_code import ClaudeCodeAdapter
        return ClaudeCodeAdapter(ladders["claude-code"])
    raise ValueError(f"unknown runtime {runtime!r}; known: claude-code")


def adapter_source_path(runtime: str) -> Path:
    try:
        return ADAPTER_SOURCE[runtime]
    except KeyError:
        raise ValueError(f"unknown runtime {runtime!r}; known: {', '.join(ADAPTER_SOURCE)}") from None
