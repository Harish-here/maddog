# tests/

Model-driven tests for this repo. Design: `docs/testing/spec.md`.

## Set up once

    python3 -m venv tests/.venv
    tests/.venv/bin/pip install -r tests/requirements.txt

## Run

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case ci-flake-pressure
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

`--runs N` sets how many times each case runs on each side (default 3). `--pressure <name>` keeps only the cases tagged with that pressure.

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

    tests/.venv/bin/python -m pytest tests/harness tests/guard -q

These offline tests are cheap and always run in full. CI runs them as one
step of `.github/validate.sh` on every pull request (see "CI and the release
gate" below); model runs never run in CI.

### `--changed`: run only the model tests a change touches

    tests/.venv/bin/python tests/run.py --changed --runtime claude-code --dry-run
    tests/.venv/bin/python tests/run.py --changed --runtime claude-code
    tests/.venv/bin/python tests/run.py --changed origin/main --runtime claude-code

Each case file lists the repo files it tests in a top-level `covers:` list of
repo-relative globs (`*` stays within one folder, `**` crosses folders). A
file with no `covers:` covers nothing and is never selected:

    covers:
      - "skills/advisor-mode/**"
      - "agents/executor-*.md"

`--changed [BASE]` (BASE defaults to `main`) replaces the target. The changed
files are `git diff --name-only BASE...HEAD` plus uncommitted changes to
tracked files; changed files under `tests/` and `.claude/` select nothing. It
checks every `skills/*/handoff.yaml` (skill mode) and
`agents/*/patterns.yaml` (agent mode), and runs each one whose `covers:`
matches a changed file, one after another, in its own mode. Give a target or
`--changed`, not both. `--case`, `--patterns` and `--skill-file` do not mix
with `--changed`; `--tier`, `--pressure`, `--runs`, `--jobs` and the rest
apply to every selected file.

`--dry-run` (with `--changed`) prints the changed files, the selected case
files, and each one's case count and runs x sides, then exits without calling
a model. Nothing selected prints that and exits 0.

### `--changed --record`: record a release

    tests/.venv/bin/python tests/run.py --changed --record --runtime claude-code

The release run. It refuses unless local `main` equals `origin/main` (it runs
`git fetch origin` first; BASE is `main`, or `origin/main`, which is then the
same commit). Then, in order:

1. runs the offline tests (`pytest tests/harness tests/guard`); any failure stops it;
2. selects test files from the changed files. Only files outside `tests/` and
   `.claude/` select, so a tests-only or repo-internal change selects nothing.
   A test file's globs are its `covers:` in the base tree plus its `covers:` in
   this tree. Nothing selected prints "no covered changes", writes nothing and
   exits 0. A selected test file that this branch deleted stops the run;
3. refuses when something is selected but `.claude-plugin/plugin.json` still
   has main's version ("bump the version first"), and when a tracked covered
   file has uncommitted changes (the fingerprints are of committed content);
4. runs every selected file in full: every case, at its expected tier, `--runs`
   times (at least 3) on each side. `--case`, `--pressure`, `--tier`,
   `--ladder`, `--dry-run` and `--runs` below 3 are refused;
5. writes `tests/releases/<version>/`, replacing an earlier recording of the
   same version, and prints the attempt number (kept in the manifest as
   `attempt`, so re-recording until a lucky pass shows in review).

The pass rule per case: the branch passes at least `main`'s passes minus one (a
one-run gap is allowed). Agent-mode cases also need the branch to pass in at
least 2 of 3 runs (generally `ceil(2/3 * runs)`); skill-mode cases have no such
floor. A case fails whenever it hit the void limit or either side has fewer than
`--runs` valid runs. A test
file passes when all of its cases pass. The command exits 1 after writing a
recording that failed the rule; the gate rejects it.

`tests/releases/<version>/` holds, all committed:

- `manifest.json`: version, tested and base commits, changed files, attempt,
  runs, per test file its mode, results path (`tests/results/<time>/`), cases
  `{branch_pass, main_pass, valid_runs, void_limited, verdict}`, verdict and
  fingerprints, plus the offline summary line, total cost in USD and the time.
  No runtime or model name appears anywhere under `tests/releases/`.
- `offline.txt`: the pytest summary line.
- `<test-folder>.md` (for example `skills-advisor-mode.md`): that file's case
  table, with no runtime column.

A fingerprint is a sha256 of one file's content: every tracked file matched by
the test file's base-or-head `covers:` globs, and the test file itself. Raw
`runs.jsonl` and transcripts stay in the git-ignored `tests/results/`. Old
`tests/releases/*` folders stay in the repo.

### CI and the release gate

`tests/gate.py --base <ref>` is the offline half. It needs no model and takes
seconds:

    tests/.venv/bin/python tests/gate.py --base origin/main

It prints "no covered changes" and exits 0 when no changed file selects a test
file. Otherwise it fails when any of these holds: the version equals the
base's; `tests/releases/<version>/manifest.json` is missing, or its `version`
differs from the folder name; the manifest lacks a selected test file or any
case id in that file's current yaml; any verdict is fail; a selected test file
was deleted; a fingerprinted file is missing or its hash changed; or a file
now matched by the base-or-head `covers:` has no fingerprint.

`.github/validate.sh` holds every pull-request check and is the single thing
CI runs. It stops at the first failure, in this order: frontmatter, JSON and
version consistency; `scripts/fragment-check.py`; `bash -n` on `scripts/*.sh`;
every command path in `hooks/hooks.json` exists; `jq` is installed; the offline
tests; the gate (`--base ${BASE:-origin/main}`). Run it locally with the test
venv's python, from a clone that has a local `main`:

    PYTHON=tests/.venv/bin/python .github/validate.sh

`.github/workflows/validate.yml` has one job, `validate`, on `pull_request`
only: it fetches full history, creates local `main` from `origin/main`, sets up
Python 3.13 with a pip cache, installs `jq` if missing, then runs the script. A
newer push cancels the older run. The job name `validate` is what main requires,
so a release with covered changes and no passing recording cannot merge. For the
merge tree to equal the tested tree, main must also require branches to be up to
date before merging.

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
doesn't set its own. A new case file also needs a `covers:` list, or
`--changed` never selects it.

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
   directory or sets up the shell (`cd`, `pushd`, `popd`, `pwd`, `export X=1`, `X=1`,
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
- `releases/`: one folder per recorded version, written by `--record` and read by `gate.py`.
- `gate.py`: the offline release gate.
