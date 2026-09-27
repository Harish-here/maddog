# tests/

Model-driven tests for this repo. Design: `docs/testing/spec.md`.

## Set up once

    python3 -m venv tests/.venv
    tests/.venv/bin/pip install -r tests/requirements.txt

## Run

    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code
    tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code --case ci-flake

Each case runs 3 times on this working tree and 3 times on `main`, starting at
the `low` tier. A case that fails at least 2 of 3 climbs to the next tier, up to `max_tier` in `harness/runtimes/ladders.yaml` (currently `mid`).
Every run calls a real model and costs tokens. Runs use your existing Claude
Code login unless `ANTHROPIC_API_KEY` is set, in which case they bill that key.

Harness unit tests (no model):

    tests/.venv/bin/python -m pytest tests/harness -q

## Read a report

`tests/results/<time>/report.md` has one row per case per tier:

- **Branch / Main**: passes out of valid runs on this working tree and on `main`.
- **Lowest passing tier** vs **Expected tier**: the flag `ABOVE EXPECTED` means
  you decide: edit the skill once and rerun all cases, or give the case an
  `expected_tier` with a `why` in its `handoff.yaml`. Never change a case's
  `pressure` after its first run.
- `NO PASSING TIER (tried up to mid)`: the case never passed at any tier up to `mid`; `high` was not tried. With `max_tier: high`, this flag means a real routing defect.
- `VOID LIMIT`: commands kept being refused; the environment is broken, not the skill.

Below the table, every failed or void run lists its events in order.

## Add a case

Add an entry to the folder's `handoff.yaml`: `id`, `prompt`, `expect` (one of
Fast-Read, Fast, Smart, Judge, Lead), `pressure` (`none`, `user`, or `decision`). Set
pressure before the first run. Optional: `expected_tier` plus `why`, only when
a report showed the case needs a higher tier and you accepted that.

## Layout

- `harness/core/`: names no runtime. Cases, fixtures, baseline, runner, scoring, report.
- `harness/runtimes/`: the only place runtime details live. One adapter per runtime, plus `ladders.yaml`.
- `fixtures/`: practice repos, copied to a temp folder outside this repo per run.
- `skills/`, `agents/`, `scripts/`: case files, mirroring the repo's own folders.
