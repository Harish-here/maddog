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
        payload = {"agent_type": agent, "tool_input": {"command": "rm -r x"}, "cwd": str(ws)}
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
    "echo \"$(case x in a) echo y;; esac)\"",
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
    "case x in a) ls;; esac",
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
    "env nice git push -f",
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
    payload = {"agent_type": LEAD, "tool_input": {"command": "rm -r x"}, "cwd": str(ws)}
    proc = subprocess.run(
        ["bash", str(scripts / "hooks" / "executor-guard.sh")],
        input=json.dumps(payload), capture_output=True, text=True, timeout=10,
    )
    reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "return blocked" not in reason
    assert "retry" in reason
