"""Offline tests for scripts/hooks/judge-dispatch-guard.sh.

Runs the real script with a crafted PreToolUse payload on stdin. The hook limits what a calling
subagent may dispatch: executor-judge may rent executor-fast-read or researcher; executor-smart
may rent executor-fast or executor-fast-read. Everyone else, and the main conversation, is allowed.

Covered here, one test group per branch of the script:
  non-dispatch tool or unreadable payload -> allow       unguarded caller -> allow
  guarded caller, no target               -> deny        guarded caller, allowed target -> allow
  guarded caller, other target            -> deny        deny output shape and text
  probe logging (off by default, never changes the outcome)
  encode failure while denying            -> allow       a failing date in a probe line
  wiring in hooks/hooks.json
Without jq, and with a lib that is missing or cut short, are tested in test_missing_jq.py and
test_missing_lib.py, which already include this script.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "hooks" / "judge-dispatch-guard.sh"
HOOKS = REPO_ROOT / "hooks" / "hooks.json"
PATH = "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="the guard needs jq")

JUDGE_HANDS = ["executor-fast-read", "researcher"]
SMART_HANDS = ["executor-fast", "executor-fast-read"]
CALLERS = {"executor-judge": JUDGE_HANDS, "executor-smart": SMART_HANDS}
EVERY_HAND = ["executor-fast", "executor-fast-read", "researcher"]
NOT_ALLOWED_FOR = {c: [t for t in EVERY_HAND + ["executor-smart", "executor-lead", "executor-judge",
                                                  "general-purpose", "Explore"] if t not in hands]
                   for c, hands in CALLERS.items()}


def run_text(text, tmp_path, env=None):
    env = {"PATH": PATH, "TMPDIR": str(tmp_path)} if env is None else env
    return subprocess.run(["bash", str(GUARD)], input=text, capture_output=True, text=True,
                          timeout=10, env=env, cwd=str(tmp_path))


def dispatch(agent_type, target, **overrides):
    """A PreToolUse payload for an Agent call. target=None leaves subagent_type out."""
    tool_input = {"prompt": "do it", "description": "x"}
    if target is not None:
        tool_input["subagent_type"] = target
    payload = {"tool_name": "Agent", "tool_input": tool_input, "session_id": "s1", "cwd": "/tmp"}
    if agent_type is not None:
        payload.update(agent_type=agent_type, agent_id="a1")
    payload.update(overrides)
    return payload


def run_guard(tmp_path, payload):
    proc = run_text(json.dumps(payload), tmp_path)
    assert proc.returncode == 0, proc.stderr
    return proc


def decision(proc):
    out = proc.stdout.strip()
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "allow"


def verdict(tmp_path, agent_type, target):
    return decision(run_guard(tmp_path, dispatch(agent_type, target)))


# --- allowed dispatches ---

@pytest.mark.parametrize("prefix", ["", "maddog:", "plugin:maddog:"])
@pytest.mark.parametrize("caller,hands", CALLERS.items())
def test_each_caller_may_rent_each_of_its_hands(tmp_path, caller, hands, prefix):
    for hand in hands:
        for target in (hand, "maddog:" + hand):
            proc = run_guard(tmp_path, dispatch(prefix + caller, target))
            assert proc.stdout == "", (caller, target)


# --- denied dispatches ---

@pytest.mark.parametrize("prefix", ["", "maddog:", "plugin:maddog:"])
@pytest.mark.parametrize("caller", CALLERS)
def test_each_caller_is_denied_every_other_target(tmp_path, caller, prefix):
    for target in NOT_ALLOWED_FOR[caller]:
        for named in (target, "maddog:" + target):
            assert verdict(tmp_path, prefix + caller, named) == "deny", (caller, named)


@pytest.mark.parametrize("caller", CALLERS)
@pytest.mark.parametrize("target", ["executor-fast-readx", "xexecutor-fast-read", "executor-fast-read:",
                                    "a:b:executor-fast-read", "Executor-Fast-Read", " executor-fast-read",
                                    "executor-fast-read ", "researcher2", "maddog:"])
def test_a_lookalike_target_is_denied(tmp_path, caller, target):
    assert verdict(tmp_path, caller, target) == "deny"


@pytest.mark.xfail(strict=True, reason="agent_target_in uses grep -Eq, which matches any one line of the target, "
                   "so a subagent_type whose later line is an allowed hand is allowed")
@pytest.mark.parametrize("caller", CALLERS)
def test_a_multi_line_target_is_denied_when_any_line_is_not_a_hand(tmp_path, caller):
    assert verdict(tmp_path, caller, "general-purpose\n" + CALLERS[caller][0]) == "deny"


@pytest.mark.parametrize("target", [5, ["executor-fast-read"], {"name": "executor-fast-read"}])
def test_a_target_that_is_not_a_string_is_denied(tmp_path, target):
    for caller in CALLERS:
        assert verdict(tmp_path, caller, target) == "deny"


def test_the_denial_names_the_caller_the_target_and_the_hands(tmp_path):
    proc = run_guard(tmp_path, dispatch("maddog:executor-judge", "maddog:executor-fast"))
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert set(out) == {"hookEventName", "permissionDecision", "permissionDecisionReason", "additionalContext"}
    assert out["hookEventName"] == "PreToolUse"
    assert out["permissionDecision"] == "deny"
    assert out["permissionDecisionReason"] == (
        "Blocked by judge-dispatch-guard.sh: executor-judge attempted to dispatch 'maddog:executor-fast'. "
        "executor-judge may only rent executor-fast-read or researcher as hands.")
    assert "fix-less by design" in out["additionalContext"]
    assert "STOP and return blocked" in out["additionalContext"]


def test_the_executor_smart_denial_names_its_own_hands_and_reason(tmp_path):
    proc = run_guard(tmp_path, dispatch("executor-smart", "researcher"))
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert "executor-smart attempted to dispatch 'researcher'" in out["permissionDecisionReason"]
    assert "executor-fast or executor-fast-read" in out["permissionDecisionReason"]
    assert "two cheap hands" in out["additionalContext"]


def test_a_target_with_quotes_and_backslashes_still_yields_valid_json(tmp_path):
    proc = run_guard(tmp_path, dispatch("executor-judge", 'we"ird\\target'))
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny"
    assert 'we"ird\\target' in out["permissionDecisionReason"]


# --- a guarded caller that names no target ---

@pytest.mark.parametrize("caller", CALLERS)
@pytest.mark.parametrize("how", ["absent", "empty", "null"])
def test_no_target_is_denied_as_the_default_agent(tmp_path, caller, how):
    payload = dispatch(caller, None if how == "absent" else "")
    if how == "null":
        payload["tool_input"]["subagent_type"] = None
    proc = run_guard(tmp_path, payload)
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    assert out["permissionDecision"] == "deny"
    assert f"{caller} attempted an Agent dispatch with no subagent_type named" in out["permissionDecisionReason"]
    assert "default general-purpose agent" in out["permissionDecisionReason"]
    assert "Naming no subagent_type is not an exemption" in out["additionalContext"]


@pytest.mark.parametrize("caller", CALLERS)
def test_a_payload_with_no_tool_input_is_denied_as_no_target(tmp_path, caller):
    payload = dispatch(caller, "executor-fast-read")
    del payload["tool_input"]
    assert decision(run_guard(tmp_path, payload)) == "deny"


# --- callers the hook leaves alone ---

def test_the_main_conversation_is_allowed_any_target(tmp_path):
    for target in [None, "", "general-purpose", "executor-smart", "executor-fast"]:
        assert verdict(tmp_path, None, target) == "allow", target


@pytest.mark.parametrize("agent_type", ["executor-lead", "maddog:executor-lead", "executor-fast",
                                        "maddog:executor-fast-read", "general-purpose", "researcher",
                                        "executor-judge-x", "xexecutor-smart", "executor-smart:", ""])
def test_an_unguarded_caller_is_allowed_any_target(tmp_path, agent_type):
    for target in [None, "", "general-purpose", "executor-smart", "executor-judge"]:
        assert verdict(tmp_path, agent_type, target) == "allow", target


def test_a_null_agent_type_is_the_main_conversation(tmp_path):
    payload = dispatch(None, "general-purpose")
    payload["agent_type"] = None
    assert decision(run_guard(tmp_path, payload)) == "allow"


# --- a payload the hook does not act on ---

@pytest.mark.parametrize("tool_name", ["Bash", "Read", "Task", "agent", "", None])
@pytest.mark.parametrize("caller", CALLERS)
def test_a_tool_other_than_agent_is_allowed(tmp_path, caller, tool_name):
    payload = dispatch(caller, "general-purpose", tool_name=tool_name)
    assert decision(run_guard(tmp_path, payload)) == "allow"


@pytest.mark.parametrize("text", ["", "\n", "   ", "not json", "{", '{"tool_name": "Agent"', "[]", "null", "42",
                                  '"executor-judge"'])
def test_empty_and_malformed_payloads_are_allowed(tmp_path, text):
    proc = run_text(text, tmp_path)
    assert proc.stdout == "" and proc.returncode == 0


def test_a_payload_that_names_a_guarded_caller_but_is_malformed_is_allowed_with_jq(tmp_path):
    # Only a missing jq or a missing lib denies on raw text (test_missing_jq.py, test_missing_lib.py).
    text = '{"tool_name": "Agent", "agent_type": "executor-judge", "tool_input": {"subagent_type": "general-purpose"'
    proc = run_text(text, tmp_path)
    assert proc.stdout == "" and proc.returncode == 0


# --- probe logging ---

def probe_files(tmp_path):
    return sorted(p.name for p in tmp_path.iterdir() if "probe" in p.name)


@pytest.mark.parametrize("target", ["executor-fast-read", "general-purpose", None])
def test_probe_logging_is_off_by_default(tmp_path, target):
    run_guard(tmp_path, dispatch("executor-judge", target))
    assert probe_files(tmp_path) == []


def test_an_empty_probe_variable_leaves_logging_off(tmp_path):
    env = {"PATH": PATH, "TMPDIR": str(tmp_path), "MADDOG_DISPATCH_PROBE": ""}
    run_text(json.dumps(dispatch("executor-judge", "general-purpose")), tmp_path, env)
    assert probe_files(tmp_path) == []


def test_probe_logging_writes_one_line_per_guarded_call_when_asked(tmp_path):
    env = {"PATH": PATH, "TMPDIR": str(tmp_path), "MADDOG_DISPATCH_PROBE": "1"}
    first = run_text(json.dumps(dispatch("maddog:executor-judge", "general-purpose")), tmp_path, env)
    second = run_text(json.dumps(dispatch("executor-smart", "executor-fast")), tmp_path, env)
    run_text(json.dumps(dispatch("executor-lead", "general-purpose")), tmp_path, env)  # unguarded: not logged
    assert decision(first) == "deny" and decision(second) == "allow"
    lines = (tmp_path / "maddog-dispatch-probe.log").read_text().splitlines()
    assert len(lines) == 2
    assert "tool_name=Agent agent_type=maddog:executor-judge target=general-purpose" in lines[0]
    assert "agent_type=executor-smart target=executor-fast " in lines[1]


def test_a_probe_line_for_a_call_with_no_target_says_none(tmp_path):
    env = {"PATH": PATH, "TMPDIR": str(tmp_path), "MADDOG_DISPATCH_PROBE": "1"}
    run_text(json.dumps(dispatch("executor-judge", None)), tmp_path, env)
    assert "target=none" in (tmp_path / "maddog-dispatch-probe.log").read_text()


@pytest.mark.parametrize("target, expected", [("executor-fast-read", "allow"), ("general-purpose", "deny")])
def test_a_log_that_cannot_be_written_does_not_change_the_outcome(tmp_path, target, expected):
    (tmp_path / "maddog-dispatch-probe.log").mkdir()  # a directory where the log file should be
    env = {"PATH": PATH, "TMPDIR": str(tmp_path), "MADDOG_DISPATCH_PROBE": "1"}
    proc = run_text(json.dumps(dispatch("executor-judge", target)), tmp_path, env)
    assert proc.returncode == 0
    assert decision(proc) == expected


# --- a denial that cannot be encoded, and a clock that fails ---
# Both tests run the guard under a PATH of shims. The jq shim appends a line to `jq-encode-calls`
# each time it is asked to encode text (-Rs), which only emit_deny does, and fails on the calls
# numbered in JQ_FAIL_CALLS (1 is the reason, 2 is the context). So the files tell three outcomes
# apart even though stdout is empty in all of them:
#   allowed            probe line logged, no encode call
#   reached emit_deny  probe line logged, encode calls made
#   field read broke   no probe line, no encode call


def shim_bin(tmp_path, date_fails=False):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "jq").write_text(
        '#!/bin/bash\n'
        'for a in "$@"; do\n'
        '  if [ "$a" = "-Rs" ]; then\n'
        '    echo x >> "$TMPDIR/jq-encode-calls"\n'
        '    n=$(wc -l < "$TMPDIR/jq-encode-calls")\n'
        '    for f in $JQ_FAIL_CALLS; do [ "$f" -eq "$n" ] && exit 1; done\n'
        '  fi\n'
        'done\n'
        'exec "%s" "$@"\n' % shutil.which("jq"))
    (bindir / "jq").chmod(0o755)
    for tool in ["bash", "cat", "dirname", "tr", "grep", "wc"] + ([] if date_fails else ["date"]):
        (bindir / tool).symlink_to(shutil.which(tool))
    if date_fails:
        (bindir / "date").write_text("#!/bin/bash\nexit 1\n")
        (bindir / "date").chmod(0o755)
    return bindir


def run_shimmed(tmp_path, bindir, payload, fail_calls="", probe=True):
    env = {"PATH": str(bindir), "TMPDIR": str(tmp_path), "JQ_FAIL_CALLS": fail_calls}
    if probe:
        env["MADDOG_DISPATCH_PROBE"] = "1"
    proc = subprocess.run([str(bindir / "bash"), str(GUARD)], input=json.dumps(payload), capture_output=True,
                          text=True, timeout=10, env=env, cwd=str(tmp_path))
    assert proc.returncode == 0, proc.stderr
    log = tmp_path / "maddog-dispatch-probe.log"
    calls = tmp_path / "jq-encode-calls"
    return (proc, log.read_text().splitlines() if log.exists() else [],
            len(calls.read_text().splitlines()) if calls.exists() else 0)


@pytest.mark.parametrize("fail_calls", ["1 2", "1", "2"])
def test_a_denial_jq_cannot_encode_is_allowed_not_blocked(tmp_path, fail_calls):
    # Failing the reason, the context, or both: nothing is printed, so the call is allowed.
    proc, lines, encode_calls = run_shimmed(tmp_path, shim_bin(tmp_path),
                                            dispatch("executor-judge", "general-purpose"), fail_calls)
    assert proc.stdout == ""
    assert len(lines) == 1 and "target=general-purpose" in lines[0]  # the field reads worked
    assert encode_calls == 2  # emit_deny ran and tried to encode both texts


def test_the_working_encoder_denies_the_same_dispatch(tmp_path):
    # Control: with no encode call failing, the shimmed PATH prints the deny for the same payload.
    proc, lines, encode_calls = run_shimmed(tmp_path, shim_bin(tmp_path),
                                            dispatch("executor-judge", "general-purpose"))
    assert decision(proc) == "deny"
    assert len(lines) == 1 and encode_calls == 2


def test_a_no_target_denial_jq_cannot_encode_is_allowed_not_blocked(tmp_path):
    proc, lines, encode_calls = run_shimmed(tmp_path, shim_bin(tmp_path),
                                            dispatch("executor-smart", None), "1 2")
    assert proc.stdout == ""
    assert len(lines) == 1 and "target=none" in lines[0]
    assert encode_calls == 2


def test_an_allowed_dispatch_never_reaches_the_encoder(tmp_path):
    # Control for the tests above: an allowed call under the failing encoder logs its line and
    # makes no encode call, which a call that reached emit_deny would.
    proc, lines, encode_calls = run_shimmed(tmp_path, shim_bin(tmp_path),
                                            dispatch("executor-judge", "executor-fast-read"), "1 2")
    assert proc.stdout == ""
    assert len(lines) == 1 and "target=executor-fast-read" in lines[0]
    assert encode_calls == 0


@pytest.mark.parametrize("date_fails, stamp", [(False, r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ"), (True, "unknown")])
def test_the_probe_line_is_stamped_and_says_unknown_when_date_fails(tmp_path, date_fails, stamp):
    payload = dispatch("executor-judge", "general-purpose")
    proc, lines, _ = run_shimmed(tmp_path, shim_bin(tmp_path, date_fails), payload)
    assert decision(proc) == "deny"  # a failing clock changes nothing about the outcome
    assert len(lines) == 1
    assert re.match(stamp + r"\ttool_name=Agent agent_type=executor-judge target=general-purpose ", lines[0])


# --- the script and its wiring ---

def test_script_has_valid_bash_syntax_and_is_executable():
    assert subprocess.run(["bash", "-n", str(GUARD)], capture_output=True, timeout=10).returncode == 0
    assert os.access(GUARD, os.X_OK)


def test_hooks_json_wires_the_guard_to_agent_dispatches_only():
    hooks = json.loads(HOOKS.read_text())["hooks"]["PreToolUse"]
    entries = [h for h in hooks if any("judge-dispatch-guard.sh" in c["command"] for c in h["hooks"])]
    assert len(entries) == 1
    assert entries[0]["matcher"] == "Agent"
    command = entries[0]["hooks"][0]["command"]
    # The placeholder is double-quoted so an install path with a space does not split the command.
    assert command == '"${CLAUDE_PLUGIN_ROOT}/scripts/hooks/judge-dispatch-guard.sh"'
    assert (REPO_ROOT / command.strip('"').replace("${CLAUDE_PLUGIN_ROOT}/", "")).exists()
