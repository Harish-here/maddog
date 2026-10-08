# tests/

Model-driven tests for this repo. Design: `docs/testing/spec.md`.

## Set up once

    python3 -m venv tests/.venv
    tests/.venv/bin/pip install -r tests/requirements.txt

## Run

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case ci-flake
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --tier mid --pressure decision
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --tier low --case rename-add-item --case list-flags
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --ladder
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --fresh-main
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --jobs 3
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --tier mid --jobs 6 --skill-file .claude/reviews/advisor-mode.draft.md

By default each case runs 3 times on this working tree and 3 times on
`main`, once, at its own expected tier — no climbing. A case's expected
tier comes from its own `expected_tier`, else its file's `expected_tier`,
else the `pressure` mapping in `harness/runtimes/ladders.yaml`.

`--tier` overrides the tier for every selected case and still never climbs.
`--ladder` opts into the old behaviour: start at `low`, and climb to the
next tier whenever fewer than half of a case's branch runs pass, up to `max_tier` in
`ladders.yaml` (currently `mid`). `--ladder` and `--tier` cannot be used
together.

`main`'s runs are reused across invocations: once a case/tier has enough
valid `main` runs on disk, later runs skip calling the model for `main`
again and only run the branch. `--fresh-main` ignores and overwrites that
cache. Branch runs are never cached — they are the thing under test.

Every run against a real model costs tokens and money. Runs use your
existing Claude Code login unless `ANTHROPIC_API_KEY` is set, in which case
they bill that key. The report and `runs.jsonl` record each run's cost in
USD and its token usage, where the runtime reports them.

### `--jobs`: running cases in parallel

`--jobs N` (default 1) runs up to `N` cases at once, instead of one at a
time. Each case claims one job slot when it starts and keeps that same
slot for its whole life — every tier it needs, branch then main, its
runs one after another in the usual order — releasing the slot only
when it finishes. A refused (VOID) attempt is still replaced the same
way, and the ladder still climbs the same way; `runs.jsonl` and the
report stay in `handoff.yaml` order, no matter which case actually
finishes first.

Keeping a case in one slot also makes it cheap: each job slot `k`
reuses one fixed workdir path, `<system temp>/maddog-run-<k>/<fixture>`,
emptied and rebuilt before every run instead of a fresh random path
each time, and every fixture commit is stamped with the same fixed
date. Runtime sessions include the workdir path and git state in their
system prompt, so holding both constant across a case's own later runs
lets the runtime's own prompt cache actually hit, instead of missing on
the first differing byte every time. Slot folders are removed when the
run finishes, including on a stop signal (below).

### `--skill-file`: testing a draft skill

`--skill-file <path>` tests a draft of the skill without editing it;
agents and everything else come from this working tree. The branch runs
use the given file instead of the real skill, while main still runs from
the latest commit. All selected cases must have the same `skill`.

### Stopping a run

SIGINT (Ctrl-C) and SIGTERM both still remove the `main` baseline
worktree and every job slot folder before the process exits (with a
non-zero status) — the signal is turned into an ordinary exception so
the run's own cleanup code runs, the same as on any other error.

A run also sweeps `tests/`' own leftover temp folders at startup:
`maddog-run-*`, `maddog-test-*`, and `maddog-baseline-*` folders (and any
git worktree registered under one) are removed if the process that made
them isn't alive any more, or if they carry no ownership marker and are
over 24 hours old. A folder currently owned by a live process — its own
or a sibling run's — is always left alone.

Harness unit tests (no model):

    tests/.venv/bin/python -m pytest tests/harness -q

## Read a report

`tests/results/<time>/report.md` has one row per case per tier, with a
**Cost** column (branch / main, summed across that row's runs) and a total
cost line at the end. A `Main` cell reading `main (cached)` means those
runs came from a prior `main` run, not a fresh model call.

Without `--ladder`, the table has no **Lowest passing tier** or **Expected
tier** column, and a case whose branch failed fewer than half of its runs is
flagged `FAIL AT <tier>`.

With `--ladder`, the table adds those two columns:

- **Lowest passing tier** vs **Expected tier**: the flag `ABOVE EXPECTED`
  means you decide: edit the skill once and rerun all cases, or give the
  case an `expected_tier` with a `why`, in its own entry or at the top of
  its `handoff.yaml`. Never change a case's `pressure` after its first run.
- `NO PASSING TIER (tried up to mid)`: the case never passed at any tier up
  to `mid`; `high` was not tried. With `max_tier: high`, this flag means a
  real routing defect.

`VOID LIMIT` (either mode): commands kept being refused; the environment is
broken, not the skill.

Below the table, every failed or void run lists its events in order.

## Add a case

Add an entry to the folder's `handoff.yaml`: `id`, `prompt`, `expect` (one of
Fast-Read, Fast, Smart, Judge, Lead), `pressure` (`none`, `user`, or `decision`). Set
pressure before the first run. Optional: `expected_tier` plus `why`, only when
a report showed the case needs a higher tier and you accepted that — either
on the case itself, or once at the top of the file for every case that
doesn't set its own.

## Agent patterns (`tests/agents/`)

    tests/.venv/bin/python tests/run.py agents/executor-fast --runtime claude-code --patterns --jobs 3
    tests/.venv/bin/python tests/run.py agents/executor-fast-read --runtime claude-code --patterns --case R4

`--patterns` runs the folder's `patterns.yaml` in agent mode; without it the
folder's `handoff.yaml` runs in skill mode, as before. Each case runs the
agent's own file as the main session, to completion, in a copy of the
`fast-tier` fixture: the file's body is the system prompt, its `tools:` line
the tool set, its `effort:` line the effort. This is a main-session proxy for
a real dispatch, good for comparing this branch with `main`, not a replica of
a subagent (Claude Code adds its own wrapper text to those). No plugin loads,
so nothing from this repo's `hooks/` can fire: the cases measure the agent
text alone. The only hook is the harness's own fence: file tools may not write
outside the workdir and the shell may not reach out (curl, ssh, sudo, git
push); a hit voids and reruns the run. It is not a sandbox, because a shell
command can still write outside the workdir. The branch run reads the agent
file from this working tree, the `main` run from the `main` worktree. Both run
at the case's expected tier (`low`, Haiku), 3 runs each.

A run passes only if all four checks pass:

1. the text `PATTERNS:` is in the agent's own text before its first tool
   call, in any position and with any markup around it (the user-locked rule;
   `scripts/pattern-declare-guard.sh` applies the same one)
2. the line holding it names every pattern the case expects; naming more is fine, so
   declaring every pattern passes this check and checks 3 and 4 catch a wrong
   classification
3. the first tool call is the kind and target the case expects; this is strict,
   so an `ls` or a Glob before the grep fails it. Setup steps are not scored
   and are skipped when choosing the first call: a step that only changes
   directory or sets up the shell (`cd`, `pushd`, `popd`, `export X=1`, `X=1`,
   `set -e`, `unset X`). `cd /w && grep -rn x .` is scored as the grep; a lone
   `cd` followed by an edit still fails
4. the law check for that case: files changed or left alone (read from git
   after the session, committed edits included), the order of calls, the
   command run, and, for Fast-Read, the exact quotes and the `CONFIRMED` /
   `CONTRADICTED` / `NO EVIDENCE` label in its return

`main` has no declaration rule, so checks 1 and 2 fail there by design; compare
checks 3 and 4 between branch and `main`. The report adds a "Checks (branch /
main)" table, one row per case, and a failed run's reason names the check that
failed.

A shell call that chains steps (`a && b; c`) is recorded as one event per step,
in order (split on `&&`, `||`, `;` and newlines outside quotes; a pipeline stays
one step and counts as its head command), so the order checks score the order
of the steps, not of the calls; setup steps (above) are kept in the log but not
matched. The split is not a shell parser: it does not
look inside `$( )` or `( )`.

Not measured: whether Fast calls a failure a success (Goodhart, the F3 law),
and whether it diagnoses a bug it was told only to reproduce (F4); both would
need a model's words in a place the waiver does not reach. F6's order check
measures obeying the capture-first order its prompt dictates, not RECOVER's law
independently, and F2 does not measure "never improvise a recovery step". The
case loader rejects `return_quotes`, `return_lacks`, and `label` in any case
file that is not Fast-Read's.

Scoring a model's words is waived for exactly two things, by user waiver
2026-10-08: the `PATTERNS:` line (both agents), and Fast-Read's returned quotes
and verdict labels. There is no grading model. To add a case, copy an entry in
`patterns.yaml`, give it a known answer the fixture makes true, and add that
answer to `harness/tests/test_fast_tier_fixture.py`.

## Layout

- `harness/core/`: names no runtime. Cases, fixtures, baseline, runner, scoring, report.
- `harness/runtimes/`: the only place runtime details live. One adapter per runtime, plus `ladders.yaml`.
- `fixtures/`: practice repos, copied to a temp folder outside this repo per run (`todo-app` for skills, `fast-tier` for agents).
- `skills/`, `agents/`, `scripts/`: case files, mirroring the repo's own folders.
