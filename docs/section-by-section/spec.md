# section-by-section — design spec

Date: 2026-09-19. Status: current design for `skills/section-by-section/`.
**Supersedes the spec approved 2026-09-15**, which described the 3.1.0 design.
The filed rulings `rulings/SBS-GATE-1.md`, `rulings/SBS-GATE-2.md`,
`rulings/SBS-GATE-3.md` and `rulings/SBS-GATE-3-erratum.md` ruled on that earlier
design and are kept as history; they do not bind this one, and the constraints
they established are carried forward explicitly below where they still hold.

This design was authored outside the `author-agent` loop, at the user's
instruction, and validated by blank-context reading (section 10) instead.

## 1. Purpose

A shipped, slash-only skill that walks ONE existing instruction file — a
`SKILL.md` or an agent definition — with the user, one section at a time. Each
section is tested against the file's stated intent and closed by the user with
one or more verdicts from a fixed vocabulary. Once every section is closed,
the reassembled whole is checked against that same intent. A run produces a
draft of the reworked file and a verdict ledger, and never edits the target.
Draft, ledger and target are the evidence set for an independent review the
skill does not run.

Protects PHILOSOPHY.md point 3 above all — the skill has no authority to decide
what an instruction file says, so the file grants it none — and points 1, 2 and
6: the user sees a compressed proposal per section, the ledger is the durable
record of what was decided, and every section must earn its place.

## 2. The closure law

The rule the file exists to carry, and the reason it sits in the premium slot:

> The skill proposes; the user closes. A section is closed when the user gives
> its verdicts and approves any replacement text they carry. No verdict
> the user did not give reaches the ledger.

Design consequences, not wording:

- **One closure word.** "Closed" is defined once and is the only closure term in
  the file. "Settled", "authorized" and "approved" are not used as synonyms —
  each invites the question "by whom?" and none of them answers it.
- **Assembly holds no closing authority.** Assembly changes no closed section on
  its own; every Assembly-time change is posted as a proposal and closed by the
  user, with its own ledger row. The counterweight is structural, not a qualifier
  such as "do not rewrite closed sections merely to assemble".
- **Every user contact leaves a durable mark.** The intent anchor and the
  observation ids open the ledger; every closure writes a row; the section map
  and the outline are shown and closed. An obligation with no artifact was either
  dropped or given one.

## 3. Scope

In scope:

- one target file per run, by path: a `SKILL.md` or an agent definition file
- a review scope: the whole file, or a named set of sections
- the target's frontmatter description (`DESC`), named first, in the section
  map at Start, and closed at Assembly's Verify step, before the outline
- the user's observations of how the target behaved — asked once, optional
- outside files the user names as something the target relies on — asked
  once, optional; read only by redundancy, pointers and names (D5)

Out of scope:

- authoring a new file: an intent no section carries is a GAP; it is drafted
  only once the user approves text for it, and closes with a second row
- a `references/` file, unless the user names it as the target of its own run
  (SBS-GATE-1 F1)
- applying the draft to the target, or dispatching the independent review
- running without the user: the user closes every section

## 4. Flow

The body is readable as this flow and carries no stage outside it.

```text
START           read target whole → setup message (intent anchor,
                section map, paths, observations and outside files) →
                wait until every item is answered
  │
  ▼
SECTION LOOP    for each in-scope section, in file order:
                diagnose (every check but deletions, each finding its
                own verdict) → settle → write → approve → record
  │
  ▼
ASSEMBLY        close every HOLD and GAP → rerun every diagnosis check
                over the whole file → verify the outline and the
                description together → compose the draft
  │
  ▼
HAND-OFF
```

Two blocks sit outside the flow because they are framing, not stages: the
closure law and the Check-table law above START, the Prohibitions below
HAND-OFF.

Two stages of the 3.1.0 design survive as one Assembly step, Verify (step 3):
the description can only be tested against a reworked body that exists, and
that body first exists at Assembly; the outline it shows and closes, before
the draft is composed, is the same step for the same reason.

## 5. Verdicts and markers

Nine verdicts. A section takes at most one placement verdict, plus any number
of wording verdicts; KEEP stands alone.

| Verdict | Kind | Means |
|---|---|---|
| KEEP | — | unchanged; no check found anything |
| REMOVE | placement | deleted |
| SPLIT | placement | two sections, each diagnosed and closed on its own |
| MERGE | placement | folded into a named partner, which keeps the question |
| MOVE | placement | relocated unchanged |
| REPLACE | wording | a different instruction takes its place, on evidence |
| RESHAPE | wording | same content, a form that fits it |
| COMPRESS | wording | same instruction, fewer words |
| REWORD | wording | same instruction, clearer words |

REMOVE and SPLIT carry no wording verdict of their own; a SPLIT's halves take
their own verdicts once diagnosed.

Three markers, which are not verdicts:

| Marker | Means | Then |
|---|---|---|
| HOLD | the user cannot decide yet | the loop goes on; still open at Assembly |
| GAP | the intent anchor needs an instruction no section carries | a ledger row |
| UNREVIEWED | outside this run's review scope | a ledger row, written when the scope is named, carried into the draft under a line reading `UNREVIEWED` |

Ten checks run inside Diagnose, every time, in this fixed order: redundancy,
responsibility, coherence, ambiguity, correctness, clarity, pointers, names,
form, deletions. Correctness runs only on a diagnosis, because it needs
evidence new text cannot have; deletions runs only on proposed text. Every
check that finds something contributes its verdict — a section can carry
several — and the fixed order means a check that produced nothing still
shows as a row, rather than as a gap nobody can see.

This replaces the 3.2.0–3.3.2 design's ordered, first-match test: triggers
ran in a fixed precedence and the earliest true line gave the section its
one and only verdict. That design was the source of a recurring defect
(§13): a section that needed two verdicts — say RESHAPE and REWORD, or a
placement change and a wording fix — could carry only the first the test
reached, and the rest went unrecorded.

## 6. Artifacts

- **Draft.** The full reworked file, at a path named at START, defaulting to the
  session's scratch directory; where the runtime has none, the user is asked for
  a path (SBS-GATE-1 F15). Never the target path.
- **MOVE-destination draft.** Where a MOVE targets another file, that file is
  drafted beside the draft, named for the destination file it feeds and never the
  draft's own path, so it collides with neither the draft nor an existing file
  (SBS-GATE-1 F5).
- **Ledger.** A markdown table with a header separator, opening with the intent
  anchor, the observation ids, the named outside files, the review scope, and
  a Rulings list (`R1..Rn`, empty at the start; every later proposal names any
  ruling it bends). Then one row per closure, each row written at its closure.
  No proposal is posted and no artifact composed until the previous closure's
  row exists — the structure that makes the ledger unskippable and lets a pass
  resume mid-file.

  | id | title | verdicts | reason | evidence | detail |
  |---|---|---|---|---|---|
  | S4 | Return format | MERGE | S9 already answers how the return is shaped | O1 | partner S9 |
  | S7 | Retry rule | REWORD, COMPRESS | said its rule in more words than it needed, and the retry count had a second reading | O3 | — |
  | — | Escalation | GAP | O2 names a failure no section covers | O2 | — |

  Ids are `S1..Sn`; a SPLIT yields `S3a` and `S3b`; the frontmatter description is
  `DESC`; a GAP row carries no section id (SBS-GATE-3 F21 and its erratum). The
  `verdicts` column holds the closed set, placement verdict first — not one
  verdict, since 3.4.0 (§13). `reason` is what the section closed on — the
  user's reason where it differs from the proposal's. `detail` carries the
  MOVE destination, the MERGE partner, the SPLIT halves, or `—`.
- **Hand-off.** Delivers the draft, the ledger, and any second file a MOVE to
  another file produced; names the observations no verdict cited.

## 7. Prohibitions

The body carries one prohibition, at the bottom: never write to the target
path — every change lands in the draft.

The other two the 3.2.0 design stated here are gone, since 3.3.0: "never
judge a section before START closes" survives in meaning inside Start
("Diagnose no section until the user has answered every item it asks
about"); the bar on dispatching or naming an independent review survives
nowhere, since Hand-off no longer mentions one. Everything the 3.1.0 body
also listed as a prohibition — never close a section without the user, never
draft a GAP, one target file per run — is likewise stated once, in the
section that owns the question, and is not repeated at the bottom. A
prohibition block that restates rules already carried elsewhere is exactly the
redundancy this skill exists to find.

Deliberately NOT a prohibition: any bar on writing to existing file paths.
SBS-GATE-2 F16 ruled that such a bar contradicts the ledger, whose path is an
existing file on any resumed pass.

## 8. The skill file

Path: `skills/section-by-section/SKILL.md`. Residency: WARM, loaded per
invocation. No `references/` file.

Size at 3.2.0: 174 lines / 1562 words, against 154 / 1370 at 3.1.0. The body is
larger, not smaller, because it now supplies what the 3.1.0 body left implicit:
eight verdict triggers instead of five tests, the closure law, the interpret
step, the selected-sections mode with its UNREVIEWED marker, Assembly's authority
rule, and the ledger header. The compression the user asked for landed in the
prose, not the rule count.

Frontmatter: `disable-model-invocation: true` — a long interactive ritual, and
auto-triggering it on "review this skill" would hijack a quick review — and
`argument-hint: [path to SKILL.md or agent file]`. The description is 448
characters, under the 500-character target in
`.claude/skills/review-agent/references/description-standard.md` §3, and carries
a claim naming the whole-file check alongside the section-by-section pass, a
"Use when" trigger sentence, two redirects (against shaping a file by how long
it stays loaded, with the efficient-md pointer guarded "where installed" per
SBS-GATE-1 F4, and against authoring a new file) and the never-edits invariant.
It carries no procedure: an agent that acts on a description without loading
the body must not be able to run the ritual from it.

Body order: closure law, Check-table law, Start, Markers, Section loop,
Assembly, Hand-off, Prohibitions. The body names capabilities (read, write a
draft), never runtime tool identifiers (CLAUDE.md invariants; PHILOSOPHY.md
point 5), and cites `efficient-md` only in the form guarded by "where that
skill is installed" (SBS-GATE-1 F4, and efficient-md's own SHIP RULE).

## 9. What changed from the 3.1.0 design

| Change | Why |
|---|---|
| Closure law hoisted to the premium slot; "closed" defined once | closure words with no actor — settled, authorized, approved — leave the skill free to close a section itself |
| Every verdict gets a trigger; the test is ordered and first-fit | four of the eight verdicts had no trigger at all, so they were unreachable |
| REMOVE's trigger narrowed to "the intent needs nothing this section says" | the looser form swallowed every MERGE case |
| Assembly may change no closed section on its own | resolving ownership and contradictions between closed sections is a decision, and it had no user in it |
| "Assembly must not invent policy" replaced by "Assembly writes no instruction the user has not closed" | the old prohibition cancelled Assembly's own obligations |
| UNREVIEWED marker added | a selected-sections run emitted a draft in which unreviewed sections were indistinguishable from sections closed KEEP |
| HOLD kept, with one named resolution point | an undecided section otherwise has no representation and no exit |
| Ledger is a real markdown table, opening with the intent anchor and observation ids | it rendered as a wall of pipes, and two START closures left no durable trace |
| Interpret step added before Settle | "discuss until the decision is settled" treats a reaction as a verdict |
| Description rewritten to 483 chars: trigger sentence restored, procedure removed, both redirects restored | description-standard §3 and §5 |
| "Description last" and "Arrange" demoted from stages to Assembly steps | the user's mandated flow has four stages, and both fit inside Assembly without loss |
| Prohibitions cut from six to three | the other four restated rules their owning sections already carried |

## 10. Validation

There is no test suite (CONTRIBUTING.md §Validation). This design was validated
by **blank-context reading**: the whole body was pasted to fresh agents on two
model tiers, with no repository access, no prior version and no spec, and each
was asked — for a set of concrete situations — which section answers it, what to
do, and who performs each action. Their wrong answers and their disagreements
with each other were the defect list. Each fix addressed the class of
underspecification, never the individual probe, and no test case is named in the
body.

Four rounds ran. Round 1 found an underivable MOVE-destination filename, two
obligations with no visible trace, and a reader disagreement over COMPRESS vs
REWORD. Round 2 found the REMOVE-swallows-MERGE defect recorded in section 5.
Rounds 3 and 4 produced no wrong answer about who acts and no two sections
claiming one question, which is the stop condition.

Two residual findings are accepted, not fixed:

- The verdict table's meanings and Diagnose's triggers both bear on the
  COMPRESS/REWORD distinction. The table is the reference card; the test is the
  decision. Folding the table into the test would remove the overlap and about
  ten lines, at the cost of the at-a-glance vocabulary.
- Neither the closure law nor the ordered test can be verified from the artifacts
  alone: nothing in a ledger proves the verdict came from the user rather than
  from the skill. The diagnosis post's check table, naming what each check
  looked at and its result, is the closest available trace; the diagnosis post
  no longer carries a separate `Fails` line.

For any later change, the same method is the validation, together with a live
run: exercise the skill on one `skills/*/SKILL.md` and one `agents/*.md` with at
least one observation supplied, and confirm the draft and ledger land at the
named paths and the target is byte-identical afterwards.

## 11. What changed in 3.3.1

Three changes, all from a live run of the skill against its own file, with the
user closing every verdict.

- **Tested-text law**, a third law beside the closure and progressive-disclosure
  laws. Text the skill proposes for the file is run over the axes before it is
  shown, and the result is shown above it as a `Tested:` block. The 3.3.0 design
  carried the same requirement as an emphatic sentence inside the Write step,
  and it was skipped in production: the test produced nothing observable, so
  nothing marked its absence. Each producing step — Write, Assembly step 6,
  Assembly step 7 — names the block in the same words, because naming the law
  alone fired at one step and not another.
- **Diagnose reads the section against the section map** before going down the
  axes. REMOVE on duplication, MERGE and SPLIT all depend on what other sections
  say, and nothing asked for that comparison. Runs that skipped it fell through
  to a clarity verdict on a section another section already owned.
- **Redundancy's trigger** covers "another section already says all of it", so a
  fully duplicated section stops there instead of also matching MERGE. An added
  condition on MERGE was tried for the same purpose and reverted: it made MERGE
  fire less often and cost the partial-overlap case.

Validation was a live run plus scenario runs on a cheap model, cut at each step
that produces text. After the change the block appears unprompted at all three
producing steps, a fully duplicated section draws REMOVE in three of three runs,
partial overlap draws MERGE in two of two, and a diagnosis post never carries a
block.

## 12. What changed in 3.3.2

Two changes, from the release review of 3.3.1, which found that release
reintroducing the defect it existed to fix.

- **The diagnosis block gains an `Elsewhere:` line**, under `Does:`, for what
  other sections already answer that bears on this one. 3.3.1 told Diagnose to read
  the section against the section map and report nothing about it, so a skipped
  comparison left no mark. Diagnose now names that line where it orders the
  comparison. The line lives in the diagnosis post and never reaches the ledger,
  which records closed decisions and not conversation, so §10's residual on
  artifact-only verification stands unchanged.
- The Also line's template said "other axes that fired" where the rule in
  Diagnose is "Lines below it may describe the section too". Two runs filed an
  axis above the verdict's, asserting a check had fired that had not. The
  template now reads "axes below the verdict's that also fired".

  Known limitation, left open: a second trigger inside one axis has no legal
  place. One run produced that case, COMPRESS as the verdict with REWORD also
  applying, both under clarity. A wording of "lines below the verdict's",
  matching Diagnose's own sentence, would admit it, and it was tried: across
  eight runs it produced no Also line at all, where "axes below" had produced
  two correct ones. It was reverted on that evidence. The mismatch between
  Diagnose's line-granular sentence and the template's axis-granular one
  predates this release.

Validation: scenario runs on a cheap model, cut at the point where the agent
must post a diagnosis.

- The `Elsewhere:` line appeared in every run of the shipped shape, nine of
  nine, and named the overlapping section each time. Two further runs carry the
  line in its earlier position and are reported separately below.
- A fully duplicated section drew REMOVE in four of four.
- Partial overlap drew MERGE in four of five. The fifth reported the overlap on
  the `Elsewhere:` line and then took a clarity verdict, the fallthrough this
  line exists to expose. Two control runs against the same file with the line in
  its earlier position split the same way, so the position is not what decides
  this fixture. Whether carrying the line at all affects the verdict is untested
  at a useful number of runs: the 3.3.1 shape, which has no line, drew MERGE in
  two of two.
- The Also line's new wording is confirmed in both directions, thinly. Across
  twelve runs carrying it, no run filed an axis above the verdict's, which is
  the misfiling it targets. Two runs on a fixture built for the positive case —
  a section answering two questions, also written in padded prose — filed
  `Also: clarity` under a responsibility verdict, which is the line working as
  intended. A third run on that fixture filed a second clarity line, the
  limitation recorded above.
- The positive case resists demonstration on a cheap model. A fourth fixture
  put the verdict on correctness, driven by a supplied observation, with padded
  prose below it: three runs returned REPLACE citing the observation and left
  the Also line empty, though clarity plainly applied. Across every fixture the
  Also line carries content in a minority of runs. It is advisory and carries no
  verdict, so an omitted one loses information without producing a wrong
  decision.

## 13. What changed in 3.4.0

Sourced from a sweep of 76 user catches across 8 real runs, grouped into 11
file-agnostic patterns (`docs/section-by-section/plan-2026-09-27.md`,
decisions D1–D6), then a section-by-section review of this file against
itself with the user closing every verdict and a judge gate on the result.
The run's draft and ledger were session-scratch and were not kept; the
rulings R1–R7 survive in `docs/section-by-section/state.md`. Validation was
the user closing every section, an independent judge gate on the draft
(PASS WITH FIXES, six fixes closed), and the release reviewer. The
description (`DESC`) was reopened at release review to bring it under the
500-character target and to restore the efficient-md redirect guarded
"where installed" (SBS-GATE-1 F4).

- **A section may carry several verdicts** (ruling R1, plan D2). The
  3.2.0–3.3.2 ordered, first-match test gave one verdict where several
  applied — pattern 5, restated across 3 sessions and 5 catches — because
  the earliest true line in the ladder stopped the test before it reached
  the rest. Diagnose now runs every check and lets each finding carry its
  own verdict: one placement verdict (REMOVE, SPLIT, MERGE, MOVE) plus any
  number of wording verdicts (REPLACE, RESHAPE, COMPRESS, REWORD). Ruling
  R6 bends plan D2: a section needing two placement verdicts is a SPLIT,
  with each half diagnosed and verdicted on its own, rather than the halves
  taking wording verdicts directly.
- **A ten-check table replaces the `Tested:` block and the Discuss
  template** (rulings R3–R5, plan D1). Both showed at most a bare `clean`
  for a check that ran and found nothing, which hid a skipped check; the
  table now names what each check looked at and, for a diagnosis, ends
  every row in a verdict or `clean` — never a bare one. Rows keep a fixed
  order, so a missing row is visible. Ambiguity is a new check, after
  coherence and before correctness (plan D4; pattern 6, a sentence with a
  second reading, 5 catches); pointers and names split into their own rows
  instead of hiding inside clarity (pattern 1, 15 catches: a term
  undefined, a reference that misses its target, two names for one
  thing); form gains a same-kind comparison and heading fit (pattern 4, 8
  catches); correctness now takes a worked case or a checked fact as
  evidence, alongside an observation, a ruling, or a run failure.
- **Redundancy and Responsibility run per sentence, not only per section**
  (pattern 2, 12 catches — a definition restating its own word was missed
  by a whole-section test; pattern 8/9, 5 catches — a sentence in the
  wrong section, or missing what its own question needs). COMPRESS now
  cuts an individual sentence said elsewhere or owned by another section;
  Responsibility gains REWORD or GAP for a section missing what its own
  question needs, and states where "one level down" means: a
  `references/` file beside the draft.
- **Outside files, named once at Start** (plan D5). The user may name a
  file the target relies on; redundancy, pointers and names read it, and
  no other file outside the target.
- **A Rulings list opens the ledger** (plan pattern 10, 2 catches: a
  mid-run ruling the user made was lost by a later closure). Every later
  proposal now names any ruling it bends. The ledger's `verdict` column is
  renamed `verdicts` and holds the closed set, placement verdict first.
- **Assembly's seven listed steps collapse to four**: close every HOLD and
  GAP; rerun every diagnosis check over the whole file, with correctness as
  a worked case through the draft; Verify, showing the outline and the
  description together, since the description can only be tested once the
  reassembled body exists; Compose, which now proposes moving detail past
  a 500-line ceiling (ruling R7 — the ceiling existed in an earlier design
  and was lost; restored here after a replay-set fixture flagged its
  absence).

The replay test (plan slice 4 — Haiku and Sonnet against the replay set,
scored against the new draft and, as control, the pre-change file) was
deferred to after this release, at the user's instruction.
`docs/section-by-section/state.md` carries it as the open item.

Validation for 3.4.0 is the live run itself: the user closed every section,
not a scenario run on a cheap model, and an independent judge gate reviewed
the finished draft against the target before it landed (PASS WITH FIXES, six
fixes closed). This departs from §10's blank-context-reading method and from
3.3.x's cheap-model scenario runs; the replay test above is this release's
counterpart to that measurement, run after release rather than before.

