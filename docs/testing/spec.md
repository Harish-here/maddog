# Model-driven test setup — design spec

This spec designs the first version of `tests/`, this repo's home for
testing. Every decision below is closed and approved. What is not yet
decided is listed under Open questions at the end.

The first thing `tests/` checks is advisor-mode's routing: given one task,
does the advisor hand the work to the right helper? A **helper** is one of
this repo's five executor roles — Fast-Read, Fast, Smart, Judge, or Lead
(see `docs/executor-family/constitution.md`). A **handoff** is the moment
the advisor's session calls one of these roles to take the task. The first
build covers only the happy path: five tasks where the right helper is
clear-cut.

## Trial before building

Before any of the design below is built, run a short throwaway trial to
confirm two things:

1. The Claude Agent SDK can load a plugin from a folder with no user
   settings loaded.
2. The adapter (defined under Harness-neutral architecture) can stop a
   session at the helper call, before the helper runs.

If either fails, revisit this design before building anything.

## Method: stop at the first handoff

Run a real advisor session, with the real skill, and give it one task.
Record every tool call the session makes. Stop the session the moment it
hands work to a helper — before the helper runs. Score only from the
recorded calls, never from the model's own stated reasoning, and never
with a second model grading the transcript.

Why: routing is one decision made at one moment. A test that instead asked
the model to state its decision ("which helper would you pick?") passed 23
of 24 recall questions on text where 12 applied scenarios still found 3
rules that did not fire (measured 2026-09-21) — stated intent does not
predict applied behavior. A full end-to-end run, letting the helper
actually finish the task, adds cost and failure modes that have nothing to
do with routing. Keep an end-to-end run as an occasional final check, but
it is outside this spec.

## Isolation

An earlier attempt, on 2026-09-26, was abandoned: running the advisor
through `claude -p` loaded the user's own settings and hooks, and
permission gating refused commands in about 60 of 170 runs. Those refusals
looked like wrong routing, but were really an isolation failure.

The fix: each test session loads only this plugin, from a folder, with no
user settings and no user hooks. It runs against a fresh copy of a fixture
repo (a small sample project used as the target of the task) in a
temporary folder **outside** this repo, so no repo `CLAUDE.md` loads into
the session under test.

Any run where a command is refused is **VOID**: it is never scored, and it
reruns.

## Scoring

| Result | Meaning |
|---|---|
| PASS | The first helper called is the expected role, **and** before that call there are no edits or file writes, and at most one non-skill tool call. Loading a skill and one short read are allowed — this follows the skill's own "Dispatch First" rule. |
| FAIL | The wrong helper is called, or the advisor did the work itself (an edit or a write) before handing off. |
| VOID | A command was refused. |

Each case runs 3 times. The runner rejects a request for fewer than 3
runs. The report shows passes out of runs (for example, 2/3). "Fails
repeatedly" means at least 2 of the 3 runs fail.

### Stopping early

A session ends as soon as its score can no longer become PASS: after a
write, after any handoff, or once a second read/command event arrives
before a handoff (at that point `score()` already returns FAIL, whatever
happens next). `settled(events)`, next to `score()` in `harness/core/`,
is the pure function that decides this; the adapter calls it once a tool
call's result has been observed, so a refusal on the very call that
settles the run is still recorded as VOID rather than missed. One
consequence: a refusal on any *later* call, after the run has already
settled, is never observed or recorded, because the session has already
ended.

## Baseline

Every result is reported next to the same cases run against `main` (a
plugin copy taken from a git worktree of `main`). This separates the
effect of an edit under test from ordinary run-to-run variance.

## Testing a draft skill

`--skill-file <path>` tests a skill draft without editing it: the branch
runs use the given file instead of the real skill, while main still runs
from the latest commit. All selected cases must have the same `skill`.

## Model ladder

Models are grouped into three **tiers** — low, mid, high — from weakest to
strongest. A case names only the tier it expects, never a model name.
Each runtime maps tiers to real models in its own config. For Claude Code,
that config is `tests/harness/runtimes/ladders.yaml`:

```yaml
# Tier → model for each runtime. Cases name only tiers.
claude-code:
  low:  claude-haiku-4-5-20251001
  mid:  claude-sonnet-5
  high: claude-opus-5-5
# Pressure kind → the tier a case is expected to pass at.
expected_tier:
  none: low
  user: mid
  decision: mid
# highest tier the runner climbs to; raise to high later
max_tier: mid
```

Every case declares a **pressure** kind when it is written, before any
run. `none`: the task is written to be easy to route correctly. `user`:
the user in the prompt pushes the model to act directly — urgency, "tiny
fix", "just confirm it". `decision`: the prompt's wording points to the
wrong hand — "audit", "tricky", "mechanical", "code review", "drop-in".
Both `user` and `decision` expect the `mid` tier. Each pressure case
tests one kind, so a failure names the kind that broke it. All five
happy-path cases are `pressure: none`.

A case's expected tier, used only for the report's `--ladder` columns,
comes from the first of: its own `expected_tier` (with a required
`why`), else the same pair set once at the top of its `handoff.yaml` (so
every case in the file inherits it unless it sets its own), else the
`pressure` mapping above.

## Escalation loop (opt-in)

By default the runner does not climb: each case runs once, at its own
expected tier, and the report shows only whether it passed there. This
keeps a routine run cheap — one model per case, not up to three.

`--ladder` opts into the climb: the script runs a case at the `low` tier
first, and if it fails repeatedly, climbs to `mid`, then `high`, to find
the lowest tier that passes. The report then shows this lowest passing
tier next to the case's expected tier (from the `expected_tier` mapping
above). For now the climb stops at `mid` (`max_tier` in `ladders.yaml`);
`high` is kept in the ladder for later. `--ladder` and `--tier` (which
pins every case to one named tier, also with no climbing) cannot be used
together.

If a `--ladder` run's lowest passing tier is above the expected tier, the
user decides between two options:

- Edit the skill **once**, then rerun **all** cases — not just the failing
  one, because an edit can break a case that used to pass, and the `main`
  baseline is what shows that.
- Raise the case's expected tier, and record why.

The one-edit limit exists so the skill does not grow without bound to
satisfy the weakest model: every real session pays the cost of reading
that skill text.

## Cost

Every run records the session's cost in USD and its token usage (input,
output, cache read, cache creation), taken from the runtime's own final
result message. The adapter is the only place that parses runtime-shaped
usage fields; core only ever sees these four plain numbers plus a cost
figure, alongside the event log. When the runtime cannot report cost or
usage, the run records `null` for it, never `0` — a real $0 run and an
unreported one must never look the same. The report shows a cost column
per row (branch and main summed separately) and a total for the whole
run; `runs.jsonl` carries the same fields per run.

## Reusing `main`'s runs

`main` never changes between runs of the same branch, so its results are
cached on disk under `tests/results/.main-cache/` (already covered by
`tests/results/` in `.gitignore`), keyed on `main`'s commit SHA, the
runtime, the model the tier maps to, the case's prompt and fixture, and a
hash of the adapter's source file — so a branch edit to the adapter, or a
new commit on `main`, invalidates the cache on its own. The cache stores
raw events per run, never a verdict: `score()` runs again on load, so a
scoring change never needs the cache invalidated. A cache hit with at
least the required number of valid runs skips calling the model for
`main` on that case and tier; the report marks those rows `main
(cached)`. `--fresh-main` ignores and overwrites the cache. Branch runs
are never cached — they are the thing under test, and must always run
fresh.

## Running cases in parallel

`--jobs N` (default 1) runs up to `N` cases at once instead of one at a
time. Each case claims one job slot the moment it starts and keeps it
for its whole life: every tier it needs, branch then main, its own
runs one after another, in the same order a `--jobs 1` run would use.
The slot is released only when the case finishes, freeing it for
whichever case is queued behind it. A VOID attempt is still replaced
the same way, `MAX_VOIDS` still ends the case, and the ladder still
climbs the same way. `runs.jsonl` and the report stay in
`handoff.yaml` order, regardless of which case actually finished first.

Pinning a case to one slot for its whole life is what makes concurrency
cheap: a session's system prompt includes its working directory and
git state, so a case whose later runs land in a fresh random workdir
with fresh commit hashes would defeat the runtime's cache from the
first differing byte on. Each job slot `k` (0..N-1) instead reuses one
fixed path, `<system temp>/maddog-run-<k>/<fixture>`, emptied and
rebuilt before each run; every fixture commit gets one fixed
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`, so identical content always
hashes to an identical commit. A case's later runs then reuse the
runtime's own prompt cache from its earlier ones. A slot is held with
an exclusive lock for the life of the process, so two `run.py`
processes never share one; a locked slot number is skipped in favor of
the next free one.

On SIGINT or SIGTERM, `run.py` still removes the `main` baseline
worktree and every slot folder before exiting non-zero — the signal is
turned into an ordinary exception so the existing cleanup code runs. At
startup, `run.py` also sweeps its own leftover `maddog-run-*`,
`maddog-test-*`, and `maddog-baseline-*` folders (and any git worktree
registered under one): a folder is removed only if the process that
made it is no longer alive, or it carries no ownership marker and is
over 24 hours old, so a live sibling run's folders are never touched.

## Harness-neutral architecture

Per `PHILOSOPHY.md` §5 (abstract responsibility and authority; adapt
mechanics): a neutral core names no AI runtime, and one **adapter** per
runtime holds every runtime-specific detail. Porting this setup to Codex
means writing one new adapter file — no change to cases, core, or reports.

- **Cases** name roles, tiers, `skill: advisor-mode`, and the task text.
  They never name agent IDs, model names, or slash-command syntax.
- **The core** works on an ordered event log. An **event** is one recorded
  step in a session. There are six kinds: `handoff` (which role), `write`,
  `read`, `command`, `skill_load`, `refused`.
- **The adapter interface** is `run(case, plugin_path, workdir, tier) →
  event log`. The adapter owns: invocation syntax (today,
  `/maddog:advisor-mode …`); mapping roles to agent IDs (for example,
  Fast-Read → `maddog:executor-fast-read`); mapping tiers to models;
  translating raw tool calls into events; isolation; stopping the session
  at the first `handoff` event; and one option to run a plain session with
  no skill loaded (used later by the agents tests, see Executor-family
  adoption).
- **The Claude Code adapter** uses the Claude Agent SDK (Python). Caveat:
  this event list was designed from Claude Code alone. The first Codex
  adapter may force changes to it.

## Layout

The top level of `tests/` mirrors the repo's own folders:

```text
tests/
├── README.md                how to run, add, and read tests
├── requirements.txt         claude-agent-sdk, pyyaml
├── run.py                   python tests/run.py skills/advisor-mode --runtime claude-code
├── harness/
│   ├── core/                names no runtime
│   │   ├── events.py
│   │   ├── fixture.py       copy to a temp dir outside the repo, git init, apply branch patch
│   │   ├── baseline.py      this branch vs main
│   │   ├── maincache.py     reuse main's run events across invocations
│   │   ├── score.py
│   │   └── report.py
│   └── runtimes/            the only place runtime identifiers appear
│       ├── ladders.yaml
│       └── claude_code.py
├── fixtures/todo-app/       small Python to-do CLI, tests, CHANGELOG
│   └── feature-export.patch the extra branch (git can't nest a repo)
├── skills/advisor-mode/handoff.yaml
├── agents/                  second build
├── scripts/                 later: plain shell checks, no model
└── results/                 git-ignored: <timestamp>/runs.jsonl + report.md
    └── .main-cache/         git-ignored: cached main-version run events
```

Test files are named for what they check — `handoff.yaml` checks the first
handoff. The harness is Python, matching the repo's existing
`scripts/*.py` checks. It runs in a plain virtual environment
(`python3 -m venv`, then `pip install -r tests/requirements.txt`), so no
extra tool is needed. There is no dashboard for now; revisit once the `agents/` cases
land, or when comparing a case's lowest passing tier across releases.
`runs.jsonl` keeps the underlying data for that.

## Happy-path cases

`tests/skills/advisor-mode/handoff.yaml` holds these five cases. All are
`pressure: none`, run against the `todo-app` fixture:

| # | Task | Expected role |
|---|---|---|
| 1 | "For each command the CLI offers, list its flags and the test that covers it." | Fast-Read |
| 2 | "Rename `add_item` to `create_item` everywhere, including tests. Change nothing else." | Fast |
| 3 | "The due-date parser rejects `2026-10-01T09:00`. Make it accept ISO date-times, keeping the existing tests passing." | Smart |
| 4 | "Branch `feature/export` is about to merge into main, which the team builds on. Get a verdict on whether it's ready." | Judge |
| 5 | "Tests pass locally but fail in CI on some runs. Find out why and get it fixed." | Lead |

Known weak spot: case 5 could reasonably route to Fast-Read first, to
gather facts before anyone fixes anything. If trials show that happening,
either tighten the task wording or accept Fast-Read as a second valid
answer.

## Rules live in code

The harness enforces isolation, VOID runs, the `main` baseline, and the
3-run minimum as defaults no case can switch off. There is no
`tests/CLAUDE.md`.

### Proposed doc edits

These are recorded here verbatim as **PROPOSED**. They need the user's
approval and are not applied by this spec:

- The adapter-set line in the root `CLAUDE.md` becomes: "- Adapter set —
  the only paths where runtime mechanics may live: agent and skill
  frontmatter, `hooks/`, `scripts/`, `workflows/`, `tests/`, `.github/`,
  `.claude/`, `.claude-plugin/`." Within `tests/`, only
  `tests/harness/runtimes/` names runtime identifiers.
- A new invariant in the root `CLAUDE.md`: "- Model-driven tests score
  from recorded tool calls, never a model's words or a grading model.
  `tests/harness/` enforces isolation, voided runs, and the main-branch
  baseline: change the harness, never bypass it."

Two more docs change in the same build: `CONTRIBUTING.md`'s "Validation —
there is no test suite" section (which currently prescribes paired manual
`claude -p` probes) gets replaced to point at `tests/`; and `README.md`'s
layout section gains `tests/`.

## Executor-family adoption (second build)

Each executor gets `tests/agents/executor-<name>/handoff.yaml`, with tasks
that agent should win in a plain session — no skill loaded, so only the
agents' descriptions guide Claude Code's choice. `run.py agents` runs
all five together, because the descriptions compete with each other for
the same tasks.

The same five task texts from the happy-path cases are copied into these
per-agent files. A task that passes one suite but fails the other shows
which text needs fixing: advisor-mode's Classify table, or the executor's
own description.

After this build lands, any edit to an executor description or to
advisor-mode's Classify table must run both case sets before release. That
rule gets written into `docs/executor-family/constitution.md` and into the
release skill's reviewer table, through the `author-agent` loop, in a
later change.

Out of scope: checking that a helper stays inside its limits while it
works. That is a future `boundary.yaml`, with its own spec.

## Decisions deferred

- A results dashboard.
- An automatic full end-to-end check.
- Wrapping `run.py` in a skill.
- Moving the harness to TypeScript, if maintaining Python becomes a burden
  (the maintainer works mainly in TypeScript).
- `boundary.yaml` (checking a helper stays inside its limits while working).

## Open questions

None. All thirteen source decisions are closed; nothing needed to build
the first version is missing.
