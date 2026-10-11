"""Regression tests for scripts/executor-guard.sh.

Invokes the real guard script (`bash scripts/executor-guard.sh`) with a
crafted PreToolUse JSON payload on stdin, exactly the shape the hook itself
receives (agent_type, tool_input.command, cwd). `cwd` always points at a
`tmp_path` workspace holding real files — some checks below no longer need
an existing file to deny (option B removed judge's path-aware allowlist),
but the workspace is kept so a command can reference a real path where one
is written into the command string.
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
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "executor-guard.sh").write_text(GUARD.read_text())
    (scripts / "path-guard-lib.sh").write_text(
        "normalize_path() { printf '/tmp'; }\nis_temp_path() { exit 7; }\n"
    )
    for agent in (LEAD, JUDGE):
        payload = {"agent_type": agent, "tool_input": {"command": "rm -r x"}, "cwd": str(ws)}
        proc = subprocess.run(
            ["bash", str(scripts / "executor-guard.sh")],
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
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "executor-guard.sh").write_text(GUARD.read_text())
    (scripts / "path-guard-lib.sh").write_text(
        "normalize_path() { printf '/tmp'; }\nis_temp_path() { exit 7; }\n"
    )
    payload = {"agent_type": LEAD, "tool_input": {"command": "rm -r x"}, "cwd": str(ws)}
    proc = subprocess.run(
        ["bash", str(scripts / "executor-guard.sh")],
        input=json.dumps(payload), capture_output=True, text=True, timeout=10,
    )
    reason = json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
    assert "return blocked" not in reason
    assert "retry" in reason
