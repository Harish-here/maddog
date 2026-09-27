"""Adapter registry. Adding a runtime means one entry here and one adapter file."""


def get_adapter(runtime: str, ladders: dict):
    if runtime == "claude-code":
        from harness.runtimes.claude_code import ClaudeCodeAdapter
        return ClaudeCodeAdapter(ladders["claude-code"])
    raise ValueError(f"unknown runtime {runtime!r}; known: claude-code")
