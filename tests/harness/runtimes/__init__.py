"""Adapter registry. Adding a runtime means one entry here and one adapter file."""
from pathlib import Path

ADAPTER_SOURCE = {"claude-code": Path(__file__).parent / "claude_code.py"}


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
