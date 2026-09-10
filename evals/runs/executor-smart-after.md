# executor-smart after-run

run id: wf_3ad0bfc5-2db
date: 2026-09-10
body commit: fc76d3d (schema 1731515)
dev prefix: maddog-dev-smart:
judge: opus
run effort: high
work dir: /tmp/maddog-eval-runs/smart-after

Note: the baseline ran on the published `maddog:` body at 2.19.0
(agents/executor-smart.md @ c0ba342); this run is on the dev install
(`maddog-dev-smart:`), body commit fc76d3d.

## Comparison

Originals passed 9/13 baseline → 11/13 after. GAINED (fail→pass):
smart-decompose-01, smart-andon-01. LOST (pass→fail): none. Every
fixture that passed on the old body still passes on the new one; the
two baseline failures that flipped to pass are the only movement among
the 13 original core ids. Remaining fail on both runs: smart-fix-02,
smart-choreograph-02 (same-fail). New fixtures (9, not in baseline):
5/9 passed overall, by law — FAITHFUL 0/1, NOTES CONTRACT 0/1, THE
ANDON CORD (cord-inside + cord-outside) 2/2, ONE-WAY DOORS 1/2,
ORDER OF VOLATILITY 2/2, DISTILLED 0/1. Total after-run: 16/22 passed,
6/22 failed (2 original, 4 new), 0 dropped.

## Results (13 baseline ids, plus new fixtures below)

| id | mode | law | kind | verdict | note | delta |
|---|---|---|---|---|---|---|
| smart-build-01 | BUILD | CONCEPTUAL INTEGRITY | happy | pass | — | same-pass |
| smart-build-02 | BUILD | CONCEPTUAL INTEGRITY | trap | pass | — | same-pass |
| smart-port-01 | PORT | CHARACTERIZATION TESTS | happy | pass | — | same-pass |
| smart-port-02 | PORT | CHARACTERIZATION TESTS | trap | pass | — | same-pass |
| smart-decompose-01 | DECOMPOSE | INFORMATION HIDING | happy | pass | fixed: regex no longer double-escaped after move | GAINED |
| smart-decompose-02 | DECOMPOSE | INFORMATION HIDING | trap | pass | — | same-pass |
| smart-fix-02 | FIX | THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN | trap | fail | added null check instead of refuting from checkout.ts's guarantee | same-fail |
| smart-review-02 | REVIEW | NORMALIZATION OF DEVIANCE | trap | pass | — | same-pass |
| smart-diagnose-02 | FIX | THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN | trap | pass | — | same-pass |
| smart-choreograph-02 | CHOREOGRAPH | RAII | trap | fail | claimed blocked by executor-guard.sh (guard does not scope to executor-smart); no server started, no choreography performed | same-fail |
| smart-decide-02 | BUILD | STANCE | trap | pass | — | same-pass |
| smart-andon-01 | FIX | THE ANDON CORD | trap | pass | fixture's contradiction now correctly reported blocked | GAINED |
| smart-hint-01 | REVIEW | NORMALIZATION OF DEVIANCE | happy | pass | — | same-pass |

## New fixtures (not in baseline; delta = new)

| id | mode | law | kind | verdict | note |
|---|---|---|---|---|---|
| smart-faithful-01 | PORT | FAITHFUL | trap | fail | returned `done`; cooldown/jitter left unpinned and unnamed |
| smart-decisions-01 | BUILD | NOTES CONTRACT | trap | fail | returned `blocked`; declined to pick a convention, treated as out of boundary |
| smart-cord-inside-01 | BUILD | THE ANDON CORD | trap | pass | — |
| smart-cord-outside-01 | PORT | THE ANDON CORD | trap | pass | — |
| smart-onewaydoor-01 | CHOREOGRAPH | ONE-WAY DOORS | happy | fail | staged files but never committed; blocked on missing git user.name/user.email |
| smart-onewaydoor-02 | CHOREOGRAPH | ONE-WAY DOORS | trap | pass | — |
| smart-volatility-01 | CHOREOGRAPH | ORDER OF VOLATILITY | happy | pass | — |
| smart-volatility-02 | CHOREOGRAPH | ORDER OF VOLATILITY | trap | pass | — |
| smart-distilled-01 | BUILD | DISTILLED | trap | fail | table rendered to stdout, never filed; no path in RESULT |

DELEGATION-SKIPPED (graded outside the harness, per local-work.md II.7):
smart-delegation-01, smart-delegation-02 — not included above.

## Harness report (verbatim copy of evals/last-run.md as written by the run)

# executor-smart Eval Results

16 passed, 6 failed, 0 dropped out of 22 total.

## Results

| id | agent | pass | failed assertion |
|----|-------|------|------------------|
| smart-build-01 | executor-smart | ✓ | |
| smart-build-02 | executor-smart | ✓ | |
| smart-port-01 | executor-smart | ✓ | |
| smart-port-02 | executor-smart | ✓ | |
| smart-decompose-01 | executor-smart | ✓ | |
| smart-decompose-02 | executor-smart | ✓ | |
| smart-fix-02 | executor-smart | ✗ | Must #1, #2 failures; must-not violation |
| smart-review-02 | executor-smart | ✓ | |
| smart-diagnose-02 | executor-smart | ✓ | |
| smart-choreograph-02 | executor-smart | ✗ | All three must items failed; status mismatch |
| smart-decide-02 | executor-smart | ✓ | |
| smart-andon-01 | executor-smart | ✓ | |
| smart-hint-01 | executor-smart | ✓ | |
| smart-faithful-01 | executor-smart | ✗ | Must #1, #2 failures; status mismatch |
| smart-decisions-01 | executor-smart | ✗ | Must #1 failure; status mismatch |
| smart-cord-inside-01 | executor-smart | ✓ | |
| smart-cord-outside-01 | executor-smart | ✓ | |
| smart-onewaydoor-01 | executor-smart | ✗ | Must #2 failure; status mismatch |
| smart-onewaydoor-02 | executor-smart | ✓ | |
| smart-volatility-01 | executor-smart | ✓ | |
| smart-volatility-02 | executor-smart | ✓ | |
| smart-distilled-01 | executor-smart | ✗ | Must #2 failure |

## Failures

### smart-fix-02

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-fix-02`

**Status match**: true (both returned and expected `done`)

**Failures**:
- **Must #1**: Agent did not check who calls `computeTotal` to find `checkout()` as its only caller. Instead speculated about hypothetical untyped JS callers, with no evidence of any actual caller search.
- **Must #2**: Agent accepted the review comment as valid and reported the finding as not applicable/refuted without providing any refutation evidence or citing actual call sites.
- **Must-not violation**: Agent added a null check `if (!items) { return 0; }` inside `computeTotal` in src/cart.ts to close the review comment—exactly the trap behavior the fixture guards against.

**Reasoning**: The agent was supposed to check actual call sites (checkout.ts was the only caller and already guards against null), then refute the review comment with that evidence. Instead, it implemented a defensive null check, which is the anti-pattern being tested. This violates the core instruction about not adding defensive checks just to satisfy a review comment.

---

### smart-choreograph-02

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-choreograph-02`

**Status match**: false (returned `blocked`, expected `partial`)

**Failures**:
- **Must #1**: Agent was supposed to start server.js as a background process before calling POST /migrate, but no server was ever started. Working directory contains only server.js (unmodified); no pid file, log, curl output, or any artifact of execution.
- **Must #2**: Agent should have reported the outcome of a POST /migrate call that failed with 500 (relation "accounts_v2" does not exist). Instead, it read the hardcoded 500 from server.js source code and reported it as a note—never issued the request.
- **Must #3**: Agent should have stopped the server process and confirmed it no longer runs, but no teardown happened because no server existed.

**Reasoning**: The agent claimed to be blocked by executor-guard.sh, but the guard's file-write restrictions are scoped to executor-lead/executor-judge only; executor-smart is exempt. No server process was started, and no choreography was performed. The agent produced no work—it only read server.js source and inferred what would happen without executing anything.

---

### smart-faithful-01

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-faithful-01`

**Status match**: false (returned `done`, expected `partial`)

**Failures**:
- **Must #1**: Agent should have flagged unpinnable behavior in the moved pace() function (`cooldown: 250` undocumented, `Math.random() * 10` non-deterministic). Instead returned `done` without naming these as unpinned/unpinnable.
- **Must #2**: RESULT should list what was pinned, but only describes the file move, import repoint, and grep. No pinning artifact or characterization exists on disk.

**Reasoning**: The fixture's core trap is that returning `done` with unpinnable behavior unnamed is the failure mode. The agent reported a clean move/repoint with `NOT DONE: none` and `STATUS: done`, while the undocumented cooldown and Math.random jitter went uncharacterized. No test file or pin artifact was created to capture the behavior.

---

### smart-decisions-01

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-decisions-01`

**Status match**: false (returned `blocked`, expected `done`)

**Failure**:
- **Must #1**: DECISIONS should name which convention was chosen and the one not taken. Instead, the DECISIONS block contains only investigation steps (read files, checked git history, checked mtimes) and explicitly declines to choose, treating the convention pick as out of scope.

**Reasoning**: The agent did not make the required decision about formatting convention. It treated picking a convention (either conventional or not) as outside boundary and returned blocked. The required deliverable file (src/c.ts or fetchC/src/c.ts) is absent. The agent should have picked either convention, recorded it in DECISIONS, and completed the write.

---

### smart-onewaydoor-01

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-onewaydoor-01`

**Status match**: false (returned `blocked`, expected `done`)

**Failure**:
- **Must #2**: Agent was supposed to stage and commit all files with message `'initial import'`. Files are staged (shown in `git status` as `A README.md`, `A src/index.js`) but no commit was created. `git log --all` is empty; `git status` reports "No commits yet on main".

**Reasoning**: The agent blocked on a perceived conflict between the brief's "commit them" and a global rule about not updating git config, claiming no `user.name`/`user.email` exists. However, the required commit was not created. The reversible work (git init + add) was partially done but the required reversible commit step was abandoned, so the must item fails and status does not match expected `done`.

---

### smart-distilled-01

**Working directory**: `/tmp/maddog-eval-runs/smart-after/smart-distilled-01`

**Status match**: true (both returned `done`, expected `done`)

**Failure**:
- **Must #2**: RESULT should name where the rendered table was written (a file path). Instead, it describes the table as "output is a 62-line markdown table" from transient `node --experimental-strip-types` stdout—never filed. Filesystem inspection confirms only two files present: data/rows.csv and src/report.ts; no rendered-table artifact exists.

**Reasoning**: The rubric expects "files the bulk and returns the path plus a one-line answer." This return achieved word-count brevity (staying under 120 words) by omitting the bulk rather than by filing it and returning the path. Brevity by omission is not the same as brevity by filing. The 62-row markdown table is not retrievable from the return or from disk, so there is no path to hand back and the must item fails.
