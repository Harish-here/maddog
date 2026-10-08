"""Regression tests for scripts/pattern-declare-guard.sh.

Runs the real script with a crafted PreToolUse payload on stdin and a fake
transcript tree under tmp_path, laid out the way Claude Code lays it out:
    <dir>/<session_id>.jsonl                             the parent transcript
    <dir>/<session_id>/subagents/agent-<agent_id>.jsonl  the subagent's own
TMPDIR points at tmp_path so the per-agent marker never touches the real one.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "pattern-declare-guard.sh"
HOOKS = REPO_ROOT / "hooks" / "hooks.json"
PATH = "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="the guard needs jq")

SESSION = "6c7f28ff-9a77-4304-a8c5-ae65ba44de08"


def assistant(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def tool_use():
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}}


def user(text):
    return {"type": "user", "message": {"content": text}}


def write_subagent(tmp_path, agent_id, entries):
    sub = tmp_path / "proj" / SESSION / "subagents" / f"agent-{agent_id}.jsonl"
    sub.parent.mkdir(parents=True, exist_ok=True)
    sub.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return sub


def run_guard(tmp_path, agent_type="maddog:executor-fast", agent_id="a1b2c3", **overrides):
    payload = {"agent_type": agent_type, "agent_id": agent_id, "session_id": SESSION,
               "transcript_path": str(tmp_path / "proj" / f"{SESSION}.jsonl"),
               "tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": str(tmp_path)}
    payload.update(overrides)
    payload = {k: v for k, v in payload.items() if v is not None}
    return subprocess.run(["bash", str(GUARD)], input=json.dumps(payload), capture_output=True, text=True,
                          timeout=10, env={"PATH": PATH, "TMPDIR": str(tmp_path)})


def decision(proc):
    out = proc.stdout.strip()
    if not out:
        return "allow"
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


def test_first_call_with_a_patterns_line_is_allowed(tmp_path):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("PATTERNS: SWEEP\n- SWEEP: grep x; RESULT")])
    assert decision(run_guard(tmp_path)) == "allow"


def test_first_call_without_one_is_denied_with_the_reason(tmp_path):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    proc = run_guard(tmp_path)
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny"
    assert out["permissionDecisionReason"] == "write PATTERNS first, then repeat the call"
    assert proc.returncode == 0


def test_the_second_call_is_allowed_even_though_the_line_is_still_missing(tmp_path):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    assert decision(run_guard(tmp_path)) == "deny"
    assert decision(run_guard(tmp_path)) == "allow"
    assert decision(run_guard(tmp_path)) == "allow"


def test_a_quote_of_the_line_in_the_dispatch_prompt_does_not_count(tmp_path):
    write_subagent(tmp_path, "a1b2c3", [user("Begin with PATTERNS: SWEEP."), assistant("Looking now."), tool_use()])
    assert decision(run_guard(tmp_path)) == "deny"


@pytest.mark.parametrize("text, expected", [
    ("PATTERNS: SWEEP", "allow"),
    ("Starting.\nPATTERNS: SWEEP\n- SWEEP: x; y", "allow"),
    ("   PATTERNS: SWEEP", "allow"),
    ("**PATTERNS:** SWEEP", "allow"),
    ("## PATTERNS: SWEEP", "allow"),
    ("I will write PATTERNS: SWEEP soon", "allow"),
    ("patterns: sweep", "deny"),
    ("No marker in this text.", "deny"),
])
def test_the_marker_rule_is_the_scorers_rule(tmp_path, text, expected):
    # Same cases as test_check1_* in tests/harness/tests/test_agent_score.py: one definition, two places.
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant(text)])
    assert decision(run_guard(tmp_path)) == expected


def test_racing_first_calls_deny_exactly_once(tmp_path):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    payload = json.dumps({"agent_type": "maddog:executor-fast", "agent_id": "a1b2c3", "session_id": SESSION,
                          "transcript_path": str(tmp_path / "proj" / f"{SESSION}.jsonl"), "tool_name": "Read"})
    procs = [subprocess.Popen(["bash", str(GUARD)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                              env={"PATH": PATH, "TMPDIR": str(tmp_path)}) for _ in range(8)]
    outs = [p.communicate(payload, timeout=20)[0] for p in procs]
    assert sum(1 for out in outs if "deny" in out) == 1


def test_a_missing_subagent_log_is_allowed(tmp_path):
    assert decision(run_guard(tmp_path)) == "allow"


def test_a_log_that_is_not_json_is_allowed(tmp_path):
    sub = write_subagent(tmp_path, "a1b2c3", [])
    sub.write_text("not json at all\n{\n")
    assert decision(run_guard(tmp_path)) == "allow"


def test_the_main_conversation_is_allowed(tmp_path):
    assert decision(run_guard(tmp_path, agent_type=None, agent_id=None)) == "allow"


@pytest.mark.parametrize("agent_type", ["maddog:executor-smart", "executor-lead", "general-purpose", "executor-fast-reader"])
def test_other_agents_are_allowed_without_a_line(tmp_path, agent_type):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    assert decision(run_guard(tmp_path, agent_type=agent_type)) == "allow"


@pytest.mark.parametrize("agent_type", ["executor-fast", "maddog:executor-fast", "executor-fast-read", "maddog:executor-fast-read"])
def test_both_fast_agents_are_checked_bare_or_namespaced(tmp_path, agent_type):
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    assert decision(run_guard(tmp_path, agent_type=agent_type)) == "deny"


@pytest.mark.parametrize("bad_id", ["../../etc", "a b", "a/b", "a;b"])
def test_an_agent_id_that_is_not_plain_is_allowed_and_leaves_no_marker(tmp_path, bad_id):
    assert decision(run_guard(tmp_path, agent_id=bad_id)) == "allow"
    assert not (tmp_path / "maddog-pattern-declare").exists()


def test_a_marker_directory_that_cannot_be_made_is_allowed(tmp_path):
    (tmp_path / "maddog-pattern-declare").write_text("a file where the directory should be")
    write_subagent(tmp_path, "a1b2c3", [user("do it"), assistant("Let me look.")])
    assert decision(run_guard(tmp_path)) == "allow"


@pytest.mark.parametrize("payload", ["", "not json"])
def test_empty_and_garbage_payloads_are_allowed(tmp_path, payload):
    proc = subprocess.run(["bash", str(GUARD)], input=payload, capture_output=True, text=True, timeout=10,
                          env={"PATH": PATH, "TMPDIR": str(tmp_path)})
    assert proc.stdout.strip() == "" and proc.returncode == 0


def test_script_has_valid_bash_syntax_and_is_executable():
    assert subprocess.run(["bash", "-n", str(GUARD)], capture_output=True, timeout=10).returncode == 0
    assert GUARD.stat().st_mode & 0o111


def test_hooks_json_wires_the_guard_to_every_tool_the_two_agents_hold():
    hooks = json.loads(HOOKS.read_text())["hooks"]["PreToolUse"]
    entries = [h for h in hooks if any("pattern-declare-guard.sh" in c["command"] for c in h["hooks"])]
    assert len(entries) == 1
    matched = set(entries[0]["matcher"].split("|"))
    assert {"Read", "Grep", "Glob", "Edit", "Write", "Bash", "WebFetch", "WebSearch"} <= matched
    command = entries[0]["hooks"][0]["command"]
    assert command == "${CLAUDE_PLUGIN_ROOT}/scripts/pattern-declare-guard.sh"
    assert (REPO_ROOT / command.replace("${CLAUDE_PLUGIN_ROOT}/", "")).exists()
