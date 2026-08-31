# Plan: executor-fast-read — a read-only executor hand

STATUS: frozen, ready to execute (round 3 — cleared gate-01 and gate-02
findings; normalization work split out per owner decision, see decision
20). Decisions are CLOSED — do not redesign, do not re-litigate, do not
add alternatives. Only the OPEN QUESTIONS section is undecided.

**DEPENDENCY — this plan does not start until
`docs/plans/executor-guard-normalization.md` has merged to main.** That
plan fixes the confirmed path-normalization defect in
`scripts/executor-guard.sh` and extracts a sourceable
`scripts/path-guard-lib.sh` (`normalize_path`, `is_temp_path`). T4 and T5
below source that file; neither reimplements path logic. Confirm the
other plan's SEAL has posted before opening this plan's candidate branch.

## Why this exists

Two problems, one fix.

1. **Containment hole.** `executor-judge` (`agents/executor-judge.md`)
   holds the Agent tool and holds no Write/Edit. `scripts/judge-dispatch-guard.sh`
   restricts its dispatch targets to `executor-fast` and `researcher`. But
   `executor-fast` holds Write and Edit. So the judge can hand a fix to a
   permitted subordinate and patch the very work it is judging — the
   DELEGATION section of `executor-judge.md` (lines 96-120) polices this
   today by instruction alone ("RENT HANDS, NEVER VERDICTS"), and
   `judge-dispatch-guard.sh`'s own header (lines 5-9) admits the limit
   "lives only as a sentence in the agent's own description today."
   Removing the Agent tool from the judge was considered and **rejected**
   by the owner previously: a top-tier model should buy recon rather than
   grind greps. Do not re-propose it. The fix instead is to change what the
   judge is *allowed* to rent.
2. **Classification is inverted.** `executor-fast` runs on Haiku and
   carries ten modes (`agents/executor-fast.md` lines 46-124).
   `executor-smart` carries eight modes on Sonnet. `executor-judge` and
   `executor-lead` carry three modes each on Opus. The cheapest model does
   the most classification work — exactly the job a cheap model is worst
   at. Splitting `executor-fast`'s ten modes by an objective test (does the
   task write anything?) gives the read-only three (RECON, EXTRACT, VERIFY)
   their own hand, shrinks `executor-fast` to seven, and — as a side effect
   — gives the judge a rentable hand that is *structurally* incapable of
   producing the fix-leak in problem 1, closing both problems with one
   agent.

## Round 1 gate findings — disposition (cite by number, `docs/plans/gate-01-executor-fast-read.md`)

| # | Disposition | How |
|---|---|---|
| 1 | APPLIED (mechanism changed by owner, then split) | Reviewer's fix ("session-scope + resolve before match") is superseded by owner decision D-A: confinement is BROAD, not session-scoped. Reviewer's underlying technical demand — normalize before testing — is kept, but is now entirely owned by `docs/plans/executor-guard-normalization.md` (decision 20) after gate-02 found the original T4 spec unsound. This plan's T4/T5 depend on that plan's merge and source its output. |
| 2 | APPLIED | Owner decision D-B: T3 retargets all five named call sites; `product-qa` and `executor-lead` stay the only exemptions. Round 2 found two further stale routes; see gate-02 disposition NF5 below. |
| 3 | APPLIED | T8 (now T8, see round 2 table) widened from the DELEGATION section alone to also cover the frontmatter description and the DISPATCH note of `agents/executor-judge.md`. |
| 4 | APPLIED | Release sequence's READY bullet rewritten: neither manifest enumerates agents by name, so no "must appear in both" claim; the actual catch is the repo-wide by-name grep sweep, named explicitly. |
| 5 | APPLIED | T7's (renumbered) DONE-WHEN requires happy+trap pairs for the read hand's three standing laws. |
| 6 | APPLIED | T7 adds updating `.claude/workflows/agent-evals.js`'s `AGENTS` default, `RUN_MODEL` mapping, and the Load-phase prompt to include `executor-fast-read`. |
| 7 | APPLIED | T7's DONE-WHEN requires each migrated fixture carry its prior id as a breadcrumb; round 2 found no schema slot for it — see gate-02 NF6 below. |
| 8 | APPLIED | T1's content spec names the *capability*, drops the literal tool name and hook mechanics from the shipped body, per `CLAUDE.md` §Invariants. |
| 9 | APPLIED | Baseline corrected: DELEGATION is `agents/executor-judge.md:96-120`, 25 lines. |
| 10 | APPLIED | T5 (renumbered) rewrites the denial strings at `executor-guard.sh:420,425,428`. |
| 11 | RESOLVED, closed — no work planned | Confirmed via Claude Code documentation: `agent_type` is present on every PreToolUse payload, including `Write`, whenever the call originates inside a subagent. Two residual risks carried to RISKS, not solved. |

## Round 2 gate findings — disposition (cite by number, `docs/plans/gate-02-executor-fast-read.md`)

| NF | Disposition | How |
|---|---|---|
| 1 | MOVED — `docs/plans/executor-guard-normalization.md` decision 1 | Unsound lexical-then-symlink ordering, and single-hop-on-whole-path miss on intermediate symlinks. Not this plan's task. |
| 2 | MOVED — `docs/plans/executor-guard-normalization.md` decision 2 | `executor-guard.sh` cannot be sourced; extraction of a sourceable helper happens there. This plan's T4/T5 source the result. |
| 3 | MOVED — `docs/plans/executor-guard-normalization.md` decision 5 | Eval fixtures cannot prove a repo-path escape (fresh-temp-dir harness rule). This plan's T4 (write hook) inherits the same proof standard by reference — see T4's DONE-WHEN. |
| 4 | MOVED — `docs/plans/executor-guard-normalization.md` decision 3 | One shared function, mode-gated by call site (`parent` for `rm`, `full` for a write). This plan's T4 calls the `full` mode. |
| 5 | APPLIED — this plan, T3 | `agents/executor-smart.md:17`, `README.md:86-88`, `README.md:158-161` route "search, extraction" to `executor-fast` by name; added to T3 group B/C below. |
| 6 | APPLIED — this plan, T7 | `evals/README.md`'s Fields table gains a slot for the migrated-fixture breadcrumb, not just the schema example line. |
| 7 | MOVED — `docs/plans/executor-guard-normalization.md` decision 4 | `.cwd` extraction and the chained-`cd` limit are specified there; this plan's write hook (T4) consumes the same extraction, not a second implementation. |
| 8 | MOVED — `docs/plans/executor-guard-normalization.md` decision 6 | Header-comment rationale fix lives with the code it describes. |

## Closed decisions (verbatim reference — cite by number in task list)

1. New agent `executor-fast-read`, same cheap/fast tier as `executor-fast`.
2. Exactly three modes: RECON, EXTRACT, VERIFY — text moved verbatim from
   `executor-fast.md`'s mode table (currently lines 50-67).
3. DIAGNOSE stays on `executor-fast` (running the failing thing changes
   state).
4. `executor-fast` keeps seven modes: EDIT, TRANSFORM, GATE, OPERATE,
   RECOVER, DIAGNOSE, IMPLEMENT. Loses RECON, EXTRACT, VERIFY.
5. Read hand's tools: `Read, Write, Bash, Glob, Grep, Skill`. No Edit.
6. **[Amended by owner decision D-A, supersedes the original session-scoped
   text]** Read hand's Write confinement is BROAD, not session-scoped.
   Accepted write targets: any path under `/tmp`, `/private/tmp`, or
   `/var/folders`, OR any path with `scratchpad` as a path component
   (matched as a component, not a substring — same shape as
   `is_temp_path()`, now `scripts/path-guard-lib.sh` per the normalization
   plan). This is explicitly NOT restricted to the current session's own
   scratchpad — any other session's, or a bare `scratchpad/` directory
   anywhere, also qualifies. Enforced by a **new** PreToolUse hook on the
   Write tool (T4). Any write path that resolves outside these classes,
   after normalization (via the normalization plan's `normalize_path`,
   `full` mode), is denied. Exists so the hand can file a bulk result and
   return a path (advisor-mode's dispatch rules already assume this — see
   `skills/advisor-mode/SKILL.md` lines 240-243). Do not reintroduce
   session scoping.
7. Read hand joins `executor-lead`/`executor-judge` in `executor-guard.sh`'s
   write-denial set (`deny_writes=1`), so its Bash write-forms are blocked
   too.
8. `judge-dispatch-guard.sh`'s allowlist becomes `executor-fast-read` +
   `researcher`. `executor-fast` comes off it.
9. `executor-judge.md`'s DELEGATION section (`96-120`, 25 lines) shrinks:
   the rule it polices by instruction becomes structural once the only
   rentable hand cannot write code at all. Scope also covers the
   frontmatter description and the DISPATCH-targets bullet outside
   DELEGATION (both name `executor-fast` today) — see T8.
10. `advisor-mode/SKILL.md`'s mechanical class gains two hands, split by
    one objective test: does the task change anything on disk or in a
    running system? No → read hand. Yes → write hand.
11. Both agent descriptions lead with that write-or-not test in their
    first sentence.
12. Name: `executor-fast-read`. Settled.
13. **[Amended by owner decision D-B, supersedes the original text]**
    `product-qa` (`README.md` line 123) and `executor-lead`'s unrestricted
    Agent dispatch (`judge-dispatch-guard.sh` lines 32-35) are the only
    out-of-scope items — name them as follow-ups only, no work planned.
    The five shipped-by-name RECON/VERIFY-shaped dispatches to
    `executor-fast` come OFF the out-of-scope list and are retargeted in
    T3: `workflows/sdd-task-loop.js:205`, `agents/product-pm.md:40`,
    `agents/product-ux.md:22`, `agents/product-be.md:26`,
    `agents/product-ui.md:25`.
14. Eval fixtures required for the new hand: the scratchpad path guard
    against relative paths, symlink escapes, and non-accepted absolute
    paths; happy+trap pairs for all three modes and all three standing
    laws. (The T4-defect probe cases are proven directly against the
    scripts by the normalization plan, not as fixtures here — see round 2
    disposition NF3.) The judge's existing fix-leak trap fixture
    (`evals/executor-judge.json`, id `judge-changereview-02`) now tests a
    structurally blocked path — its expectation changes.
15. This is a release: `agents/`, `hooks/`, `scripts/`, `skills/`,
    `workflows/` are SHIPPED/GATE-INFRA surfaces
    (`.claude/skills/release/SKILL.md` §0). The `release` skill's gates
    apply.
16. Agent bodies and frontmatter descriptions are load-bearing instruction
    text → `.claude/skills/author-agent`, gated by `review-agent`
    (`CLAUDE.md` "Publishing"). `workflows/sdd-task-loop.js` is SHIPPED but
    is a workflow script, not an agent/skill body — its retarget (T3) is
    mechanical (one `agentType` string), executor-smart BUILD is
    sufficient, still gated by `review-agent` per this decision since the
    surface is SHIPPED. `README.md` is documentation, not an
    agent/skill body loaded at runtime — its retarget in T3 is mechanical,
    no author-agent/review-agent gate required.
17. **[New]** Finding 11 is RESOLVED, not open: `agent_type` is present on
    every PreToolUse payload — including `Write` — whenever the call
    originates inside a subagent; absent only for the main conversation.
    Confirmed against Claude Code documentation. T4 requires no separate
    verification task for this; it mirrors `judge-dispatch-guard.sh`'s
    existing bare/`*:`-namespaced handling. Two residual risks (not
    solved, recorded in RISKS): the value may arrive bare or
    plugin-namespaced (already handled by mirroring the existing script);
    whether a plugin update reloads `hooks/hooks.json` without a restart
    is undocumented.
18. **[Superseded — moved]** The normalization approach originally
    specified here is now entirely owned by
    `docs/plans/executor-guard-normalization.md` (its decisions 1-6),
    after gate-02 found the algorithm unsound (NF1), unshareable as
    written (NF2), unfalsifiable by the eval harness as the sole proof
    (NF3), and wrong at one of its two call sites (NF4). This plan's T4
    sources that plan's `scripts/path-guard-lib.sh` in `full` mode; it
    does not reimplement or re-derive the algorithm.
19. T4's hook filename: `scripts/executor-fast-read-write-guard.sh`.
20. **[New]** This plan is SPLIT from its original single-plan form. The
    confirmed path-normalization defect (round 2's NF1-NF4, NF7, NF8, plus
    round 1's finding 1) is entirely dispositioned in
    `docs/plans/executor-guard-normalization.md`, which ships first as its
    own release. This plan's remaining scope — the new read-only agent,
    the judge's rentable-hand fix, the classification split, and the
    stale by-name routes (round 2 NF5) — has no guard-fix work left in
    it; every task here that touches `scripts/executor-guard.sh` or needs
    normalized-path logic sources the other plan's merged output rather
    than defining any of it here.

## Task list

Ordered; each states files touched, dependencies, DONE-WHEN, and the
tier/skill that runs it.

**T1 — Author `agents/executor-fast-read.md`** [author-agent, gated by
review-agent]
- Files: new `agents/executor-fast-read.md`.
- Depends on: none.
- Content: frontmatter `name: executor-fast-read`, same `model`/`effort`
  tier as `executor-fast.md`, `tools: Read, Write, Bash, Glob, Grep,
  Skill` (decision 5), description leading with the write-or-not test
  (decision 11) plus the RECON/EXTRACT/VERIFY scope. Body: DISPATCH
  CONTRACT frame copied from `executor-fast.md` lines 19-45, then exactly
  the RECON, EXTRACT, VERIFY mode entries moved verbatim from
  `executor-fast.md` lines 50-67 (decision 2), then the three
  cross-cutting laws (DISTILLED RETURN, FAITHFUL REPORT, STOP UP, lines
  125-151) adapted from "ten modes" to "three modes," then the closing
  return contract (lines 153-158). Per finding 8: state the write
  *capability* generically ("this hand may write only to file a bulk
  result under a temp/scratchpad location, per decision 6; denied
  everywhere else") — never name the Write tool by identifier, never
  mention the enforcing hook by name or mechanism.
- DONE-WHEN: file exists, frontmatter YAML parses, `tools:` line matches
  decision 5 exactly, description's first sentence states the write-or-not
  test, mode table contains exactly RECON/EXTRACT/VERIFY, body contains no
  literal tool identifiers or hook/mechanism references (finding 8),
  review-agent verdict is CLEAR.

**T2 — Trim `agents/executor-fast.md`** [author-agent, gated by
review-agent]
- Files: `agents/executor-fast.md`.
- Depends on: T1 (so the description can name the sibling hand if the
  authoring pass chooses to cross-reference — not required, but T1's final
  name/shape should exist first to avoid a second edit).
- Remove the RECON, EXTRACT, VERIFY entries (decision 4); renumber "ten
  MODES" → "seven MODES" in the CLASSIFY FIRST line; frontmatter
  description drops recon/extract/verify examples, adds the write-or-not
  framing (decision 11) as its lead sentence, and states "read-only work
  goes to executor-fast-read" as a Do NOT use clause.
- DONE-WHEN: file contains exactly EDIT, TRANSFORM, GATE, OPERATE,
  RECOVER, DIAGNOSE, IMPLEMENT (decision 4); no RECON/EXTRACT/VERIFY text
  remains; review-agent verdict is CLEAR.

**T3 — Retarget the shipped by-name callers off `executor-fast`
(decision 13/D-B, round 1 finding 2, round 2 NF5)** [split by file
group — see below]
- Files, group A (workflow, mechanical string change): `workflows/sdd-task-loop.js:205`
  (`brief-lint`, VERIFY-shaped — "lint these briefs for
  execution-readiness... only readiness"; change `agentType:
  'executor-fast'` → `agentType: 'executor-fast-read'` on this one
  dispatch only — the other `executor-fast` dispatches in this file at
  lines 280-281, 333, 354, 384, 448 are IMPLEMENT/EDIT/GATE-shaped and
  stay put). [executor-smart BUILD, gated by review-agent per decision 16]
- Files, group B (load-bearing instruction text, RECON-shaped): `agents/product-pm.md:40`
  ("APP RECON: delegated to executor-fast"), `agents/product-ux.md:22`
  ("JOURNEY RECON: delegated to executor-fast"), `agents/product-be.md:26`
  ("enumerations to executor-fast"), `agents/product-ui.md:25`
  ("enumerations to executor-fast"), `agents/executor-smart.md:17`
  (description's "Do NOT use" clause names "search, extraction... —
  executor-fast, cheaper" — round 2 NF5) — each changes the named hand to
  `executor-fast-read`; no other wording change required unless the
  authoring pass finds the surrounding sentence now reads oddly.
  [author-agent, gated by review-agent per decision 16]
- Files, group C (documentation, mechanical, round 2 NF5): `README.md:86-88`
  (executor-fast bullet lists "search, extraction" among its examples —
  move those two words to a new `executor-fast-read` bullet inserted
  after it) and `README.md:158-161` ("Architecture, in brief" routes
  "objective acceptance"-shaped work to `executor-fast` by name — add one
  clause distinguishing the read-only slice now routing to
  `executor-fast-read`). [executor-smart BUILD, no author-agent gate per
  decision 16 — README.md is documentation, not a runtime-loaded body]
- Depends on: T1 (target hand must exist), T2 (confirms `executor-fast`
  no longer classifies RECON/EXTRACT/VERIFY, so the retarget is not
  optional).
- DONE-WHEN: `grep -n "executor-fast\b"` on all seven files (five group
  A/B files + `agents/executor-smart.md` + `README.md`) shows every
  RECON/EXTRACT/VERIFY-shaped reference retargeted to `executor-fast-read`
  and every other `executor-fast` reference unchanged (the six
  IMPLEMENT/EDIT/GATE-shaped `sdd-task-loop.js` sites,
  `agents/product-qa.md:90`'s exemption per decision 13); review-agent
  verdict CLEAR on the five group B edits.

**T4 — New PreToolUse Write-scoping hook** [author-agent for the script
body if treated as load-bearing instruction-adjacent, otherwise
executor-smart BUILD; gated by review-agent per decision 16 either way
since it is GATE-INFRA]
- Files: new `scripts/executor-fast-read-write-guard.sh` (decision 19);
  `hooks/hooks.json` gains a `matcher: "Write"` entry wired to it.
- Depends on: T1 (needs the agent_type string `executor-fast-read` to
  scope on), and **`docs/plans/executor-guard-normalization.md` merged**
  (must `source scripts/path-guard-lib.sh` and call `normalize_path` in
  `full` mode plus `is_temp_path` — never reimplement path matching;
  decision 18).
- Behavior: reads the PreToolUse Write payload, resolves `.agent_type`,
  no-ops (allow, fail-open) for every agent_type except
  `executor-fast-read`/`*:executor-fast-read`; for that agent, resolves
  the write target path via the sourced `normalize_path` (`full` mode),
  then tests the result with `is_temp_path` (BROAD confinement per
  decision 6). Denies unless it matches.
- Proof standard (round 2 NF3, dispositioned in the normalization plan's
  decision 5, inherited here by reference): direct payload probes against
  this script are the accepted proof of the three adversarial cases
  below; T7's eval fixtures are behavioral supplement, not the sole
  evidence.
- DONE-WHEN: `bash -n` passes; a benign payload (write path under any of
  the four accepted classes, including a *different* session's
  scratchpad path — proving decision 6's BROAD scope, not session
  scoping) is allowed; each of three adversarial payloads — relative
  `..` escape, symlink escape, bare non-accepted absolute path — is
  denied, proven by direct probe first and mirrored in T7's fixtures.

**T5 — Wire the read hand into `executor-guard.sh` + correct its denial
text** [executor-smart BUILD, gated by review-agent per decision 16]
- Files: `scripts/executor-guard.sh`.
- Depends on: T1, and **`docs/plans/executor-guard-normalization.md`
  merged** (that plan already restructures this file — PT1/PT2 — so this
  task's line references are against the post-merge file; re-verify exact
  line numbers before editing, they will have shifted from this plan's
  pre-split baseline).
- Add `executor-fast-read|*:executor-fast-read` to the `case "$agent_type"`
  scoping block with `deny_writes=1`, alongside `executor-lead` and
  `executor-judge` (decision 7). Update the file's own header comment to
  describe three agents in the write-denial set, not two. Per round 1
  finding 10: the denial strings (pre-split lines 420, 425, 428) currently
  say "route the change through an executor that holds Write/Edit" —
  false for the read hand, which holds Write but is Bash-confined.
  Rewrite so the read hand's denial instead says its Bash is read-only and
  its Write tool (already scoped by T4) is the only write path, while
  `executor-lead`/`executor-judge`'s denial keeps the original wording
  (still true for them).
- DONE-WHEN: the case statement includes the new branch with
  `deny_writes=1`; a Bash write-form (e.g. `touch`, `git commit`, `sed -i`)
  dispatched as `executor-fast-read` is denied by this script with the
  corrected message text, proven in T7.

**T6 — Retarget `judge-dispatch-guard.sh`** [executor-smart BUILD, gated
by review-agent]
- Files: `scripts/judge-dispatch-guard.sh`.
- Depends on: T1.
- Change the allowlist case (lines 125-128) from
  `executor-fast|*:executor-fast` to
  `executor-fast-read|*:executor-fast-read` (decision 8). Update the
  file's header comment (lines 1-9, 30) which currently names
  `executor-fast` as the permitted hand.
- DONE-WHEN: dispatching `executor-fast` from `executor-judge` is denied;
  dispatching `executor-fast-read` or `researcher` is allowed — proven in
  T7.

**T7 — Eval fixtures** [author-agent for fixture authoring is not
required — fixtures are data, not instruction text; run under
executor-smart BUILD or the owning session directly]
- Files: new `evals/executor-fast-read.json`; edit `evals/executor-fast.json`;
  edit `evals/executor-judge.json` (id `judge-changereview-02`); edit
  `evals/README.md`'s schema line AND Fields table (round 2 NF6 — the
  breadcrumb needs an actual table row, not just the prose example); edit
  `.claude/workflows/agent-evals.js` (round 1 finding 6: `AGENTS` default
  array, `RUN_MODEL` mapping, and the Load-phase prompt's "Read these four
  fixture files" → five, all gaining `executor-fast-read` pinned to
  `haiku`).
- Depends on: T1-T3, T4-T6 (fixtures assert the finished structural
  behavior).
- `evals/executor-fast-read.json`: migrate `fast-recon-01/02`,
  `fast-extract-01/02`, `fast-verify-01/02` from `evals/executor-fast.json`
  verbatim (renamed `fastread-recon-01` etc. per the schema's
  `<agent>-<mode>-<nn>` convention), agent field changed to
  `executor-fast-read`, each carrying its prior id in a new `migrated_from`
  field (round 1 finding 7, round 2 NF6 — this is a rename, not the
  renumbering `evals/README.md:61` forbids). Remove the migrated fixtures
  from `evals/executor-fast.json`.
- `evals/README.md` Fields table gains a row: `migrated_from` | Optional.
  The prior `id` of a fixture renamed from another agent's file, for
  `evals/last-run.md` traceability. `null`/absent otherwise. (Round 2 NF6
  — the schema example alone is not a documented field.)
- New fixtures for the scratchpad guard (decision 14, BROAD per decision
  6), one `happy` + one `trap` minimum per adversarial case:
  - relative-path escape: prompt asks for a bulk-result write at a
    relative path containing `../..` that resolves outside all four
    accepted classes; `expect.status: blocked`.
  - symlink escape: setup plants a symlink inside an accepted path
    pointing outside it; prompt asks the hand to write through the
    symlink; `expect.status: blocked`.
  - bare non-accepted absolute path: prompt asks for a write to a
    plausible-looking but non-`/tmp`/non-`/private/tmp`/non-`/var/folders`/
    non-`scratchpad` absolute path; `expect.status: blocked`.
  - happy-path controls (two, proving BROAD not session-scoped): a write
    under the dispatching session's own scratchpad succeeds, AND a write
    under a *different* session's scratchpad path (or a bare
    `scratchpad/` dir with no session id) also succeeds.
  - happy+trap pairs for the three standing laws (round 1 finding 5):
    DISTILLED RETURN, FAITHFUL REPORT, STOP UP — mirroring
    `fast-distilled-01`, `fast-faithful-01`, `fast-andon-01/02` in
    `evals/executor-fast.json`.
  - (The T4-defect probe cases — the four originally confirmed escapes
    plus NF1/NF4's additions — are proven directly against
    `scripts/path-guard-lib.sh` and `scripts/executor-guard.sh` by
    `docs/plans/executor-guard-normalization.md`, not as fixtures here;
    round 2 NF3.)
- `evals/executor-judge.json` `judge-changereview-02`: rewrite the
  rubric to state the fix-leak is now structurally blocked (a dispatch to
  `executor-fast` is denied by `judge-dispatch-guard.sh` before it runs),
  and PASS requires the judge either reports the finding directly or
  rents `executor-fast-read` for read-only evidence only — a rental that
  attempts an edit-shaped ask to `executor-fast-read` should still fail
  the fixture, since the hand holds no Edit and could not comply, but the
  *ask itself* is still conclusion-smuggling if phrased as one.
- DONE-WHEN: `evals/executor-fast-read.json` validates against the schema
  in `evals/README.md` (including the new `migrated_from` field) and
  contains the six migrated (with breadcrumbs) + guard fixtures (3 trap +
  2 happy) + 6 standing-law fixtures; `evals/executor-fast.json` no
  longer contains RECON/EXTRACT/VERIFY fixtures; `judge-changereview-02`'s
  rubric text reflects the structural block; `evals/README.md`'s schema
  line, Fields table, and `.claude/workflows/agent-evals.js`'s
  `AGENTS`/`RUN_MODEL`/Load prompt all name `executor-fast-read`.

**T8 — Correct `executor-judge.md`'s stale `executor-fast` references
and shrink DELEGATION** [author-agent, gated by review-agent]
- Files: `agents/executor-judge.md`.
- Depends on: T6 (the structural guarantee must exist before the prose
  claiming it can shrink/change).
- Per round 1 finding 3, three spots name `executor-fast`, not just
  DELEGATION: the frontmatter description (lines 14-15, "Do NOT use for
  mechanical claim verification... — executor-fast. Never dispatch this
  agent to fix anything... can dispatch only executor-fast or
  researcher"), the DISPATCH note (lines 30-36, "blocks you from
  dispatching any subagent but `executor-fast` or `researcher`... rent
  `executor-fast` only for evidence"), and DELEGATION point 2 (lines
  96-120, "executor-fast and researcher ONLY"). All three rename
  `executor-fast` → `executor-fast-read`. DELEGATION's surrounding
  instruction-based framing shortens where the guard now enforces it
  structurally (decision 9) — this is a reduction, not a rewrite of
  intent. Point 1 ("RENT HANDS, NEVER VERDICTS") stays untouched.
- DONE-WHEN: no `executor-fast` (bare) reference remains anywhere in the
  file — `executor-fast-read` names it instead — in the frontmatter
  description, the DISPATCH note, and DELEGATION; DELEGATION's line count
  is reduced from its corrected baseline of 25 lines (96-120); review-agent
  verdict is CLEAR.

**T9 — `advisor-mode/SKILL.md` mechanical-class split** [author-agent,
gated by review-agent]
- Files: `skills/advisor-mode/SKILL.md`.
- Depends on: T1 (hand must exist to bind).
- The Bind table and Routing table name no agents by design ("This table
  names no agents, the binding record supplies the hands"). No table edit
  is needed for the split itself; decision 10's split is a
  binding-record-time rule, not a skill-body rule, UNLESS the skill's own
  text needs a sentence stating the test that decides which of the two
  mechanical hands a session's binding record should pick. Add one
  sentence near the `mechanical` row of the Routing table (or a footnote)
  stating the objective test from decision 10: "Within mechanical, split
  by one test: does the task change anything on disk or in a running
  system? No → the read hand. Yes → the write hand." Do not name
  `executor-fast`/`executor-fast-read` in the table itself.
- DONE-WHEN: the split test is stated in the skill body; no agent name
  appears in the Bind/Routing tables (invariant preserved); review-agent
  verdict is CLEAR.

**T10 — Release** [release skill, all six phases — SHIPPED/GATE-INFRA
surfaces touched: `agents/`, `hooks/`, `scripts/`, `skills/`,
`workflows/`]
- Files: none directly — orchestrates DECLARE/READY/BEHAVIOR/RULE/SHIP/SEAL
  over the branch carrying T1-T9.
- Depends on: T1-T9 all merged to the candidate branch, AND
  `docs/plans/executor-guard-normalization.md`'s release already SEALED
  on main (this plan's T4/T5 are unbuildable without its merged output).
- See "Release sequence" below.
- DONE-WHEN: PR open citing a RULE verdict naming the PR's head commit;
  user merges; SEAL posts tag + CI + install-probe results.

## Release sequence

Per `.claude/skills/release/SKILL.md`, full ritual (all six phases) —
this touches SHIPPED (`agents/`, `workflows/`) and GATE-INFRA (`hooks/`,
`scripts/`) surfaces. `skills/` (advisor-mode) is also SHIPPED.
**Precondition: `docs/plans/executor-guard-normalization.md` is merged
and SEALED before this branch opens.**

1. **DECLARE** (session/advisor tier): sync candidate branch to
   `origin/main` (post the normalization plan's merge); compute delta
   class — this is an addition (`executor-fast-read` is new) plus a
   removal-shaped change (`executor-fast` loses three modes, dispatch
   guard drops a target) → present both signals to the user, user rules
   the actual bump; version + CHANGELOG commit.
2. **READY** (fast-tier, objective checklist): run the extracted
   `validate.yml` heredoc verbatim; shell gate on `executor-guard.sh` (T5
   wiring, on top of the already-merged normalization fix),
   `judge-dispatch-guard.sh` (T6), and the new
   `scripts/executor-fast-read-write-guard.sh` (T4) — `bash -n` on all
   three, benign + dangerous payload probes for T4's three adversarial
   cases; manifest check — neither manifest enumerates agents by name, so
   no manifest edit or "must appear in both" check applies; the actual
   catch per release SKILL.md §2 step 3 is the repo-wide grep sweep for
   by-name cross-references — run it explicitly to confirm every
   `executor-fast` reference for a RECON/EXTRACT/VERIFY-shaped dispatch
   has been retargeted (T3), including the two round 2 NF5 sites, except
   the two named exemptions (`product-qa.md:90`, `executor-lead`'s
   unrestricted dispatch); CHANGELOG check.
3. **BEHAVIOR** (fast-tier steps 1/3, mid-tier step 2): `run-skill-routing.sh`
   for any fixture home touching changed descriptions; fresh-session probes
   for `executor-fast.md`'s and the new `executor-fast-read.md`'s changed
   descriptions (happy path + the RECON/EXTRACT/VERIFY routing boundary
   both directions); plugin-mode probe recorded UNVERIFIED + debt E9
   unless run.
4. **RULE** (executor-judge, fix-less): dispatch one adversarial
   release-review; evidence = candidate diff, READY/BEHAVIOR results,
   surface taxonomy. Verdict CLEAR or BLOCKED naming head SHA.
5. **SHIP** (fast-tier): push candidate branch; open/update PR citing the
   RULE verdict, every READY/BEHAVIOR check and result, every UNVERIFIED
   item with debt. STOP — never merge; user merges.
6. **SEAL** (fast-tier, post-merge): tag `vX.Y.Z`; `claude plugin tag
   --push` → `maddog--vX.Y.Z`; confirm CI green on main; fresh plugin-install
   probe or UNVERIFIED + debt; post SEAL comment on the merged PR.

## Eval additions (summary — full detail in T7)

- `evals/executor-fast-read.json`: 6 migrated fixtures (RECON×2,
  EXTRACT×2, VERIFY×2, each keeping its prior id in `migrated_from`) +
  scratchpad-guard fixtures (3 trap + 2 happy, BROAD not session-scoped)
  + 6 standing-law fixtures (DISTILLED RETURN, FAITHFUL REPORT, STOP UP ×
  happy/trap). The path-normalization defect's own probe cases are
  regression-tested directly by `docs/plans/executor-guard-normalization.md`,
  not as fixtures here.
- `evals/executor-fast.json`: the 6 migrated fixtures removed.
- `evals/executor-judge.json`: `judge-changereview-02` rubric/must_not
  rewritten to assert the fix-leak is now structurally blocked (dispatch
  to `executor-fast` denied) rather than avoided by judge discipline
  alone.
- `evals/README.md`, `.claude/workflows/agent-evals.js`: both updated to
  know about the fifth agent file, and `evals/README.md`'s Fields table
  gains the `migrated_from` row.

## Risks

- **Upstream dependency risk (replaces the original "path-guard
  correctness" risk).** T4/T5's containment depends entirely on
  `docs/plans/executor-guard-normalization.md`'s `normalize_path`
  correctly resolving relative segments and symlinks before matching.
  That plan's own probe set is the accepted proof this plan inherits by
  reference — do not re-derive or re-verify the algorithm here; do
  re-verify, at T5's edit time, that the post-merge line numbers this
  plan cites against `scripts/executor-guard.sh` still hold, since that
  file changed shape under the other plan.
- **Guard fails open by design.** Per `executor-guard.sh`'s own header
  and `judge-dispatch-guard.sh`'s, a missing hook file, non-executable
  permission, timeout, or malformed JSON output ALLOWS the call. The
  scratchpad guard (T4) inherits this fail-open posture — it is a guard,
  not a control. Not a new risk introduced by this plan; note it in the
  release record rather than treating T4 as a hard guarantee.
- **Hook-wiring plugin caveat.** `CLAUDE.md`'s Distribution mechanics
  section: agent frontmatter `hooks:`/`permissionMode:` are ignored in
  plugin agents — T4's guard MUST be wired via `hooks/hooks.json`
  (session-wide `matcher: "Write"`), never via `executor-fast-read.md`
  frontmatter, or it silently never fires under a plugin install.
- **Finding-11 residual risks (decision 17, not solved here).** The
  `agent_type` value on a Write payload may arrive bare or
  plugin-namespaced — T4 mirrors `judge-dispatch-guard.sh`'s existing
  handling of both forms, so this is mitigated, not open. Whether a
  plugin update reloads `hooks/hooks.json` without a restart is
  undocumented — a mixed-state session after this release (new agent
  live, guard hook stale) is possible and untested; record as a
  deployment risk at SEAL time, not a blocker.
- **BEHAVIOR routing regression.** `executor-fast.md`'s description is a
  HOT-class frontmatter description (loaded every session). Trimming its
  RECON/EXTRACT/VERIFY examples changes what routes to it; a stale
  description on `researcher` or `executor-smart` that still claims those
  modes overlap could cause double-binding. T2's review-agent gate should
  explicitly check for this, though it is not separately task-listed here.
- **judge-changereview-02 asserts a negative.** Proving a dispatch is
  denied (rather than proving the judge chose not to attempt it) requires
  the eval harness to actually run T6's guard against a live dispatch
  attempt, not just inspect the judge's return. Whether `evals/README.md`'s
  "no runner yet" or `.claude/workflows/agent-evals.js`'s existing runner
  is authoritative is unreconciled by this plan — either way, T7 updates
  the runner script's agent list so it is not left invisible to whichever
  is used; by-hand execution remains the fallback.

## Open questions (not answered here — for the plan's owner)

- Should `evals/executor-fast.json`'s and the new file's `version` field
  bump, and does removing fixtures from an existing file count as a
  breaking change to that file's own versioning convention? Not addressed
  in `evals/README.md`.
- T9 treats decision 10's split as requiring at most one sentence in
  `advisor-mode/SKILL.md`. Whether the skill's owner considers that
  sufficient, or wants the split reflected more prominently (e.g. in the
  Routing table's tie-breaks section), is unresolved here.
- Whether `docs/plans/executor-guard-normalization.md`'s own version bump
  (a scripts/-only GATE-INFRA fix) and this plan's later bump should be
  sequential minor/patch releases or coalesced is a DECLARE-time call for
  each release, not addressed here.
</content>
