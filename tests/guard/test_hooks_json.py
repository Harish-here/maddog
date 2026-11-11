"""Every hook command in hooks/hooks.json wraps ${CLAUDE_PLUGIN_ROOT} in a matched pair of double quotes.

Without the quotes, an install path containing a space splits the command, the
guard never starts, and the tool call goes ahead unguarded. The same pattern is
enforced by the "hook command paths exist" step in .github/validate.sh.
"""
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / "hooks" / "hooks.json"

# The whole command: one quoted path that starts at the placeholder, nothing outside the quotes.
QUOTED = re.compile(r'"\$\{CLAUDE_PLUGIN_ROOT\}/([^"]*)"')


def hook_commands():
    hooks = json.loads(HOOKS.read_text())["hooks"]
    return [
        hook["command"]
        for entries in hooks.values()
        for entry in entries
        for hook in entry["hooks"]
    ]


def test_hooks_json_holds_the_three_guard_commands():
    # Guards the guard: an empty list would let the check below pass with nothing to check.
    names = sorted(Path(QUOTED.fullmatch(c).group(1)).name for c in hook_commands())
    assert names == ["executor-guard.sh", "judge-dispatch-guard.sh", "pattern-declare-guard.sh"]


@pytest.mark.parametrize("command", hook_commands())
def test_hook_command_wraps_the_plugin_root_in_matched_double_quotes(command):
    match = QUOTED.fullmatch(command)
    assert match, f"not wrapped in a matched pair of double quotes: {command}"
    assert (REPO_ROOT / match.group(1)).is_file()


@pytest.mark.parametrize(
    "command",
    [
        "${CLAUDE_PLUGIN_ROOT}/scripts/hooks/executor-guard.sh",  # no quotes
        '"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/executor-guard.sh',  # opening quote only
        '${CLAUDE_PLUGIN_ROOT}/scripts/hooks/executor-guard.sh"',  # closing quote only
        "'${CLAUDE_PLUGIN_ROOT}/scripts/hooks/executor-guard.sh'",  # single quotes
        '"${CLAUDE_PLUGIN_ROOT}"/scripts/hooks/executor-guard.sh',  # quotes close early
        '"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/executor-guard.sh""',  # extra closing quote
    ],
)
def test_the_pattern_rejects_a_command_that_is_not_one_matched_pair(command):
    assert QUOTED.fullmatch(command) is None
