"""Tests for the three hook guards when one of the libraries they source fails to load.

Each hook sources scripts/lib/*.sh. If any of them is missing, unreadable or has a syntax
error, the hook must not let a guarded agent through: it falls back to a raw-input match on its
guarded agent types and prints a static deny. Every other payload (no agent type, an unguarded
one, empty input) is still allowed, so the user's own main session is never blocked.

A lib cut off at a function boundary sources without error but leaves every later function
undefined. Each hook lists the functions it needs in REQUIRED_FUNCS and takes the same path when
one is missing; the tests at the end cut each lib before each required function in turn.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"

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


def libs_sourced_by(script):
    """The lib file names a hook sources, read from the hook itself."""
    text = (SCRIPTS / "hooks" / script).read_text()
    return sorted(set(re.findall(r'source "\$LIB/([a-z-]+\.sh)"', text)))


FUNCTION_DEF = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(\) *\{", re.M)


def required_functions(script):
    """The names in a hook's REQUIRED_FUNCS array, read from the hook itself."""
    text = (SCRIPTS / "hooks" / script).read_text()
    body = re.search(r"^REQUIRED_FUNCS=\(\n(.*?)^\)", text, re.M | re.S)
    assert body, f"{script} has no REQUIRED_FUNCS array"
    return body.group(1).split()


def defining_lib(script, name):
    """The lib, among those the hook sources, that defines the function."""
    found = [lib for lib in libs_sourced_by(script)
             if name in FUNCTION_DEF.findall((SCRIPTS / "lib" / lib).read_text())]
    return found


# one case per (hook, lib it sources, way the lib fails)
BREAKS = ["missing", "syntax-error", "unreadable"]
CASES = [(s, lib, how) for s in HOOKS for lib in libs_sourced_by(s) for how in BREAKS]


def raw_payload(agent_type, tool_name="Bash"):
    body = {"tool_name": tool_name, "tool_input": {"command": "ls", "subagent_type": "executor-fast-read"},
            "cwd": "/tmp", "agent_id": "a1", "session_id": "s1", "transcript_path": "/tmp/s1.jsonl"}
    text = json.dumps(body, separators=(",", ":"))
    if agent_type is None:
        return text
    return text[:-1] + ',"agent_type":"%s"}' % agent_type


def broken_copy(tmp_path, lib, how):
    """A copy of scripts/ in which one lib fails to load."""
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    target = scripts / "lib" / lib
    if how == "missing":
        target.unlink()
    elif how == "syntax-error":
        target.write_text("this is ( not valid bash\nfi fi\n")
    else:
        target.chmod(0)
    return scripts


def run_hook(scripts, script, text, tmp_path):
    env = dict(os.environ, TMPDIR=str(tmp_path))
    proc = subprocess.run(["bash", str(scripts / "hooks" / script)], input=text, capture_output=True,
                          text=True, timeout=10, env=env, cwd=str(tmp_path))
    assert proc.returncode == 0, proc.stderr
    return proc


def assert_lib_failure_deny(proc, script):
    out = json.loads(proc.stdout)  # valid JSON
    hso = out["hookSpecificOutput"]
    assert set(hso) == {"hookEventName", "permissionDecision", "permissionDecisionReason", "additionalContext"}
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["permissionDecision"] == "deny"
    assert "failed to load" in hso["permissionDecisionReason"]
    assert "STOP" in hso["additionalContext"] and "return blocked" in hso["additionalContext"]
    assert script in hso["additionalContext"]
    assert "VERDICT" not in proc.stdout


@pytest.fixture(autouse=True)
def not_root():
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("an unreadable file is still readable by root")


def test_every_hook_sources_the_libs_the_cases_name():
    for script in HOOKS:
        assert "hook-io.sh" in libs_sourced_by(script), script


@pytest.mark.parametrize("script,lib,how", CASES)
def test_guarded_agent_is_denied_when_a_lib_fails_to_load(script, lib, how, tmp_path):
    scripts = broken_copy(tmp_path, lib, how)
    for agent in HOOKS[script][0]:
        for prefix in ("", "maddog:"):
            tool = "Agent" if script == "judge-dispatch-guard.sh" else "Bash"
            proc = run_hook(scripts, script, raw_payload(prefix + agent, tool), tmp_path)
            assert_lib_failure_deny(proc, script)


@pytest.mark.parametrize("script,lib,how", CASES)
def test_other_callers_are_allowed_when_a_lib_fails_to_load(script, lib, how, tmp_path):
    scripts = broken_copy(tmp_path, lib, how)
    assert run_hook(scripts, script, raw_payload(None, "Agent"), tmp_path).stdout == ""
    assert run_hook(scripts, script, "", tmp_path).stdout == ""
    for agent in HOOKS[script][1]:
        assert run_hook(scripts, script, raw_payload(agent, "Agent"), tmp_path).stdout == "", agent


@pytest.mark.parametrize("script", list(HOOKS))
def test_lookalike_agent_names_are_not_matched_when_a_lib_fails_to_load(script, tmp_path):
    scripts = broken_copy(tmp_path, "hook-io.sh", "missing")
    for lookalike in ("executor-fast-readx", "xexecutor-fast", "executor-fasts", "executor-fast:"):
        assert run_hook(scripts, script, raw_payload(lookalike, "Agent"), tmp_path).stdout == "", lookalike


# --- a lib cut off at a function boundary ---------------------------------------------------

TRUNCATIONS = [(s, name) for s in HOOKS for name in required_functions(s)]


def truncated_copy(tmp_path, script, name):
    """A copy of scripts/ in which the lib defining `name` ends just before that function."""
    (lib,) = defining_lib(script, name)  # exactly one lib defines it (see the sync test)
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    target = scripts / "lib" / lib
    text = target.read_text()
    start = re.search(r"^" + re.escape(name) + r"\(\) *\{", text, re.M).start()
    target.write_text(text[:start])
    return scripts


@pytest.mark.parametrize("script", list(HOOKS))
def test_required_functions_are_exactly_what_the_sourced_libs_define(script):
    defined = sorted(n for lib in libs_sourced_by(script)
                     for n in FUNCTION_DEF.findall((SCRIPTS / "lib" / lib).read_text()))
    assert sorted(required_functions(script)) == defined


@pytest.mark.parametrize("script,name", TRUNCATIONS)
def test_guarded_agent_is_denied_when_a_lib_is_cut_before_a_required_function(script, name, tmp_path):
    scripts = truncated_copy(tmp_path, script, name)
    tool = "Agent" if script == "judge-dispatch-guard.sh" else "Bash"
    for agent in HOOKS[script][0]:
        proc = run_hook(scripts, script, raw_payload(agent, tool), tmp_path)
        assert_lib_failure_deny(proc, script)


@pytest.mark.parametrize("script", list(HOOKS))
def test_other_callers_are_allowed_when_a_lib_is_cut_before_a_required_function(script, tmp_path):
    names = required_functions(script)
    for i, name in enumerate((names[0], names[len(names) // 2], names[-1])):
        work = tmp_path / str(i)
        work.mkdir()
        scripts = truncated_copy(work, script, name)
        assert run_hook(scripts, script, raw_payload(None, "Agent"), tmp_path).stdout == ""
        assert run_hook(scripts, script, "", tmp_path).stdout == ""
        for agent in HOOKS[script][1]:
            assert run_hook(scripts, script, raw_payload(agent, "Agent"), tmp_path).stdout == "", agent


def test_complete_libs_do_not_take_the_lib_failure_path(tmp_path):
    payload = {"agent_type": "executor-fast", "tool_input": {"command": "git reset --hard"}, "cwd": str(tmp_path)}
    proc = run_hook(SCRIPTS, "executor-guard.sh", json.dumps(payload), tmp_path)
    hso = json.loads(proc.stdout)["hookSpecificOutput"]
    assert hso["permissionDecision"] == "deny"
    assert "failed to load" not in hso["permissionDecisionReason"]
