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
one verdict from a fixed vocabulary. A run produces a draft of the reworked file
and a verdict ledger, and never edits the target. Draft, ledger and target are
the evidence set for an independent review the skill does not run.

Protects PHILOSOPHY.md point 3 above all — the skill has no authority to decide
what an instruction file says, so the file grants it none — and points 1, 2 and
6: the user sees a compressed proposal per section, the ledger is the durable
record of what was decided, and every section must earn its place.

## 2. The closure law

The rule the file exists to carry, and the reason it sits in the premium slot:

> The skill proposes; the user closes. A section is closed when the user gives
> its verdict and approves any replacement text that verdict carries. No verdict
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
- the target's frontmatter description, closed last, at Assembly
- the user's observations of how the target behaved — asked once, optional

Out of scope:

- authoring a new file: an intent no section carries is a GAP, recorded and
  never drafted
- a `references/` file, unless the user names it as the target of its own run
  (SBS-GATE-1 F1)
- applying the draft to the target, or dispatching the independent review
- running without the user: the user closes every section

## 4. Flow

The body is readable as this flow and carries no stage outside it.

```text
START           read target whole → observations → intent anchor →
                section map → draft and ledger paths
  │
  ▼
SECTION LOOP    for each in-scope section, in file order:
                check (redundancy · clarity · responsibility) →
                diagnose → discuss → interpret → settle →
                draft once → close ledger
  │
  ▼
ASSEMBLY        resolve holds → ownership → cross-section redundancy →
                contradictions → apply MOVE/MERGE/SPLIT →
                verify intent and flow → compose the final artifact
  │
  ▼
HAND-OFF
```

Two blocks sit outside the flow because they are framing, not stages: the
closure law and the Contract above START, the Prohibitions below HAND-OFF.

Two stages of the 3.1.0 design survive as steps rather than stages:

- **Description last** is Assembly's *verify intent and flow* step. The
  description can only be tested against a reworked body that exists, and that
  body first exists at Assembly.
- **Arrange** is Assembly's outline, shown and closed by the user before the
  artifact is composed.

## 5. Verdicts, markers, and the ordered test

Eight verdicts, one per section.

| Verdict | Means |
|---|---|
| KEEP | unchanged |
| REMOVE | deleted |
| COMPRESS | same instruction, fewer words |
| REWORD | same instruction, clearer words |
| RESHAPE | same content, a form that fits it |
| MOVE | relocated unchanged |
| MERGE | folded into a named partner, which keeps the question |
| SPLIT | two sections, each closing on its own verdict |

Three markers, which are not verdicts:

| Marker | Means | Then |
|---|---|---|
| HOLD | the user cannot decide yet | the loop goes on; still open at Assembly |
| GAP | the intent needs an instruction no section carries | a ledger row with no section id; never drafted |
| UNREVIEWED | outside this run's review scope | a ledger row; carried into the draft unchanged and marked there |

Every verdict has a trigger, and the triggers are one ordered test inside
Diagnose. More than one line may be true of a section; the earliest true line
gives the verdict, and it is the only one. Each line names the check that
produced it, so a proposal's `Fails` line records the check as well as the test
number — which is what makes the three checks observable rather than internal.

1. Redundancy — the intent needs nothing this section says, or another
   section already says all of it → REMOVE.
2. Responsibility — it answers two questions → SPLIT.
3. Responsibility — the intent needs what it says, but another section already
   answers its question → MERGE into that owner.
4. Responsibility — the question is its own but it sits in the wrong place →
   MOVE.
5. Clarity — content in a form that does not match it → RESHAPE.
6. Clarity — it says its one thing in more words than it needs → COMPRESS.
7. Clarity — vague, ambiguous, or self-contradicting → REWORD.
8. Otherwise → KEEP.

Precedence, and why each rank is where it is:

- **REMOVE first**, but its trigger is "the intent needs nothing this section
  says", NOT "the intent survives without this section". The looser form is true
  of every duplicated section, which makes MERGE unreachable — the defect a
  blank-context reader hit on round 2 of this design.
- **SPLIT before MERGE and MOVE**: a two-job section must become two sections
  before either half can be placed.
- **MERGE before MOVE**: a question that already has an owner is folded, not
  relocated.
- **RESHAPE before COMPRESS and REWORD**: a fitting shape usually fixes length
  and clarity on the way.
- **COMPRESS before REWORD**: both are true of many sections, and the order makes
  the verdict deterministic rather than a matter of taste.

## 6. Artifacts

- **Draft.** The full reworked file, at a path named at START, defaulting to the
  session's scratch directory; where the runtime has none, the user is asked for
  a path (SBS-GATE-1 F15). Never the target path.
- **MOVE-destination draft.** Where a MOVE targets another file, that file is
  drafted beside the draft, named for the destination file it feeds and never the
  draft's own path, so it collides with neither the draft nor an existing file
  (SBS-GATE-1 F5).
- **Ledger.** A markdown table with a header separator, opening with the intent
  anchor and the observation ids, then one row per closure, each row written at
  its closure. No proposal is posted and no artifact composed until the previous
  closure's row exists — the structure that makes the ledger unskippable and lets
  a pass resume mid-file.

  | id | title | verdict | reason | evidence | detail |
  |---|---|---|---|---|---|
  | S4 | Return format | MERGE | S9 already answers how the return is shaped | O1 | partner S9 |
  | — | Escalation | GAP | O2 names a failure no section covers | O2 | — |

  Ids are `S1..Sn`; a SPLIT yields `S3a` and `S3b`; the frontmatter description is
  `DESC`; a GAP row carries no section id (SBS-GATE-3 F21 and its erratum).
  `reason` is what the section closed on — the user's reason where it differs
  from the proposal's. `detail` carries the MOVE destination, the MERGE partner,
  the SPLIT halves, or `—`.
- **Closing report.** Observations no verdict cited, verdict counts, line count
  before and after, every GAP, every section still UNREVIEWED, and the hand-off
  line naming draft, ledger and target as the evidence set.

## 7. Prohibitions

- Never write to the target path.
- Never judge a section before START closes.
- Never dispatch the independent review, and never name a specific one: the file
  ships outside this repo, so it may cite only what ships alongside it.

Everything the 3.1.0 body also listed as a prohibition — never close a section
without the user, never draft a GAP, one target file per run — is stated once, in
the section that owns the question, and is not repeated at the bottom. A
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
`argument-hint: [path to SKILL.md or agent file]`. The description is 483
characters, under the 500-character target in
`.claude/skills/review-agent/references/description-standard.md` §3, and carries
a claim, a "Use when" trigger sentence, two redirects (against shaping a file by
how long it stays loaded, and against authoring a new file) and the never-edits
invariant. It carries no procedure: an agent that acts on a description without
loading the body must not be able to run the ritual from it.

Body order: closure law, Contract, Verdicts, Start, Section loop, Assembly,
Hand-off, Prohibitions. The body names capabilities (read, write a draft), never
runtime tool identifiers (CLAUDE.md invariants; PHILOSOPHY.md point 5), and cites
`efficient-md` only in the form guarded by "where that skill is installed"
(SBS-GATE-1 F4, and efficient-md's own SHIP RULE).

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
  from the skill. The `Fails` line, naming the check and test that produced each
  proposal, is the closest available trace.

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
  Diagnose is "axes below" the one that gave the verdict. Two runs filed an axis
  above the verdict's, asserting a check had fired that had not.

Validation: scenario runs on a cheap model, cut at the point where the agent
must post a diagnosis.

- The `Elsewhere:` line appeared in every run, eleven of eleven, and named the
  overlapping section each time.
- A fully duplicated section drew REMOVE in four of four.
- Partial overlap drew MERGE in four of five. The fifth reported the overlap on
  the `Elsewhere:` line and then took a clarity verdict, the fallthrough this
  line exists to expose. Two control runs against the same file with the line in
  a different position split the same way, so the split belongs to the fixture
  and the model, not to the change.
- The Also line's new wording is validated negatively only. Across the nine runs
  carrying it, no run filed an axis above the verdict's, which is the misfiling
  it targets; no run filed an Also line at all, so no run exercised it in the
  case where it should appear.

