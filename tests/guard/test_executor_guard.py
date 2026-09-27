"""Regression tests for scripts/executor-guard.sh.

Invokes the real guard script (`bash scripts/executor-guard.sh`) with a
crafted PreToolUse JSON payload on stdin, exactly the shape the hook itself
receives (agent_type, tool_input.command, cwd). `cwd` always points at a
`tmp_path` workspace holding real files, since the guard's judge allowlist
resolves paths against it and requires them to exist on disk.

No model call, no network — pure subprocess + JSON, like the rest of
tests/harness's unit tests.
"""
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "executor-guard.sh"

JUDGE = "maddog:executor-judge"
LEAD = "executor-lead"
FAST = "executor-fast"


def run_guard(command: str, agent_type: str, cwd: Path):
    payload = {
        "agent_type": agent_type,
        "tool_input": {"command": command},
        "cwd": str(cwd),
    }
    return subprocess.run(
        ["bash", str(GUARD)],
        input=json.dumps(payload),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=10,
    )


def _is_deny(proc: subprocess.CompletedProcess) -> bool:
    out = proc.stdout.strip()
    if not out:
        return False
    data = json.loads(out)
    return data.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"


def assert_deny(command: str, agent_type: str, cwd: Path):
    proc = run_guard(command, agent_type, cwd)
    assert _is_deny(proc), (
        f"expected DENY for {agent_type!r}: {command!r}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )


def assert_allow(command: str, agent_type: str, cwd: Path):
    proc = run_guard(command, agent_type, cwd)
    assert not _is_deny(proc), (
        f"expected ALLOW for {agent_type!r}: {command!r}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )


@pytest.fixture
def ws(tmp_path):
    """A real workspace directory with the files the allowlist forms need
    to resolve against — script files for every interpreter form, plus a
    tests/ subtree pytest/unittest/bun/deno paths can point at."""
    (tmp_path / "script.py").write_text("print('hi')\n")
    (tmp_path / "script.js").write_text("console.log('hi');\n")
    (tmp_path / "script.mjs").write_text("console.log('hi');\n")
    (tmp_path / "script.ts").write_text("console.log('hi');\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_sample.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    return tmp_path


@pytest.fixture
def outside_py(tmp_path_factory):
    """A real, existing .py file OUTSIDE any workspace this test hands the
    guard as `cwd` — stands in for the review's `/usr/lib/python3/
    tarfile.py` example (a real stdlib path that doesn't exist at that
    literal location on every machine/Python build) without depending on
    where this machine's stdlib happens to live."""
    d = tmp_path_factory.mktemp("outside")
    p = d / "outside.py"
    p.write_text("print('should not run')\n")
    return p


# --- REVIEW FINDINGS: judge DENY -------------------------------------

JUDGE_DENY_COMMANDS = [
    # combined python short flags
    'python3 -Ic "print(1)"',
    'python3 -Sc "print(2)"',
    'python3 -Bc "print(3)"',
    "python3 -Im http.server",
    "python3 -Bm pip install x",
    'python3 -W ignore -c "print(4)"',
    'python3 -X dev -c "print(5)"',
    # node
    "node -pe 1",
    "node --import=data:text/javascript,x x.js",
    "node --run build",
    "node --eval=1",
    # bun/deno subcommands
    "bun add lodash",
    "bun install",
    "bun run build",
    "bun x cowsay",
    "deno fmt .",
    "deno run -A x.ts",
    "deno eval 1",
    # pytest options that write / aren't on the allowlist
    "python3 -m pytest --junitxml=README.md",
    "python3 -m pytest --basetemp=src",
    "python3 -m pytest -p some_plugin",
    "python3 -m pytest -o cache_dir=x",
    "python3 -m pytest --result-log=x",
    "python3 -m pytest -c pytest.ini",
    # doctest: denied outright (decision — see header comment)
    "python3 -m doctest README.md",
]


@pytest.mark.parametrize("command", JUDGE_DENY_COMMANDS)
def test_judge_denies_review_finding(command, ws):
    assert_deny(command, JUDGE, ws)


def test_judge_denies_script_outside_cwd(ws, outside_py):
    assert_deny(f"python3 {outside_py} --create x", JUDGE, ws)


# --- pre-existing wrapper gap: both lead and judge -----------------------

WRAPPER_COMMANDS = [
    'sh -c "echo x > f"',
    'bash -c "echo x > f"',
    'zsh -c "echo x > f"',
    "env python3 -c 1",
    "env FOO=1 python3 -c 1",
    "command python3 -c 1",
    "exec python3 -c 1",
    "nice python3 -c 1",
    "nohup python3 -c 1",
    "timeout 5 python3 -c 1",
    "time python3 -c 1",
    "stdbuf -o0 python3 -c 1",
    "FOO=1 python3 -c 1",
]


@pytest.mark.parametrize("command", WRAPPER_COMMANDS)
def test_judge_denies_wrapped_command(command, ws):
    assert_deny(command, JUDGE, ws)


@pytest.mark.parametrize("command", WRAPPER_COMMANDS)
def test_lead_denies_wrapped_command(command, ws):
    assert_deny(command, LEAD, ws)


# --- ALLOWLIST FOR JUDGE: each form, with a real file ---------------------

JUDGE_ALLOW_COMMANDS = [
    # 1. python <script.py>
    "python3 script.py",
    "python3 script.py --flag value",
    # 2. python -m pytest|unittest with allowlisted flags + existing paths
    "python3 -m pytest tests -q",
    "python3 -m pytest tests/test_sample.py -v --tb=short",
    "python3 -m pytest -k foo tests",
    "python3 -m pytest -k=foo tests",
    "python3 -m pytest -rA tests",
    'python3 -m pytest -m "slow" tests',
    "python3 -m pytest tests::test_x",
    "python3 -m unittest tests",
    # 3. node <script>
    "node script.js",
    "node script.mjs",
    # 4. bun <script> / bun run <script> / bun test <paths>
    "bun script.ts",
    "bun run script.ts",
    "bun test tests",
    # 5. deno run <script> / deno test <paths>
    "deno run script.ts",
    "deno test tests",
]


@pytest.mark.parametrize("command", JUDGE_ALLOW_COMMANDS)
def test_judge_allows_allowlisted_form(command, ws):
    assert_allow(command, JUDGE, ws)


def test_judge_denies_pytest_c_flag_via_allowlist_not_inline_heuristic(ws):
    # The review's false-positive check: python3 -m pytest -c pytest.ini
    # stays denied, but because -c is not on the pytest allowlist — not
    # because it looks like python's own -c inline-code flag. Covered
    # already by JUDGE_DENY_COMMANDS; this just pins the reason text.
    proc = run_guard("python3 -m pytest -c pytest.ini", JUDGE, ws)
    data = json.loads(proc.stdout)
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    assert "allow" in reason.lower()


# --- lead still denies every interpreter form, allowlist or not ----------

LEAD_STILL_DENIES = [
    "python3 script.py",
    "python3 -m pytest tests -q",
    "node script.js",
    "bun run script.ts",
    "deno run script.ts",
    "deno test tests",
    "perl -e 1",
]


@pytest.mark.parametrize("command", LEAD_STILL_DENIES)
def test_lead_denies_every_interpreter_form(command, ws):
    assert_deny(command, LEAD, ws)


# --- perl: deny outright for judge too ------------------------------------

def test_judge_denies_perl_even_with_a_real_script(ws):
    (ws / "script.pl").write_text("print \"hi\\n\";\n")
    assert_deny("perl script.pl", JUDGE, ws)


# --- executor-fast: unaffected by any of the above ------------------------

def test_fast_allows_ls(ws):
    assert_allow("ls", FAST, ws)


def test_fast_denies_git_reset_hard(ws):
    assert_deny("git reset --hard", FAST, ws)


# --- shell script syntax --------------------------------------------------

def test_guard_script_has_valid_bash_syntax():
    proc = subprocess.run(
        ["bash", "-n", str(GUARD)], capture_output=True, text=True, timeout=10
    )
    assert proc.returncode == 0, proc.stderr
