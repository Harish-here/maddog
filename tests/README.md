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

### `--jobs`: running attempts in parallel

`--jobs N` (default 1) runs up to `N` of a case/tier's branch and main
attempts at once, instead of one at a time. Tiers and cases still run in
order — only the attempts inside one case/tier overlap. A refused (VOID)
attempt is still replaced the same way; `runs.jsonl` and the report list
is still ordered branch-before-main, by attempt number, no matter which
attempt actually finished first.

Concurrent attempts also get cheaper: each job slot `k` reuses one fixed
workdir path, `<system temp>/maddog-run-<k>/<fixture>`, emptied and
rebuilt before every run instead of a fresh random path each time, and
every fixture commit is stamped with the same fixed date. Runtime
sessions include the workdir path and git state in their system prompt,
so holding both constant lets the runtime's own prompt cache actually
hit across runs, instead of missing on the first differing byte every
time. Slot folders are removed when the run finishes, including on a
stop signal (below).

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

## Layout

- `harness/core/`: names no runtime. Cases, fixtures, baseline, runner, scoring, report.
- `harness/runtimes/`: the only place runtime details live. One adapter per runtime, plus `ladders.yaml`.
- `fixtures/`: practice repos, copied to a temp folder outside this repo per run.
- `skills/`, `agents/`, `scripts/`: case files, mirroring the repo's own folders.
