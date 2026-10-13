"""Regression tests for scripts/hooks/executor-guard.sh.

Invokes the real guard script (`bash scripts/hooks/executor-guard.sh`) with a
crafted PreToolUse JSON payload on stdin, exactly the shape the hook itself
receives (agent_type, tool_input.command, cwd). `cwd` always points at a
`tmp_path` workspace holding real files — some checks below no longer need
an existing file to deny (option B removed judge's path-aware allowlist),
but the workspace is kept so a command can reference a real path where one
is written into the command string.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
GUARD = SCRIPTS / "hooks" / "executor-guard.sh"

JUDGE = "maddog:executor-judge"
LEAD = "executor-lead"
FAST = "executor-fast"
SMART = "executor-smart"


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


def copy_scripts_with_stub_path_guard(tmp_path: Path) -> Path:
    """A copy of scripts/ whose path-guard library has is_temp_path exiting non-zero.

    The stub is appended to the real library, so every function the hook requires still exists.
    """
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    lib = scripts / "lib" / "path-guard.sh"
    lib.write_text(
        lib.read_text() + "\nnormalize_path() { printf '/tmp'; }\nis_temp_path() { exit 7; }\n"
    )
    return scripts


# the frozen legacy guard allows this and the live walk reaches the recursive-delete check
# inside the substitution, so a stubbed is_temp_path in the LIVE library is what fails
INTERNAL_ERROR_COMMAND = "echo $(rm -r /tmp/x)"


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
    """A real workspace directory with a few files some commands below
    reference by path — no longer load-bearing for judge's verdict (option
    B denies every interpreter form regardless of path), kept so the
    commands still read like realistic re-run invocations."""
    (tmp_path / "script.py").write_text("print('hi')\n")
    (tmp_path / "script.js").write_text("console.log('hi');\n")
    (tmp_path / "script.mjs").write_text("console.log('hi');\n")
    (tmp_path / "script.ts").write_text("console.log('hi');\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_sample.py").write_text("def test_x():\n    assert True\n")
    (tmp_path / "pytest.ini").write_text("[pytest]\n")
    return tmp_path


# --- OPTION B: judge denies every interpreter, every form, like lead -----
# 2026-09-27 release review round 2 (commit 1e3ecec) found the judge
# allowlist this replaced still leaking on `VAR=val` prefix-stripping (F1)
# and on several wrapper forms (F2, covered separately below). Maintainer
# decision: remove the allowlist rather than keep patching it — every one
# of these now denies for judge exactly as it already did for lead.

JUDGE_DENY_COMMANDS = [
    # former allowlisted forms — all deny now that the allowlist is gone
    "python3 script.py",
    "python3 script.py --flag value",
    "python3 -m pytest tests -q",
    "python3 -m pytest tests/test_sample.py -v --tb=short",
    "python3 -m pytest -k foo tests",
    "python3 -m unittest tests",
    "node script.js",
    "node script.mjs",
    "bun script.ts",
    "bun run script.ts",
    "bun test tests",
    "deno run script.ts",
    "deno test tests",
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
    # pytest options that write / aren't on the (now-removed) allowlist
    "python3 -m pytest --junitxml=README.md",
    "python3 -m pytest --basetemp=src",
    "python3 -m pytest -p some_plugin",
    "python3 -m pytest -o cache_dir=x",
    "python3 -m pytest --result-log=x",
    "python3 -m pytest -c pytest.ini",
    # doctest
    "python3 -m doctest README.md",
    # F1: VAR=val prefixes must not launder a pytest/node re-run past denial
    "PYTEST_ADDOPTS=--junitxml=README.md python3 -m pytest tests -q",
    "NODE_OPTIONS='--import=data:text/javascript,x' node script.js",
    # perl: denied outright, real script or not
    "perl script.pl",
    "perl -e 1",
]


@pytest.mark.parametrize("command", JUDGE_DENY_COMMANDS)
def test_judge_denies_every_interpreter_form(command, ws):
    assert_deny(command, JUDGE, ws)


# --- wrapper hardening: both lead and judge -------------------------------
# F2 (release review round 2): the env/nice/exec branches of the wrapper
# stripper dropped some flags, stopped, and left an unrecognized leftover
# flag as the "command" — unclassified, so it fell through to ALLOW. Each
# wrapper branch now denies immediately on any flag/argument form it does
# not fully enumerate, instead of falling through.

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
    # F2 escapes: previously ALLOWED for both lead and judge
    'env -S \'sh -c "echo x > f"\'',
    "env -P /usr/bin python3 -c 1",
    "nice -n5 python3 -c 1",
    "nice --adjustment=5 python3 -c 1",
    "exec -a foo python3 -c 1",
]


@pytest.mark.parametrize("command", WRAPPER_COMMANDS)
def test_judge_denies_wrapped_command(command, ws):
    assert_deny(command, JUDGE, ws)


@pytest.mark.parametrize("command", WRAPPER_COMMANDS)
def test_lead_denies_wrapped_command(command, ws):
    assert_deny(command, LEAD, ws)


# --- lead still denies every interpreter form -----------------------------

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


# --- executor-fast: unaffected by any of the above ------------------------

def test_fast_allows_ls(ws):
    assert_allow("ls", FAST, ws)
    assert run_guard("ls", FAST, ws).stdout == ""  # an allow is silent, not a JSON decision


def test_fast_denies_git_reset_hard(ws):
    assert_deny("git reset --hard", FAST, ws)


# --- heredoc bodies --------------------------------------------------------
# A body fed to a non-shell program is data, not commands; a body fed to a
# shell (or to anything the guard cannot identify) is still checked line by
# line, and the skip ends at the delimiter.

def test_fast_allows_python_heredoc_with_paren_body(ws):
    command = "python3 - <<'EOF'\n(1+2)\nEOF"
    assert_allow(command, FAST, ws)
    assert run_guard(command, FAST, ws).stdout == ""


def test_fast_allows_cat_heredoc_to_file(ws):
    assert_allow("cat > f.json <<'EOF'\n{\"a\":1}\nEOF", FAST, ws)


def test_fast_allows_unquoted_delimiter_heredoc(ws):
    assert_allow("python3 - <<EOF\n(1+2)\nEOF", FAST, ws)


def test_fast_allows_spaced_and_quoted_delimiter_heredoc(ws):
    assert_allow('python3 - << "EOF"\n(1+2)\nEOF', FAST, ws)


def test_fast_allows_dash_heredoc_with_tab_indented_terminator(ws):
    assert_allow("python3 - <<-EOF\n\t(1+2)\n\tEOF", FAST, ws)


def test_fast_dash_heredoc_terminator_needs_the_dash(ws):
    # without `-`, a tab-indented line is not the terminator, so the body
    # never ends and is put back: the guard checks it (and denies the '(')
    assert_deny("python3 - <<EOF\n(1+2)\n\tEOF", FAST, ws)


def test_fast_denies_recursive_delete_in_bash_heredoc(ws):
    assert_deny("bash <<'EOF'\nrm -rf /tmp/../etc\nEOF", FAST, ws)


def test_fast_denies_hard_reset_in_sh_heredoc(ws):
    assert_deny("sh <<EOF\ngit reset --hard\nEOF", FAST, ws)


def test_fast_denies_hard_reset_in_path_qualified_shell_heredoc(ws):
    assert_deny("/bin/bash <<EOF\ngit reset --hard\nEOF", FAST, ws)


def test_fast_denies_hard_reset_in_wrapped_shell_heredoc(ws):
    assert_deny("env FOO=1 bash <<EOF\ngit reset --hard\nEOF", FAST, ws)


def test_fast_denies_heredoc_piped_into_shell(ws):
    assert_deny("cat <<'EOF' | bash\ngit reset --hard\nEOF", FAST, ws)


PUSH = "git push --force origin main"


def test_fast_allows_python_dash_heredoc(ws):
    assert_allow("python3 - <<'EOF'\nprint((1+2))\nEOF", FAST, ws)


def test_fast_allows_jq_heredoc(ws):
    assert_allow("jq . <<'EOF'\n{\"a\":(1)}\nEOF", FAST, ws)


def test_fast_allows_heredoc_after_a_chained_command(ws):
    assert_allow("cd . && python3 - <<'EOF'\n(1+2)\nEOF", FAST, ws)


# Each command is a shell-fed or unidentified reader the guard once skipped
# (or could): the body is a push, so it must be checked and denied.
@pytest.mark.parametrize("header", [
    "cat <<'EOF' | \"bash\"",
    "cat <<'EOF' | $SHELL",
    "setsid bash <<'EOF'",
    "flock f bash <<'EOF'",
    "busybox sh <<'EOF'",
    "at now <<'EOF'",
    "parallel <<'EOF'",
    "cat <<'EOF' > >(bash)",
    "while read l; do $l; done <<'EOF'",
    "awk -f /dev/stdin <<'EOF'",
    "\"python3\" - <<'EOF'",
    "$PY - <<'EOF'",
    "cat <<'EOF' && bash",
    "cat <<'EOF'; bash",
])
def test_fast_denies_push_body_unless_reader_is_allowlisted(header, ws):
    assert_deny(f"{header}\n{PUSH}\nEOF", FAST, ws)


def test_fast_denies_body_of_heredoc_header_ending_in_a_pipe(ws):
    assert_deny(f"cat <<'EOF' |\n{PUSH}\nEOF\nbash", FAST, ws)


def test_fast_denies_body_when_next_line_continues_the_pipeline(ws):
    assert_deny(f"cat <<'EOF'\n{PUSH}\nEOF\n| bash", FAST, ws)


def test_fast_denies_body_inside_a_loop_piped_to_a_shell(ws):
    assert_deny(f"for x in 1\ndo\ncat <<'EOF'\n{PUSH}\nEOF\ndone | bash", FAST, ws)


def test_fast_denies_body_when_header_ends_in_a_backslash(ws):
    assert_deny(f"cat <<'EOF' \\\n| bash\n{PUSH}\nEOF", FAST, ws)


def test_fast_denies_body_when_consumer_cannot_be_identified(ws):
    assert_deny("<<EOF\ngit reset --hard\nEOF", FAST, ws)


def test_fast_denies_command_after_skipped_heredoc(ws):
    assert_deny("python3 - <<'EOF'\n(1+2)\nEOF\ngit reset --hard", FAST, ws)


def test_fast_denies_body_when_terminator_never_appears(ws):
    assert_deny("python3 - <<'EOF'\ngit reset --hard", FAST, ws)


def test_fast_skips_only_the_non_shell_body_of_two_heredocs(ws):
    # same line, but `cat` is not a shell: both bodies are data
    assert_allow("cat <<A <<B\n(1)\nA\n(2)\nB", FAST, ws)


def test_lead_and_judge_still_deny_interpreter_with_heredoc(ws):
    command = "python3 - <<'EOF'\nprint(1)\nEOF"
    assert_deny(command, LEAD, ws)
    assert_deny(command, JUDGE, ws)


def test_lead_still_denies_redirect_into_file_with_heredoc(ws):
    assert_deny("cat > f.json <<'EOF'\n{}\nEOF", LEAD, ws)


# --- deny wording ----------------------------------------------------------

def _deny_context(command: str, agent_type: str, cwd: Path) -> str:
    proc = run_guard(command, agent_type, cwd)
    assert _is_deny(proc), proc.stdout
    return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]


IRREVERSIBLE = "git reset --hard"
ALL_AGENTS = [FAST, SMART, LEAD, JUDGE]
# the wrapper stripper (timeout, stdbuf) runs for lead and judge only
SHAPE_COMMANDS = {
    "leading paren": ("(cd x && ls)", ALL_AGENTS),
    "leading brace": ("{ ls; }", ALL_AGENTS),
    "nice missing arg": ("nice -n", [LEAD, JUDGE]),
    "timeout missing arg": ("timeout -s", [LEAD, JUDGE]),
    "timeout missing duration": ("timeout", [LEAD, JUDGE]),
    "stdbuf missing arg": ("stdbuf -o", [LEAD, JUDGE]),
    "function definition": ("f() { :; }", [LEAD, JUDGE]),
    "dynamic command word": ("$G tag v1", [LEAD, JUDGE]),
    "unquoted heredoc substitution": ("cat <<EOF\n$(date)\nEOF", [LEAD, JUDGE]),
    "unclosed substitution": ("echo $(ls", [LEAD, JUDGE]),
}


def test_fast_denial_does_not_claim_a_file_write_ban(ws):
    ctx = _deny_context(IRREVERSIBLE, FAST, ws)
    assert "write files" not in ctx
    assert "irreversible actions" in ctx
    assert "STOP and return blocked" in ctx


def test_smart_denial_does_not_claim_a_file_write_ban(ws):
    assert "write files" not in _deny_context(IRREVERSIBLE, SMART, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_lead_and_judge_denial_names_the_file_write_ban(agent, ws):
    ctx = _deny_context(IRREVERSIBLE, agent, ws)
    assert "write files" in ctx
    assert "STOP and return blocked" in ctx


# an irreversible-action denial keeps STOP for every agent; only the judge's
# text names its own verdict
@pytest.mark.parametrize("agent", [FAST, SMART, LEAD])
def test_irreversible_denial_has_no_judge_wording_outside_the_judge(agent, ws):
    ctx = _deny_context(IRREVERSIBLE, agent, ws)
    assert "STOP and return blocked" in ctx
    assert "executor-judge" not in ctx
    assert "VERDICT" not in ctx


def test_judge_irreversible_denial_names_its_verdict(ws):
    ctx = _deny_context(IRREVERSIBLE, JUDGE, ws)
    assert "STOP and return blocked (VERDICT: STOP)" in ctx


# a shape refusal (the guard could not parse the command) is not a ban: every
# agent is told to rewrite and retry, never to STOP
@pytest.mark.parametrize("name", sorted(SHAPE_COMMANDS))
def test_shape_refusal_tells_every_agent_to_rewrite_and_retry(name, ws):
    command, agents = SHAPE_COMMANDS[name]
    for agent in agents:
        ctx = _deny_context(command, agent, ws)
        assert "not a ban" in ctx, agent
        assert "Rewrite it as simpler, separate commands" in ctx, agent
        assert "retry" in ctx, agent
        assert "STOP" not in ctx, agent
        assert "return blocked" not in ctx, agent
        assert "executor-judge" not in ctx, agent
        assert "VERDICT" not in ctx, agent


def test_issue_64_repro_fast_gets_the_rewrite_hint(ws):
    # the case from #64: a parse-shape refusal whose context said STOP
    ctx = _deny_context("(git add -A && git status)", FAST, ws)
    assert "Rewrite it as simpler, separate commands" in ctx
    assert "STOP" not in ctx


def test_shape_refusal_reason_is_kept(ws):
    proc = run_guard("(ls)", FAST, ws)
    reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "Cannot confidently identify the leading command" in reason


def test_internal_error_backstop_carries_the_shape_context(ws, tmp_path):
    # a library whose is_temp_path exits non-zero stands in for an internal
    # guard bug: the recursive-delete check reaches it after the trap is set
    scripts = copy_scripts_with_stub_path_guard(tmp_path)
    for agent in (LEAD, JUDGE):
        payload = {"agent_type": agent, "tool_input": {"command": INTERNAL_ERROR_COMMAND}, "cwd": str(ws)}
        proc = subprocess.run(
            ["bash", str(scripts / "hooks" / "executor-guard.sh")],
            input=json.dumps(payload), capture_output=True, text=True, timeout=10,
        )
        data = json.loads(proc.stdout)["hookSpecificOutput"]
        assert data["permissionDecision"] == "deny"
        assert "internal error" in data["permissionDecisionReason"]
        assert "Rewrite it as simpler, separate commands" in data["additionalContext"]
        assert "STOP" not in data["additionalContext"]
        assert "VERDICT" not in data["additionalContext"]
        assert "executor-judge" not in data["additionalContext"]


# --- git message heredocs --------------------------------------------------
# `git commit -F -` / `git tag -F -` read their message from stdin and never
# execute it, so a body line starting with `(` is text, not a subshell. Any
# other git form (an option between `git` and the subcommand, a header that
# pipes or chains onward) keeps its body checked.

GIT_BODY = "subject\n\n(core/fixture.py) is the cause\nEOF"


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("header", [
    "git commit -F - <<'EOF'",
    "git commit -q -F - <<'EOF'",
    "git commit -F- <<'EOF'",
    "git commit --file=- <<'EOF'",
    "git commit --file - <<'EOF'",
    "git commit -q --amend -F - <<'EOF'",
    "git tag -a v1 -F - <<'EOF'",
    "git add f && git commit -F - <<'EOF'",
])
def test_git_message_heredoc_body_is_not_checked_as_commands(agent, header, ws):
    assert_allow(f"{header}\n{GIT_BODY}", agent, ws)


@pytest.mark.parametrize("header", [
    "git -C x commit -F - <<'EOF'",
    "git -c core.editor=true commit -F - <<'EOF'",
    "git --no-pager commit -F - <<'EOF'",
    "git commit -F - <<'EOF' && echo done",
    "git commit -F - <<'EOF' | cat",
    "git commit -F - <<'EOF'; echo done",
    "git commit -m x <<'EOF'",
    "git commit -F msg.txt <<'EOF'",
    "git log -F - <<'EOF'",
    "git <<'EOF'",
])
def test_other_git_heredoc_bodies_are_still_checked(header, ws):
    assert_deny(f"{header}\n{GIT_BODY}", FAST, ws)


def test_git_message_heredoc_in_an_open_construct_is_still_checked(ws):
    assert_deny(f"if true; then\ngit commit -F - <<'EOF'\n{GIT_BODY}\nfi", FAST, ws)


def test_command_after_a_skipped_git_message_heredoc_is_checked(ws):
    assert_deny(f"git commit -F - <<'EOF'\n{GIT_BODY}\n(ls)", FAST, ws)


# --- #89: function definitions and command substitution in a heredoc ------
# The guard does not read inside a function body, so lead and judge are refused
# any function definition; fast and smart are not (they may define functions).

FUNCTION_DEFINITIONS = [
    "f() { echo hi; }",
    "f () { echo hi; }",
    "function f { echo hi; }",
    "function f() { echo hi; }",
    "f(){ echo hi; }",
    'f() { bash -c "$MAIN"; }',
    'f() { x=$(bash -c "$MAIN"); }; f',
    'ls && f() { echo hi; }',
    "if true; then f() { echo hi; }; fi",
    "! function f { echo hi; }",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", FUNCTION_DEFINITIONS)
def test_lead_and_judge_deny_every_function_definition(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_may_define_a_function(agent, ws):
    assert_allow("f() { echo hi; }", agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "grep function foo.sh",
    'grep -n "function f" foo.sh',
    "grep 'f()' foo.sh",
    'echo "f() {"',
    "git log --grep='function'",
    "find . -name '*.sh'",
    "echo $(pwd)",
])
def test_lead_and_judge_allow_text_that_only_looks_like_a_definition(agent, command, ws):
    assert_allow(command, agent, ws)


UNQUOTED_HEREDOC_BODIES = [
    "cat <<EOF\n$(touch /tmp/zz)\nEOF",
    "cat <<EOF\n`touch /tmp/zz`\nEOF",
    "cat << EOF\n$(touch /tmp/zz)\nEOF",
    "cat <<-EOF\n\t$(touch /tmp/zz)\n\tEOF",
    "jq . <<EOF\n{\"a\":\"$(touch /tmp/zz)\"}\nEOF",
    "cat <<'A' <<B\nplain\nA\n$(touch /tmp/zz)\nB",
]
QUOTED_HEREDOC_BODIES = [
    "cat <<'EOF'\n$(touch /tmp/zz)\nEOF",
    'cat <<"EOF"\n$(touch /tmp/zz)\nEOF',
    "cat <<\\EOF\n$(touch /tmp/zz)\nEOF",
    "cat << 'EOF'\n`touch /tmp/zz`\nEOF",
    "cat <<-'EOF'\n\t$(touch /tmp/zz)\n\tEOF",
    "cat <<E\"\"OF\n$(touch /tmp/zz)\nEOF",
    "cat <<EOF\nhello $HOME and ${USER}\nEOF",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", UNQUOTED_HEREDOC_BODIES)
def test_lead_and_judge_deny_substitution_in_an_unquoted_heredoc(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", QUOTED_HEREDOC_BODIES)
def test_lead_and_judge_allow_a_quoted_heredoc_and_a_plain_unquoted_one(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", UNQUOTED_HEREDOC_BODIES)
def test_fast_and_smart_keep_unquoted_heredoc_bodies_with_substitution(agent, command, ws):
    # the heredoc gap stays accepted for the two executors that may run commands
    assert_allow(command, agent, ws)


# --- #90: git global options, quoted and dynamic command words ---------------

GIT_WRITES_BEHIND_OPTIONS = [
    "git -C x tag v1",
    "git -C x commit -m m",
    "git -C x add f",
    "git -c k=v tag v1",
    "git -c k=v commit -m m",
    "git --git-dir=.git tag v1",
    "git --git-dir .git tag v1",
    "git --work-tree=. add f",
    "git --work-tree . add f",
    "git --namespace=n commit -m m",
    "git --no-pager tag v1",
    "git --no-pager -C x -c k=v tag v1",
    "git -P tag v1",
    "git --bare tag v1",
    "git -C x restore f",
    "git -C x checkout -- f",
    "git --no-optional-locks tag v1",
    "git --foo tag v1",
    "git --foo log",
    "git -x log",
]
GIT_READS_BEHIND_OPTIONS = [
    "git -C /repo log",
    "git -C /repo log --oneline -5",
    "git -C 'my dir' status",
    "git -c k=v diff",
    "git --git-dir=.git status",
    "git --git-dir .git log",
    "git --no-pager log",
    "git --no-pager -C /repo -c k=v diff",
    "git -P log",
    "git -C /repo tag -l",
    "git --version",
    "git --exec-path",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", GIT_WRITES_BEHIND_OPTIONS)
def test_lead_and_judge_deny_a_git_write_behind_global_options(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", GIT_READS_BEHIND_OPTIONS)
def test_lead_and_judge_allow_a_git_read_behind_global_options(agent, command, ws):
    assert_allow(command, agent, ws)
    assert run_guard(command, agent, ws).stdout == ""


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "git -C x push --force origin main",
    "git -C x push -f",
    "git -c k=v push origin +main",
    "git --git-dir=.git --work-tree=. reset --hard",
    "git --no-pager -C x clean -fd",
    "git -C x checkout .",
    "git -C x branch -D b",
    "git -C x merge b",
    "git -C x worktree remove w",
    "git --foo push --force",
])
def test_every_agent_is_denied_an_irreversible_git_command_behind_options(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", [
    "git -C x tag v1",
    "git -C x commit -m m",
    "git -C x push origin main",
    "git --no-pager log",
    "git --foo log",
])
def test_fast_and_smart_are_unchanged_for_git_options_that_do_nothing_irreversible(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "\\git push --force origin main",
    '"git" push -f',
    'g""it reset --hard',
    "'git' clean -fd",
    '\\rm -rf /etc',
    '"rm" -rf /etc',
    "\\npm publish",
    '"npm" publish',
    "\\find . -delete",
])
def test_every_agent_is_denied_a_quoted_spelling_of_an_irreversible_command(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "\\git tag v1",
    '"git" tag v1',
    'g""it tag v1',
    "g'i't tag v1",
    "git 'tag' v1",
    'git t""ag v1',
    "git ta\\g v1",
    "\\git -C x tag v1",
    "\\bash x",
    '"bash" -c x',
    'b""ash x',
    "\\sh -c x",
    "\\python3 -c 1",
    '"python3" -c 1',
    '"cp" a b',
    "\\touch f",
    "\\rm f",
    'env "bash" x',
    "nice \\bash x",
    "\\env bash x",
    '"timeout" 5 bash x',
])
def test_lead_and_judge_deny_a_quoted_spelling_of_a_guarded_command(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "$G tag v1",
    '"$G" tag v1',
    "${G} tag v1",
    "`echo git` tag v1",
    "$(echo bash) x",
    "$HOME/bin/tool x",
    '"$HOME/bin/tool" x',
    "FOO=1 $G x",
    "env $G x",
    "git $SUB v1",
    'git "$SUB" v1',
])
def test_lead_and_judge_deny_a_command_word_built_at_run_time(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    'git log "$REF"',
    'cat "$F"',
    'FOO=$(pwd) ls',
    'cd "$(git rev-parse --show-toplevel)" && ls',
    'for f in a b; do cat "$f"; done',
    'echo "$HOME"',
])
def test_lead_and_judge_allow_variables_that_are_arguments(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_may_run_a_command_word_built_at_run_time(agent, ws):
    assert_allow("$G tag v1", agent, ws)


# --- #92: rtk is a wrapper --------------------------------------------------

RTK_LAUNDERED = [
    "rtk proxy bash x",
    "rtk proxy sh -c x",
    "rtk proxy python3 -c 1",
    "rtk bash x",
    "rtk proxy env bash x",
    "env rtk proxy bash x",
    "nice rtk proxy bash x",
    "rtk env python3 -c 1",
    "rtk proxy cp a b",
    "rtk proxy rm f",
    "\\rtk proxy bash x",
    '"rtk" proxy bash x',
    'r""tk proxy bash x',
    "rtk proxy git add f",
    "rtk git tag v1",
    "rtk proxy git -C x commit -m m",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", RTK_LAUNDERED)
def test_lead_and_judge_classify_the_command_rtk_runs(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "rtk git push -f",
    "rtk proxy git push --force",
    "rtk proxy git -C x push --force",
    "rtk git reset --hard",
    "rtk proxy rm -rf /etc",
    "rtk rm -rf /etc",
    "\\rtk git push -f",
    '"rtk" git push -f',
    "rtk proxy git push origin +main",
])
def test_every_agent_is_denied_an_irreversible_command_run_through_rtk(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "rtk git status",
    "rtk git log --oneline",
    "rtk proxy git status",
    "rtk proxy git -C /repo log",
    "rtk ls",
    "rtk grep foo f",
    "rtk read f",
    "rtk proxy cat f",
    "rtk",
    "rtk proxy",
    "echo rtk",
    "grep rtk f",
])
def test_lead_and_judge_allow_a_read_only_command_run_through_rtk(agent, command, ws):
    assert_allow(command, agent, ws)
    assert run_guard(command, agent, ws).stdout == ""


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["rtk -v git status", "rtk proxy -x git status", "rtk -v bash x", "rtk --foo ls"])
def test_lead_and_judge_deny_an_option_before_the_command_rtk_runs(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_skip_an_option_before_the_command_rtk_runs(agent, ws):
    assert_allow("rtk -v git status", agent, ws)
    assert_deny("rtk -v git push -f", agent, ws)
    assert_allow("rtk git status", agent, ws)
    assert_allow("rtk proxy bash x", agent, ws)


# --- command substitution: the command inside is checked like any other ----------
# The text inside $(...), a backtick pair and <(...)/>(...) is a command line of its
# own, checked with the same rules as the top level; single-quoted text is not
# expanded, so it is not checked; $((...)) is arithmetic, not a command.

SHELL_IN_SUBSTITUTION = [
    "echo $(bash -c x)",
    'echo "$(bash -c x)"',
    "echo `bash -c x`",
    'echo "`bash -c x`"',
    "echo $(echo $(bash -c x))",
    'echo "a $(echo "b $(bash x)")"',
    "echo `echo \\`bash x\\``",
    "echo $(echo `bash x`)",
    "cat <(bash x)",
    "echo $((1+$(bash x)))",
    "echo $(( $(bash x) + 1 ))",
    "echo $((1+2)) $(bash x)",
    "x=$(bash y)",
    "FOO=$(bash y) ls",
    "echo ${x:-$(bash y)}",
    "echo $(ls; bash x)",
    "echo $(ls | bash)",
    "echo $(\nbash x\n)",
    "echo $(ls)$(bash x)",
    "for f in $(bash x); do cat $f; done",
    "case $(bash x) in a) ls;; esac",
    "echo $(python3 -c 1)",
    "echo $(touch f)",
    "echo $(git -C x tag v1)",
    "echo $(echo bash) $(rm f)",
]
IRREVERSIBLE_IN_SUBSTITUTION = [
    "echo $(git push -f)",
    "echo `git reset --hard`",
    'echo "$(git clean -fd)"',
    "cat <(git push --force origin main)",
    "echo $(echo $(git reset --hard))",
    "echo $((1+$(git reset --hard)))",
    "x=$(git branch -D b)",
    "echo $(rm -rf /etc)",
    "echo $(env git push -f)",
]
SAFE_WITH_SUBSTITUTION = [
    "git diff $(git merge-base main HEAD)",
    "git diff `git merge-base main HEAD`",
    "echo '$(bash x)'",
    "echo '`bash x`'",
    "echo \\$(bash x)",
    "echo $((1+2))",
    'echo "$((1+2))"',
    "echo $(( (1+2)*3 ))",
    "echo $(( $(wc -l < f) + 1 ))",
    "diff <(git show a:f) <(git show b:f)",
    'cd "$(git rev-parse --show-toplevel)" && ls',
    'echo "it\'s $(ls)"',
    'echo "$(echo ")")"',
    "git log --since=\"$(date)\" -1",
    "echo $(date +%s) | wc -c",
    "FOO=$(pwd) ls",
    "echo # a comment holding $(bash x)",
    "awk '{print $1}' f",
    "grep -E '(a|b)' f",
    "echo ${#HOME} $#",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", SHELL_IN_SUBSTITUTION)
def test_lead_and_judge_check_the_command_inside_a_substitution(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", SHELL_IN_SUBSTITUTION[:12])
def test_fast_and_smart_may_run_a_shell_inside_a_substitution(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", IRREVERSIBLE_IN_SUBSTITUTION)
def test_every_agent_is_denied_an_irreversible_command_inside_a_substitution(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", SAFE_WITH_SUBSTITUTION)
def test_substitutions_that_run_nothing_unsafe_stay_allowed(agent, command, ws):
    assert_allow(command, agent, ws)
    assert run_guard(command, agent, ws).stdout == ""


UNBALANCED = ["echo $(ls", "echo `ls", 'echo "$(ls', "cat <(ls", "echo $(echo $(ls)"]


@pytest.mark.parametrize("command", UNBALANCED)
def test_lead_and_judge_are_denied_a_substitution_the_guard_cannot_close(command, ws):
    for agent in (LEAD, JUDGE):
        ctx = _deny_context(command, agent, ws)
        assert "Rewrite it as simpler, separate commands" in ctx
    for agent in (FAST, SMART):
        assert_allow(command, agent, ws)


def test_substitutions_nested_past_the_depth_limit_are_denied_for_lead_and_judge(ws):
    deep = "echo hi"
    for _ in range(10):
        deep = f"echo $({deep})"
    for agent in (LEAD, JUDGE):
        assert_deny(deep, agent, ws)
    assert_allow(deep, FAST, ws)
    # fast and smart read what is left flat past the limit, so a command nested that deep is seen
    hidden = "true; git push -f "
    for _ in range(10):
        hidden = f"echo $({hidden})"
    for agent in (FAST, SMART, LEAD, JUDGE):
        assert_deny(hidden, agent, ws)
    shallow = "echo hi"
    for _ in range(4):
        shallow = f"echo $({shallow})"
    for agent in (LEAD, JUDGE):
        assert_allow(shallow, agent, ws)


# --- shell keywords: the command after them is the command ---------------------

KEYWORD_SHELLS = [
    "if true; then bash -c x; fi",
    "if true; then ls; else bash; fi",
    "if true\nthen\n  bash x\nfi",
    "while true; do bash x; done",
    "until bash x; do ls; done",
    "! bash x",
    "for f in a b; do bash x; done",
    "select x in a b; do bash; done",
    "case x in a) bash -c y;; esac",
    "case x in a) ls;; b) bash;; esac",
    "case $x in a) ls ;;\nb) bash x ;;\nesac",
    "if true; then python3 -c 1; fi",
    "if true; then (cd x); fi",
    "if (cd x); then ls; fi",
]
KEYWORD_SAFE = [
    "for f in a b; do cat $f; done",
    "for f in $(ls); do cat $f; done",
    "for i in 1 2 3; do echo $i; done | wc -l",
    "if git diff --quiet; then echo clean; else echo dirty; fi",
    "while read l; do echo \"$l\"; done < f",
    "until false; do ls; done",
    '"if" x',
    'echo "if then else"',
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", KEYWORD_SHELLS)
def test_lead_and_judge_read_the_command_after_a_reserved_word(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", KEYWORD_SAFE)
def test_reserved_words_with_harmless_bodies_stay_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "if true; then git reset --hard; fi",
    "while true; do git push -f; done",
    "! git push -f",
    "for f in a; do git clean -fd; done",
    "case x in a) git push -f;; esac",
    "until false; do git branch -D b; done",
])
def test_every_agent_is_denied_an_irreversible_command_after_a_reserved_word(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_keep_the_old_reading_of_a_paren_after_a_reserved_word(agent, ws):
    assert_allow("if true; then (cd x); fi", agent, ws)
    assert_allow("bash -c x; if true; then ls; fi", agent, ws)


# --- env and NAME=value prefixes ----------------------------------------------------

ENV_IRREVERSIBLE = [
    "env git push -f",
    "FOO=1 git push -f",
    "env -i FOO=1 git push -f",
    "env -u NAME git push -f",
    "env -ux git push -f",
    "env -C /tmp git reset --hard",
    "env --chdir=/tmp git reset --hard",
    "env --unset=FOO git push -f",
    "env -0 git push -f",
    "env - git push -f",
    "env -S 'git push -f'",
    'env -S"git push -f"',
    "env --split-string='git push -f'",
    "env -S 'FOO=1 git reset --hard'",
    "FOO=1 BAR=2 git reset --hard",
    'FOO="a b" git push -f',
    "FOO=$(date) git push -f",
    "rtk env git push -f",
    "env rtk git push -f",
    "\\env git push -f",
    '"env" git push -f',
    "env FOO=1 rm -rf /etc",
    "FOO=1 \\git push -f",
]


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", ENV_IRREVERSIBLE)
def test_every_agent_is_denied_an_irreversible_command_behind_env_or_assignments(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", [
    "env -i git status",
    "env FOO=bar BAZ=qux ls",
    "env -u HOME ls",
    "env -S 'git status'",
    "env",
    "FOO=1",
    "FOO=1 BAR=2 ls",
])
def test_fast_and_smart_are_unchanged_for_env_and_assignments_in_front_of_harmless_commands(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["env FOO=bar BAZ=qux ls", "env", "FOO=1", "FOO=1 BAR=2 ls", "env FOO=1 git log"])
def test_lead_and_judge_allow_env_assignments_in_front_of_a_read_only_command(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["env -i git status", "env -S 'git status'", "env -- ls", "env -u HOME ls"])
def test_lead_and_judge_are_denied_every_env_flag(agent, command, ws):
    assert_deny(command, agent, ws)


# --- wrappers in front of an irreversible command ------------------------------------
# nice, timeout, time, command, exec, nohup and stdbuf (with their options and values), env,
# NAME=value and rtk are peeled for every agent before the irreversible-command checks.
# For fast and smart that adds no other refusal: only the irreversible rule firing.

WRAPPED_IRREVERSIBLE = [
    "nice git push -f",
    "nice -n 5 git push -f",
    "nice -5 git push -f",
    "nice --adjustment=5 git push -f",
    "timeout 5 git push -f",
    "timeout -s KILL 5 git push -f",
    "timeout -k 3 -s TERM 10 git reset --hard",
    "timeout --signal=KILL 5 git reset --hard",
    "time git push -f",
    "time -p git push -f",
    "command git push -f",
    "command -p git push -f",
    "exec git push -f",
    "nohup git branch -D b",
    "stdbuf -oL git clean -fd",
    "stdbuf -o L git clean -fd",
    "stdbuf -i0 -oL -eL git push --force",
    "nice env git push -f",
    "env nice git push -f",
    "nohup rtk git reset --hard",
    "rtk nice git push -f",
    "FOO=1 nice timeout 5 env -i rtk git push -f",
    "nice -n 5 timeout -s KILL 5 stdbuf -oL git push -f",
    "\\nice git push -f",
    '"timeout" 5 git push -f',
]


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [c for c in WRAPPED_IRREVERSIBLE if "env -i" not in c])
def test_every_agent_is_denied_an_irreversible_command_behind_wrappers(agent, command, ws):
    assert_deny(command, agent, ws)


def test_the_env_flag_form_is_denied_for_every_agent(ws):
    for agent in (FAST, SMART, LEAD, JUDGE):
        assert_deny("FOO=1 nice timeout 5 env -i rtk git push -f", agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", [
    "timeout 5 git status",
    "nice -n 5 ls",
    "nice ls",
    "time -p ls",
    "command -v git",
    "nohup ls",
    "stdbuf -oL cat f",
    "exec ls",
    "timeout -s KILL 5 git log",
    "nice -x ls",
    "timeout --foo 5 ls",
    "stdbuf -x ls",
    "nice -n",
    "timeout -s",
    "timeout",
    "timeout 5",
    "nohup",
    "exec -a",
])
def test_fast_and_smart_wrapper_forms_the_guard_does_not_know_add_no_refusal(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "nice rtk proxy bash x",
    "timeout 5 rtk proxy bash x",
    "nohup rtk bash x",
    "nice env FOO=1 python3 -c 1",
])
def test_lead_and_judge_classify_the_command_behind_wrappers_and_rtk(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["timeout 5 git status", "nice -n 5 ls", "nice git log"])
def test_lead_and_judge_still_allow_read_only_commands_behind_wrappers(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["nice --adjustment=5 ls", "exec -a x ls", "timeout --foo 5 ls", "nice -x ls", "timeout -s"])
def test_lead_and_judge_keep_their_wrapper_flag_refusals(agent, command, ws):
    assert_deny(command, agent, ws)


# --- release-review findings: constructs the walk must still read -----------------

# a for/select/case header segment is not a command, but the body after `do` or after a
# pattern's `)` is, with or without a space and with or without a `(` before the pattern
BODY_WRITES = [
    "for x do echo hi >f; done",
    "select x do echo hi >f; done",
    "case x in (*) echo hi >f;; esac",
    "case x in *)echo hi>f;; esac",
    "case x in a) echo hi >f;; esac",
    "case x in\n  a) ls ;;\n  b) echo hi >f ;;\nesac",
]
BODY_SHELLS = [
    "for x do bash -c y; done",
    "case x in (*) bash -c y;; esac",
    "case x in *)bash -c y;; esac",
    "case x in a|b) bash -c y;; esac",
    "case $x in a) echo $(bash y);; esac",
    "case x in\n  a) ls ;;\n\n  b) bash x ;;\nesac",
]
BODY_IRREVERSIBLE = [
    "for x do git push -f; done",
    "select x do git push -f; done",
    "case x in (*) git push -f;; esac",
    "case x in *)git push -f;; esac",
    "case x in a|b) git push -f;; esac",
    "case x in\n  a) ls ;;\n  (b) git push -f ;;\nesac",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", BODY_WRITES + BODY_SHELLS)
def test_lead_and_judge_check_the_body_of_a_for_or_case(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", BODY_IRREVERSIBLE)
def test_every_agent_is_denied_an_irreversible_command_in_the_body_of_a_for_or_case(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_may_still_write_and_run_shells_in_a_loop_body(agent, ws):
    assert_allow("for x do echo hi >f; done", agent, ws)
    assert_allow("case x in (*) bash -c y;; esac", agent, ws)
    assert_allow("case x in a) (cd x);; esac", agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_a_subshell_in_a_case_body_is_not_taken_for_a_pattern(agent, ws):
    assert_deny("case x in a) (bash);; esac", agent, ws)
    assert_deny("case x in\n  a) ls\n(bash)\n  ;;\nesac", agent, ws)


# rtk subcommands that run the rest as a command, and `run`, which runs a string with sh -c
@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "rtk run 'echo hi > f'",
    'rtk run "echo hi > f"',
    "rtk run 'ls; bash x'",
    "rtk run bash x",
    "rtk err bash -c x",
    "rtk test bash x",
    "rtk summary python3 -c 1",
    "rtk err touch f",
    "rtk -v run ls",
    "nice rtk run 'bash x'",
])
def test_lead_and_judge_classify_what_an_rtk_subcommand_runs(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "rtk test git push -f",
    "rtk summary git push -f",
    "rtk err git reset --hard",
    "rtk run 'git push -f'",
    "rtk run git push -f",
    'rtk run "git reset --hard"',
    "rtk -v run 'git push -f'",
    "rtk -v err git push -f",
    "rtk run 'ls && git push -f'",
])
def test_every_agent_is_denied_an_irreversible_command_an_rtk_subcommand_runs(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", ["rtk test pytest", "rtk err ls", "rtk summary git status", "rtk git status", "rtk proxy git log"])
def test_an_rtk_subcommand_running_a_harmless_command_stays_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


# `''#` is two quotes and a `#` inside a word, not a comment
@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_lead_and_judge_see_a_substitution_after_empty_quotes_and_a_hash(agent, ws):
    assert_deny("echo ''#$(bash -c x)", agent, ws)
    assert_deny('echo ""#$(bash -c x)', agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
def test_every_agent_sees_an_irreversible_substitution_after_empty_quotes_and_a_hash(agent, ws):
    assert_deny("echo ''#$(git push -f)", agent, ws)
    assert_deny("echo '#' $(git push -f)", agent, ws)
    assert_allow("echo a '' #$(git push -f)", agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    'f ( ) { bash -c "$X"; }; f',
    'f( ) { bash -c "$X"; }; f',
    "f\t(\t)\t{ ls; }",
    "function f ( ) { ls; }",
])
def test_lead_and_judge_deny_a_function_definition_with_spaced_parens(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_a_body_line_ending_in_a_backslash_joins_the_next_line(agent, ws):
    assert_deny("cat <<EOF\n$\\\n(bash -c x)\nEOF", agent, ws)
    assert_deny("cat <<EOF\nabc $\\\n(touch f)\nEOF", agent, ws)
    assert_deny("cat <<EOF\n`\\\ntouch f`\nEOF", agent, ws)
    assert_allow("cat <<EOF\n$\\\\\n(not a substitution)\nEOF", agent, ws)
    assert_allow("cat <<'EOF'\n$\\\n(bash -c x)\nEOF", agent, ws)


# inside $(( )) a single quote is an ordinary character, so a substitution after it runs
@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
def test_every_agent_sees_an_irreversible_substitution_inside_arithmetic_quotes(agent, ws):
    assert_deny("echo $(( '$(git push -f)' ))", agent, ws)
    assert_deny("echo $(( 1 + '$(git push -f)' ))", agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_lead_and_judge_see_a_shell_inside_arithmetic_quotes(agent, ws):
    assert_deny("echo $(( '$(bash -c x)' ))", agent, ws)


# $'...' is ANSI-C quoting: a backslash escapes, so `$'\''` is one quote character
@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
def test_every_agent_reads_past_an_ansi_c_quoted_quote(agent, ws):
    assert_deny("echo $'\\'' $(git push -f) $'\\''", agent, ws)
    assert_deny("echo $'a\\'b' $(git push -f)", agent, ws)
    assert_deny("echo $'\\\\' $(git push -f)", agent, ws)
    assert_deny("x=$(echo $'\\'' $(git push -f))", agent, ws)
    assert_deny("echo \"$(echo $'\\'' $(git push -f))\"", agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_lead_and_judge_see_a_shell_after_an_ansi_c_quoted_quote(agent, ws):
    assert_deny("echo $'\\'' $(bash -c x) $'\\''", agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_ansi_c_quotes_that_hide_a_substitution_keep_it_hidden(agent, ws):
    assert_allow("echo $'$(git push -f)'", agent, ws)
    assert_allow("echo $'a\\'$(git push -f)'", agent, ws)
    assert_allow("echo $'x' $(git status)", agent, ws)


# a paren group after a prefix keeps its old reading for fast and smart
@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", ["time (cd /tmp && ls)", "time { make; }", "nice (ls)", "FOO=1 (ls)", "env (ls)", "timeout 5 (ls)"])
def test_fast_and_smart_are_not_refused_a_paren_group_after_a_prefix(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["time (cd /tmp && ls)", "time { make; }", "nice (ls)"])
def test_lead_and_judge_are_refused_a_paren_group_after_a_prefix(agent, command, ws):
    assert_deny(command, agent, ws)


# --- ANSI-C quoted command words, clustered env flags, quoted arguments ------------

@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "$'git' push -f",
    "$'\\x67it' push -f",
    "$'g'it push -f",
    "$'git' reset --hard",
    "$'rm' -rf /etc",
    "FOO=1 $'git' push -f",
    "env $'git' push -f",
])
def test_every_agent_reads_an_ansi_c_quoted_command_word(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["$'bash' x", "$'\\x62ash' x", "$'python3' -c 1", "$'git' tag v1", "$'$G' x"])
def test_lead_and_judge_read_an_ansi_c_quoted_command_word(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_an_ansi_c_quoted_word_that_is_harmless_stays_allowed(agent, ws):
    assert_allow("$'git' status", agent, ws)
    assert_allow("echo $'it\\'s'", agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", [
    "env -iS 'git push -f'",
    "env -iS'git push -f'",
    "env -Sgit\\ push\\ -f",
    "env -i -S 'git push -f'",
    "env -0iS 'git reset --hard'",
    "env -iu NAME git push -f",
    "env -iC /tmp git push -f",
    "env -S 'env -iS \"git push -f\"'",
])
def test_fast_and_smart_read_the_string_of_a_clustered_env_flag(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", ["env -iS 'git status'", "env -0iu NAME git status", "env -iu NAME ls"])
def test_fast_and_smart_clustered_env_flags_in_front_of_harmless_commands_stay_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", ["env -iS 'git status'", "env -iu NAME ls", "env -0 ls"])
def test_lead_and_judge_are_denied_a_clustered_env_flag(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    'git push "-f"',
    "git push '--force'",
    'git push "--force-with-lease=x"',
    "git push 'origin' '+main'",
    'git worktree "remove" x',
    'git worktree "prune"',
    'git reset "--hard"',
    'git clean "-fd"',
    'git clean "-f" "-d"',
    'git branch "-D" b',
    'git checkout "."',
    'git checkout "--" "."',
    'git restore "."',
    'git "push" "--force"',
    'git -C x push "-f"',
    'git push \\-f',
    'rm "-rf" /etc',
    'rm "-r" "/etc"',
    'find . "-delete"',
    'npm "publish"',
    'git merge "x"',
])
def test_every_agent_unquotes_every_word_before_the_irreversible_checks(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", ['git status "-s"', 'git log "--oneline"', 'git push "origin"', 'git clean "-n"', "git push origin 'main'"])
def test_quoted_words_that_are_harmless_stay_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_keep_recursive_delete_inside_temp_with_quoted_flags(agent, ws):
    assert_allow('rm "-rf" /tmp/x', agent, ws)
    assert_allow('rm -rf "/tmp/a b"', agent, ws)


# --- what lead and judge refuse because the guard cannot read it with certainty ---------

UNREADABLE = [
    # case, select, coproc in command position
    "case x in a) ls;; esac",
    "case $x in a) echo y;; esac",
    "case x in (*) ls;; esac",
    "select x in a b; do ls; done",
    "coproc ls",
    "FOO=1 coproc ls",
    "time case x in a) ls;; esac",
    "ls && case x in a) ls;; esac",
    "echo $(case x in a) ls;; esac)",
    'echo "$(case x in a) echo y;; esac)"',
    # $'...' and $"..." quoting, outside quotes
    "echo $'x'",
    'echo $"x"',
    "echo a$'\\n'b",
    "ls $'a'",
    "echo \"$(echo $'x')\"",
    # a # inside $(( )) or (( ))
    "echo $(( 1 #$(cat >f) ))",
    "echo $((16#ff))",
    "echo $(( 1 + 2 # c ))",
    "((1 #$(cat >f)))",
    "for ((i=0;i<3;i++)); do echo $i; done",
    # unquoted brace expansion
    "echo {a,b}",
    "echo {1..3}",
    "cat file{1,2}",
    "ls /tmp/{x,y}/z",
    "echo a{b,{c,d}}",
    "for f in {a,b}; do echo $f; done",
    # a glob character in the command word
    "/bin/ba*h x",
    "/bin/ba?h x",
    "/bin/[b]ash x",
    "/usr/bin/g*t status",
    "FOO=1 /bin/ba*h x",
    # rtk run, in any form
    "rtk run ls",
    "rtk run 'ls'",
    "rtk run",
    "rtk run -c 'ls'",
    "nice rtk run ls",
    # a git alias set on the command line
    "git -c alias.x=!bash x",
    "git -c ALIAS.x=!bash x",
    "git -c 'alias.x=!bash' x",
    "git --config-env=alias.x=V x",
    "git --config-env alias.x=V x",
    "git -C /repo -c alias.l=log l",
    # zsh precommand modifiers
    "noglob ls",
    "nocorrect ls",
    "builtin cd /tmp",
    "FOO=1 noglob ls",
    "nice noglob ls",
]
STILL_ALLOWED = [
    "git diff $(git merge-base main HEAD)",
    "for f in a b; do echo $f; done",
    "rtk git status",
    "rtk proxy git log",
    "git -C /repo log",
    "git -c core.pager=cat log",
    "git --config-env=core.pager=P log",
    "ls | grep a | wc -l",
    "echo 'a b' \"c d\"",
    "echo \"cost $\"",
    'grep -E "^a$" f',
    "echo 'a$'",
    "echo '$'\"x\"",
    "echo '{a,b}' \"{1..3}\"",
    "echo ${x:-a,b}",
    "find . -name x -exec ls {} \\;",
    "git show stash@{0}",
    "[ -f x ] && ls",
    "[[ -f x ]] && ls",
    "if [ -f x ]; then ls; fi",
    "ls *.sh",
    "echo $((1+2))",
    "echo $(( (1+2)*3 ))",
    "cat <<'EOF'\n$'x' {a,b} case\nEOF",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", UNREADABLE)
def test_lead_and_judge_refuse_what_the_guard_cannot_read_with_certainty(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [c for c in UNREADABLE if not c.startswith("((")])
def test_the_unreadable_refusals_tell_lead_and_judge_to_rewrite_and_retry(agent, command, ws):
    # these are shape refusals: rewrite and retry, never STOP (a few are also refused by an older
    # rule that does say STOP, e.g. a redirect in the same command)
    proc = run_guard(command, agent, ws)
    out = json.loads(proc.stdout)["hookSpecificOutput"]
    if "cannot read with certainty" in out["permissionDecisionReason"]:
        assert "not a ban" in out["additionalContext"]
        assert "STOP" not in out["additionalContext"]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", STILL_ALLOWED)
def test_lead_and_judge_still_allow_what_is_readable(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", [
    "case $x in a) echo y;; esac",
    "case x in a) ls;; esac",
    "time (cd /tmp && ls)",
    "echo $'x' $'a\\'b'",
    "echo {a,b} {1..3}",
    "echo $(( 16#ff ))",
    "rtk run ls",
    "git -c alias.x=log x",
    "noglob ls",
    "/bin/ba*h x",
    "select x in a b; do ls; done",
])
def test_fast_and_smart_are_not_refused_what_only_lead_and_judge_cannot_read(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "case x in y) ;; (x) (git push -f);; esac",
    "case x in y) ;; (x) { git push -f; };; esac",
])
def test_a_case_pattern_dropped_after_a_double_semicolon_does_not_switch_the_shape_check_off(agent, command, ws):
    assert_deny(command, agent, ws)


def test_fast_and_smart_shape_refusal_after_a_case_pattern_says_rewrite(ws):
    for agent in (FAST, SMART):
        ctx = _deny_context("case x in y) ;; (x) (git push -f);; esac", agent, ws)
        assert "Rewrite it as simpler, separate commands" in ctx


# --- git config: lead and judge may read settings, never change them -----------------

CONFIG_WRITES = [
    "git config alias.x '!touch f'",
    "git config core.hooksPath /tmp/h",
    "git config --global user.name x",
    "git config --local core.editor vim",
    "git config --system a.b c",
    "git config --add remote.origin.fetch x",
    "git config --unset user.name",
    "git config --unset-all user.name",
    "git config --replace-all a.b c",
    "git config --rename-section a b",
    "git config --remove-section a",
    "git config -e",
    "git config --edit",
    "git config --global -e",
    "git config --file x.cfg a.b c",
    "git config -f x.cfg a.b c",
    "git config --file=x.cfg a.b c",
    "git config --type=bool a.b true",
    "git config set a.b c",
    "git config unset a.b",
    "git config edit",
    "git config rename-section a b",
    "git config remove-section a",
    "git config --global set a.b c",
    "git config --foo a.b",
    "git config -x a.b",
    "git config --comment x a.b c",
    "git -C /repo config core.hooksPath /tmp/h",
    "git --no-pager config a.b c",
    "git -c core.pager=cat config a.b c",
    'git "config" "a.b" "c"',
    'git config "--add" a.b c',
    "git config alias.x '!touch f' ; ls",
    "echo $(git config a.b c)",
]
CONFIG_READS = [
    "git config",
    "git config user.name",
    "git config --get core.editor",
    "git config --get-all remote.origin.fetch",
    "git config --get-regexp 'remote\\..*'",
    "git config --list",
    "git config -l",
    "git config --global --get user.name",
    "git config --global user.name",
    "git config --local --list --show-origin",
    "git config --list --name-only",
    "git config --list -z",
    "git config --show-scope --list",
    "git config --file x.cfg --get a.b",
    "git config -f x.cfg --list",
    "git config --file x.cfg a.b",
    "git config --file=x.cfg --list",
    "git config get user.name",
    "git config list",
    "git config list --global --show-origin",
    "git config get --all remote.origin.fetch",
    "git config --type=bool --get a.b",
    "git config --bool a.b",
    "git config --get --default x a.b",
    "git config --get a.b c",
    "git -C /repo config --get core.editor",
    "git -c core.pager=cat config --list",
    "git --no-pager config --list",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", CONFIG_WRITES)
def test_lead_and_judge_deny_a_git_config_that_changes_settings(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", CONFIG_READS)
def test_lead_and_judge_allow_a_git_config_that_only_reads(agent, command, ws):
    assert_allow(command, agent, ws)
    assert run_guard(command, agent, ws).stdout == ""


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
def test_the_git_config_denial_says_stop_and_names_the_read_forms(agent, ws):
    ctx = _deny_context("git config alias.x '!touch f'", agent, ws)
    assert "STOP and return blocked" in ctx
    assert "not a ban" not in ctx
    reason = json.loads(run_guard("git config core.hooksPath /tmp/h", agent, ws).stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "--get" in reason and "--list/-l" in reason


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", CONFIG_WRITES[:-1] + CONFIG_READS)
def test_fast_and_smart_are_unchanged_for_git_config(agent, command, ws):
    # echo $(git config a.b c) and the like are allowed too: only the irreversible rules apply
    assert_allow(command, agent, ws)


# --- a # inside ${...} or $[...] is not a comment ---------------------------------------

@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "echo ${x:-a #$(bash -c y)}",
    "echo ${x:-a #$(cat >f)}",
    "echo $[ 1 #$(bash -c y) ]",
    "echo ${x:-{a} #$(bash -c y)}",
    'echo ${x:-"}" #$(bash -c y)}',
    'echo ${y:-"${x}" #$(bash -c y)}',
    'echo "${x:-a #$(bash -c y)}"',
])
def test_lead_and_judge_see_a_substitution_after_a_hash_inside_a_parameter_expansion(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "echo ${x:-a #$(git push -f)}",
    "echo $[ 1 #$(git push -f) ]",
    "echo ${x:-{a} #$(git reset --hard)}",
])
def test_every_agent_sees_an_irreversible_substitution_after_a_hash_inside_a_parameter_expansion(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "echo ${x#prefix}",
    "echo ${#x}",
    "echo ${x%%#*}",
    "echo ${x:-a # not a command}",
    "echo $[ 1 + 2 ]",
    "echo a # $(bash -c y)",
    "echo ${x:-a}  # $(bash -c y)",
    "echo ${x:-a}\n# $(bash -c y)",
])
def test_a_hash_that_starts_a_real_comment_or_is_part_of_an_expansion_stays_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


# --- a flag inside a substitution is still a flag: the line is also read as it was typed ----

FLAG_IN_SUBSTITUTION = [
    "rm -f $(echo -r) /etc",
    "rm -f `echo -r` /etc",
    "rm -f $(echo -R) /etc",
    "rm -f $(echo -fr) /etc",
    "rm $(echo -rf) /etc",
    "git push origin $(echo --force-with-lease)",
    "git push origin $(echo +main)",
    "git push --force-with-lease=$(echo x)",
    "git clean -f $(echo -d)",
    "git clean $(echo -fd)",
    "git branch $(echo -df) b",
    "git branch -D $(echo b)",
    "echo ok; rm -f $(echo -r) /etc",
]


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", FLAG_IN_SUBSTITUTION)
def test_every_agent_is_denied_a_dangerous_flag_typed_inside_a_substitution(agent, command, ws):
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
@pytest.mark.parametrize("command", [
    "git push origin main",
    "echo $(date)",
    "git log $(git merge-base main HEAD)..HEAD",
    "git diff $(git merge-base main HEAD)",
    "git push origin $(git rev-parse HEAD)",
    "git push origin $(echo main)",
])
def test_substitutions_without_a_dangerous_flag_stay_allowed(agent, command, ws):
    assert_allow(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
def test_fast_and_smart_keep_a_quoted_path_with_a_space(agent, ws):
    assert_allow('rm -rf "/tmp/a b"', agent, ws)


# --- main's 4.3.3 guard runs first: scripts/legacy/ ----------------------------------------

LEGACY = SCRIPTS / "legacy"
LEGACY_SHA256 = {
    "hooks/executor-guard.sh": "2fd66d92497b596681ccceb000a3ca23d48cb395f4334756d31e83c3926a5a60",
    "lib/agents.sh": "f9b2569eb3bea49bb162402ac7dba4a7dd442b506852b098a171a012cf3bf133",
    "lib/command-lists.sh": "03a249fa8fba4b84bb7ef89a36a9ecc604c683d971d366d3b7f257a9d891c08b",
    "lib/heredoc.sh": "4ec9e087a932888d94fcdb36867fe25087cef1bd5ea3b356038218b7fe51550b",
    "lib/hook-io.sh": "76f6de5f7084c794a5b8444d46ab96c693b934ae8831a206466158873edf66a3",
    "lib/messages.sh": "8e52705e9e645975a2362f356d0e36b8a2418f88e5f9fb58afa34dea306969f8",
    "lib/parse.sh": "3186fde98e788fee1a9b6fb4153be425f733483625aafd3009a2a1e16d30e5df",
    "lib/path-guard.sh": "cf430d96220893d972d8dce3d9f27ba164bb8a278e10487f54f5c8e3c0bcb4a9",
    "lib/rules-irreversible.sh": "c92b14cbc7b17a35ef37b06e97ce890037e7a89826843d07dec9c12a11ed65aa",
    "lib/rules-readonly.sh": "a3b2916fc5c45002494a3e21cbfe9ad2e8065e9f797eaeb9b5e7cbb980ede486",
}
LEGACY_BASE = "1dd7c7f"


def _legacy_files():
    return sorted(str(f.relative_to(LEGACY)) for f in LEGACY.rglob("*") if f.is_file())


def test_the_legacy_copy_holds_exactly_the_files_of_the_4_3_3_guard():
    assert _legacy_files() == sorted(LEGACY_SHA256)


@pytest.mark.parametrize("name", sorted(LEGACY_SHA256))
def test_every_legacy_file_is_byte_identical_to_main_at_1dd7c7f(name):
    import hashlib
    data = (LEGACY / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == LEGACY_SHA256[name]
    # and, where the history is available, to the file in git
    probe = subprocess.run(["git", "cat-file", "-e", LEGACY_BASE], cwd=str(REPO_ROOT), capture_output=True)
    if probe.returncode == 0:
        shown = subprocess.run(["git", "show", f"{LEGACY_BASE}:scripts/{name}"], cwd=str(REPO_ROOT), capture_output=True)
        assert shown.returncode == 0, shown.stderr
        assert shown.stdout == data


@pytest.mark.parametrize("name", sorted(LEGACY_SHA256))
def test_every_legacy_file_has_valid_bash_syntax(name):
    proc = subprocess.run(["bash", "-n", str(LEGACY / name)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


SEVEN = [
    (FAST, "echo $$'\\'; git push --force origin main; echo ''"),
    (SMART, "echo $$'\\'; rm -rf /etc; echo ''"),
    (FAST, 'rm -rf /tmp/x "-etc"'),
    (FAST, "echo $'\\' ; rm -rf /etc ; '"),
    (FAST, "rm -$'\\r' /etc"),
    (FAST, "rtk cat <<EOF\nrm -rf /etc\nEOF"),
    (JUDGE, "rtk cat <<EOF\nrm -rf /etc\nEOF"),
]


@pytest.mark.parametrize("agent,command", SEVEN)
def test_what_the_4_3_3_guard_refused_through_a_misread_quote_stays_refused(agent, command):
    # cwd is the repository: a relative path in the command is not under a temp directory
    assert_deny(command, agent, REPO_ROOT)


MISREADS = [
    "echo $((1>2))",
    "echo $(( a > b ))",
    "echo $((x >> 2))",
    "echo $(ls 2>&1)",
    "echo `ls 2>&1`",
    "cat <(ls 2>&1)",
    "echo $(ls 2>/dev/null)",
    "echo $(ls > /dev/null)",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", MISREADS)
def test_lead_and_judge_are_refused_a_redirect_inside_a_substitution_exactly_as_on_main(agent, command, ws):
    # the 4.3.3 guard misread these as file writes; it is kept as it was, so they stay refused
    assert_deny(command, agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", MISREADS)
def test_fast_and_smart_are_not_refused_a_redirect_inside_a_substitution(agent, command, ws):
    assert_allow(command, agent, ws)


def _copy_without_legacy_file(tmp_path, how):
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    target = scripts / "legacy" / "hooks" / "executor-guard.sh"
    if how == "missing":
        target.unlink()
    elif how == "syntax-error":
        target.write_text("this is ( not valid bash\nfi fi\n")
    else:  # a legacy hook that fails without a decision
        target.write_text("#!/usr/bin/env bash\nexit 7\n")
    return scripts


@pytest.mark.parametrize("how", ["missing", "syntax-error", "exits-nonzero"])
@pytest.mark.parametrize("agent", [FAST, SMART, LEAD, JUDGE])
def test_a_legacy_hook_that_fails_without_a_decision_denies_the_guarded_agent(how, agent, tmp_path, ws):
    scripts = _copy_without_legacy_file(tmp_path, how)
    payload = {"agent_type": agent, "tool_input": {"command": "ls"}, "cwd": str(ws)}
    proc = subprocess.run(["bash", str(scripts / "hooks" / "executor-guard.sh")], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)["hookSpecificOutput"]
    assert data["permissionDecision"] == "deny"
    assert "internal error" in data["permissionDecisionReason"]


@pytest.mark.parametrize("agent", ["executor-fast-read", "general-purpose", "researcher"])
def test_a_caller_the_guard_does_not_cover_is_allowed_even_when_the_legacy_hook_fails(agent, tmp_path, ws):
    scripts = _copy_without_legacy_file(tmp_path, "missing")
    payload = {"agent_type": agent, "tool_input": {"command": "git push -f"}, "cwd": str(ws)}
    proc = subprocess.run(["bash", str(scripts / "hooks" / "executor-guard.sh")], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=10)
    assert proc.stdout == ""


def test_a_deny_from_the_legacy_hook_is_passed_on_as_it_printed_it(ws, tmp_path):
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    deny = '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"legacy said no","additionalContext":"x"}}'
    (scripts / "legacy" / "hooks" / "executor-guard.sh").write_text(f"#!/usr/bin/env bash\ncat >/dev/null\nprintf '%s\\n' '{deny}'\n")
    payload = {"agent_type": FAST, "tool_input": {"command": "ls"}, "cwd": str(ws)}
    proc = subprocess.run(["bash", str(scripts / "hooks" / "executor-guard.sh")], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0
    assert proc.stdout.strip() == deny


def test_an_exit_2_from_the_legacy_hook_is_passed_on(ws, tmp_path):
    scripts = tmp_path / "scripts"
    shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
    (scripts / "legacy" / "hooks" / "executor-guard.sh").write_text("#!/usr/bin/env bash\ncat >/dev/null\necho blocked\nexit 2\n")
    payload = {"agent_type": LEAD, "tool_input": {"command": "ls"}, "cwd": str(ws)}
    proc = subprocess.run(["bash", str(scripts / "hooks" / "executor-guard.sh")], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    assert proc.stdout.strip() == "blocked"


# --- shell script syntax --------------------------------------------------

def test_guard_script_has_valid_bash_syntax():
    proc = subprocess.run(
        ["bash", "-n", str(GUARD)], capture_output=True, text=True, timeout=10
    )
    assert proc.returncode == 0, proc.stderr


# --- git message heredoc: editor forms keep the body checked ---------------
# `-e` makes git open the message in an editor, and a leading `VAR=val`
# (GIT_EDITOR=sh) or any wrapper before `git` can turn that editor into a
# shell, so the body is then commands. The skip needs `git` as the segment's
# first word and no `-e` / `--edit`.

@pytest.mark.parametrize("agent", ALL_AGENTS)
@pytest.mark.parametrize("header", [
    "GIT_EDITOR=sh git commit -e -F - <<'EOF'",
    "GIT_EDITOR=sh git commit -F - <<'EOF'",
    "env GIT_EDITOR=sh git commit -e -F - <<'EOF'",
    "nice git commit -F - <<'EOF'",
    "timeout 5 git commit -F - <<'EOF'",
    "command git commit -F - <<'EOF'",
    "exec git commit -F - <<'EOF'",
    "git commit -e -F - <<'EOF'",
    "git commit --edit -F - <<'EOF'",
    "git commit -qe -F - <<'EOF'",
    "git commit -F - -e <<'EOF'",
    "git tag -a v1 -e -F - <<'EOF'",
])
def test_git_message_heredoc_with_editor_or_prefix_keeps_the_body_checked(agent, header, ws):
    assert_deny(f"{header}\nsubject\n{PUSH}\nEOF", agent, ws)


# A quoted, escaped or variable spelling of `-e` / `--edit` hides the flag from
# the literal token text, and `export GIT_EDITOR=sh` earlier makes git run the
# message through sh. The skip needs every token to be a plain literal word, so
# any such spelling keeps the body checked.

@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("header", [
    "git commit \"-e\" -F - <<'EOF'",
    "git commit '-e' -F - <<'EOF'",
    "git commit \\-e -F - <<'EOF'",
    "git commit \"--edit\" -F - <<'EOF'",
    "git commit --\"edit\" -F - <<'EOF'",
    "git commit $E -F - <<'EOF'",
    "git commit -F - \"$@\" <<'EOF'",
    "git tag -a v1 \"-e\" -F - <<'EOF'",
    "git commit --e -F - <<'EOF'",
    "git commit --ed -F - <<'EOF'",
    "git commit -F - `echo -e` <<'EOF'",
    "git commit -F - --ed* <<'EOF'",
    "git commit -F - {-e,-q} <<'EOF'",
    "git commit -F - -q\"e\" <<'EOF'",
    "git commit -m 'x' -F - <<'EOF'",
])
def test_git_message_heredoc_with_a_non_literal_word_keeps_the_body_checked(agent, header, ws):
    assert_deny(f"{header}\nsubject\n{PUSH}\nEOF", agent, ws)


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("header", [
    "git commit --no-edit -F - <<'EOF'",
    "git commit -F - --no-verify <<'EOF'",
    "git commit --file=- --author=a@b.c <<'EOF'",
    "git commit -F - << EOF",
])
def test_git_message_heredoc_with_only_plain_words_is_still_skipped(agent, header, ws):
    assert_allow(f"{header}\n{GIT_BODY}", agent, ws)


# --- git tag: lead and judge may list and verify, not create or move -------

TAG_WRITE_FORMS = [
    "git tag v1",
    "git tag v1 HEAD",
    "git tag -a v1 -m x",
    "git tag -d v1",
    "git tag -f v1",
    "git tag --force v1",
    "git tag --delete v1",
    "git tag -s v1",
    "git tag -u key v1",
    "git tag --sort=-creatordate v1",
    "git tag -m x",
    "git tag --unknown-flag",
    "git tag -ln",
    "git tag -l -d v1",
]

TAG_READ_FORMS = [
    "git tag",
    "git tag -l",
    "git tag --list",
    "git tag -l 'v*'",
    "git tag --list 'v1.*'",
    "git tag -n",
    "git tag -n5",
    "git tag -n5 -l 'v*'",
    "git tag --contains HEAD",
    "git tag --contains",
    "git tag --points-at HEAD",
    "git tag --points-at=HEAD",
    "git tag --merged main",
    "git tag --no-merged main",
    "git tag --sort=-creatordate",
    "git tag --sort -creatordate",
    "git tag -l --sort=-creatordate 'v*'",
    "git tag -v v1",
    "git tag --verify v1",
]


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", TAG_WRITE_FORMS)
def test_lead_and_judge_deny_git_tag_write_forms(agent, command, ws):
    ctx = _deny_context(command, agent, ws)
    assert "STOP and return blocked" in ctx
    assert "not a ban" not in ctx


@pytest.mark.parametrize("agent", [LEAD, JUDGE])
@pytest.mark.parametrize("command", TAG_READ_FORMS)
def test_lead_and_judge_allow_git_tag_read_forms(agent, command, ws):
    assert_allow(command, agent, ws)
    assert run_guard(command, agent, ws).stdout == ""


@pytest.mark.parametrize("agent", [FAST, SMART])
@pytest.mark.parametrize("command", TAG_WRITE_FORMS + TAG_READ_FORMS)
def test_fast_and_smart_allow_every_git_tag_form(agent, command, ws):
    assert_allow(command, agent, ws)


def test_internal_error_backstop_reason_does_not_say_return_blocked(ws, tmp_path):
    scripts = copy_scripts_with_stub_path_guard(tmp_path)
    payload = {"agent_type": LEAD, "tool_input": {"command": INTERNAL_ERROR_COMMAND}, "cwd": str(ws)}
    proc = subprocess.run(
        ["bash", str(scripts / "hooks" / "executor-guard.sh")],
        input=json.dumps(payload), capture_output=True, text=True, timeout=10,
    )
    reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "return blocked" not in reason
    assert "retry" in reason
