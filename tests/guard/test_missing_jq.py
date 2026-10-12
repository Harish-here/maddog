"""Tests for the three hook guards when jq is not installed.

Each hook runs under a PATH that holds bash and a few coreutils but no jq. A payload whose
raw text names one of the hook's guarded agent types must be denied with a static JSON
string; every other payload (no agent type, an unguarded one) must be allowed, so the
user's own main session is never blocked.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts" / "hooks"

# hook script -> (agent types it guards, agent types it must let through)
HOOKS = {
    "executor-guard.sh": (
        ["executor-fast", "executor-smart", "executor-lead", "executor-judge"],
        ["executor-fast-read", "general-purpose", "researcher"],
    ),
    "judge-dispatch-guard.sh": (
        ["executor-judge", "executor-smart"],
        ["executor-fast", "executor-fast-read", "executor-lead", "general-purpose"],
    ),
    "pattern-declare-guard.sh": (
        ["executor-fast", "executor-fast-read"],
        ["executor-smart", "executor-lead", "executor-judge", "general-purpose"],
    ),
}

NEEDED_TOOLS = ["cat", "dirname", "mkdir", "date", "tr"]


@pytest.fixture(scope="module")
def bin_without_jq(tmp_path_factory):
    """A bin dir of symlinks to bash and coreutils, with no jq in it."""
    bindir = tmp_path_factory.mktemp("nojq-bin")
    for tool in ["bash"] + NEEDED_TOOLS:
        found = shutil.which(tool)
        assert found, f"{tool} not found on the test machine"
        (bindir / tool).symlink_to(found)
    assert not (bindir / "jq").exists()
    return bindir


def raw_payload(agent_type, tool_name="Bash", style="compact"):
    """The payload as text, with the agent_type key spaced the way `style` says."""
    body = {"tool_name": tool_name, "tool_input": {"command": "ls", "subagent_type": "executor-fast-read"},
            "cwd": "/tmp", "agent_id": "a1", "session_id": "s1", "transcript_path": "/tmp/s1.jsonl"}
    text = json.dumps(body, separators=(",", ":"))
    if agent_type is None:
        return text
    pair = {"compact": '"agent_type":"%s"', "colon-space": '"agent_type": "%s"',
            "spaced": '"agent_type" : "%s"', "wide": '"agent_type"\n  :\t "%s"'}[style] % agent_type
    return text[:-1] + "," + pair + "}"


def run_hook(script, text, bindir, tmp_path):
    env = {"PATH": str(bindir), "TMPDIR": str(tmp_path)}
    proc = subprocess.run([str(bindir / "bash"), str(SCRIPTS / script)], input=text, capture_output=True,
                          text=True, timeout=10, env=env, cwd=str(tmp_path))
    assert proc.returncode == 0, proc.stderr
    return proc


def assert_missing_jq_deny(proc, script):
    out = json.loads(proc.stdout)  # valid JSON
    hso = out["hookSpecificOutput"]
    assert set(hso) == {"hookEventName", "permissionDecision", "permissionDecisionReason", "additionalContext"}
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["permissionDecision"] == "deny"
    assert "jq" in hso["permissionDecisionReason"] and "install" in hso["permissionDecisionReason"].lower()
    assert "STOP" in hso["additionalContext"] and "return blocked" in hso["additionalContext"]
    assert script in hso["additionalContext"]
    assert "VERDICT" not in proc.stdout


def test_jq_is_hidden_from_the_test_path(bin_without_jq):
    proc = subprocess.run([str(bin_without_jq / "bash"), "-c", "command -v jq"], capture_output=True,
                          env={"PATH": str(bin_without_jq)})
    assert proc.returncode != 0


CASES = [(s, a) for s, (guarded, _) in HOOKS.items() for a in guarded]
ALLOWED = [(s, a) for s, (_, other) in HOOKS.items() for a in other]


@pytest.mark.parametrize("prefix", ["", "maddog:", "plugin:maddog:"])
@pytest.mark.parametrize("script,agent", CASES)
def test_guarded_agent_is_denied_without_jq(script, agent, prefix, bin_without_jq, tmp_path):
    tool = "Agent" if script == "judge-dispatch-guard.sh" else "Bash"
    proc = run_hook(script, raw_payload(prefix + agent, tool), bin_without_jq, tmp_path)
    assert_missing_jq_deny(proc, script)


@pytest.mark.parametrize("style", ["compact", "colon-space", "spaced", "wide"])
@pytest.mark.parametrize("script", list(HOOKS))
def test_whitespace_around_the_colon_is_tolerated(script, style, bin_without_jq, tmp_path):
    agent = HOOKS[script][0][0]
    proc = run_hook(script, raw_payload(agent, "Agent", style), bin_without_jq, tmp_path)
    assert_missing_jq_deny(proc, script)


@pytest.mark.parametrize("script", list(HOOKS))
def test_main_session_without_agent_type_is_allowed(script, bin_without_jq, tmp_path):
    proc = run_hook(script, raw_payload(None, "Agent"), bin_without_jq, tmp_path)
    assert proc.stdout == ""


@pytest.mark.parametrize("prefix", ["", "maddog:"])
@pytest.mark.parametrize("script,agent", ALLOWED)
def test_unguarded_agent_is_allowed_without_jq(script, agent, prefix, bin_without_jq, tmp_path):
    proc = run_hook(script, raw_payload(prefix + agent, "Agent"), bin_without_jq, tmp_path)
    assert proc.stdout == ""


@pytest.mark.parametrize("lookalike", ["executor-fast-readx", "xexecutor-fast", "executor-fasts", "executor-fast:"])
def test_only_the_exact_name_matches(lookalike, bin_without_jq, tmp_path):
    for script in HOOKS:
        proc = run_hook(script, raw_payload(lookalike, "Agent"), bin_without_jq, tmp_path)
        assert proc.stdout == "", script


@pytest.mark.parametrize("script", list(HOOKS))
def test_agent_type_text_inside_a_string_value_is_not_a_match(script, bin_without_jq, tmp_path):
    # Quoted inside a JSON string value the key is backslash-escaped, so it is not the key.
    quoted = 'echo "agent_type": "executor-fast"'
    text = json.dumps({"tool_name": "Bash", "tool_input": {"command": quoted}, "cwd": "/tmp"})
    proc = run_hook(script, text, bin_without_jq, tmp_path)
    assert proc.stdout == ""


@pytest.mark.parametrize("script", list(HOOKS))
def test_empty_input_is_allowed(script, bin_without_jq, tmp_path):
    assert run_hook(script, "", bin_without_jq, tmp_path).stdout == ""
