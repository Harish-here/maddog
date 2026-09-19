---
name: section-by-section
description: >
  Reviews ONE existing skill or agent file section by section with the
  user, who closes every section with one verdict, producing a draft of
  the reworked file and a verdict ledger. Use when an instruction file
  has grown, drifted, repeated itself, or misbehaved and the user wants
  to decide section by section what stays. Not for shaping a file by how
  long it stays loaded — that is a separate formatting pass. Not for
  authoring a new file — write that directly. Never edits the target.
disable-model-invocation: true
argument-hint: [path to SKILL.md or agent file]
---

**Closure law.** The skill proposes; the user closes. A section is closed when the
user gives its verdict and approves any replacement text that verdict carries. No
verdict the user did not give reaches the ledger. Every "closed" below means this.

## Contract

IN — one target file per run, by path: a `SKILL.md` or an agent definition file; the
review scope, whole file or named sections; and the user's observations of how it
behaved, optional. A `references/` file is a target only when the user names it.
OUT — a draft of the reworked file and a verdict ledger, at paths named before the
loop starts.

## Verdicts

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
| HOLD | the user cannot decide yet | the loop goes on, and the section is still open at Assembly |
| GAP | the intent needs an instruction no section carries | a ledger row with no section id; never drafted |
| UNREVIEWED | outside this run's review scope | a ledger row; carried into the draft unchanged and marked there |

## Start

1. **Read the target whole.** The step-4 map must cover it end to end, which is the
   proof it was read.
2. **Observations.** Ask once how the file behaved — a transcript excerpt, a
   failure, a complaint; there may be none. Ids are `O1..On`, and each proposal
   cites the ids bearing on it.
3. **Intent anchor.** One line from the frontmatter description and the
   observations: what this file exists to make an agent do. The user confirms or
   corrects it, and it is not reopened later. Every test below is against it.
4. **Section map.** Split by headings; failing those, numbered steps; failing those,
   paragraphs. Show it as a numbered list, one line of summary each. Ids are
   `S1..Sn`, a SPLIT yields `S3a` and `S3b`, the frontmatter description is `DESC`.
   The user confirms the map, merges or splits entries, and names the review scope.
5. **Paths.** Name the draft and ledger paths. Default: the session's scratch
   directory; where the runtime has none, ask the user for one.

Ask whenever intent, scope or a section boundary is unclear, whenever the
description and the body disagree about what the file does, and whenever an
observation contradicts the intent anchor. Asking is always open; these three make
it obligatory.

## Section loop

For each in-scope section, in file order.

**Check three things.** Redundancy — meaning this file carries nowhere else;
different wording is not different meaning. Clarity — direct, self-consistent,
actable without interpretation. Responsibility — one question → one owning section.

**Diagnose.** The three checks feed one ordered test. More than one line may be true
of a section; the earliest true line gives the verdict, and it is the only one.

1. Redundancy — the intent needs nothing this section says → REMOVE.
2. Responsibility — it answers two questions → SPLIT; the halves re-enter the loop
   immediately, in order, before the next section.
3. Responsibility — the intent needs what it says, but another section already
   answers its question → MERGE into that owner. Never hide an ownership conflict
   by rewording one of the two.
4. Responsibility — the question is its own but it sits in the wrong place: wrong
   position, wrong file, or detail that belongs one level down → MOVE.
5. Clarity — its content is a list, parallel cases, or a single rule, in a form that
   does not match → RESHAPE; a fitting shape usually fixes length and clarity too.
6. Clarity — it says its one thing in more words than it needs → COMPRESS.
7. Clarity — it is vague, ambiguous, or contradicts itself → REWORD; a contradiction
   with another section is Assembly's unless the local correction is unambiguous.
8. Otherwise → KEEP.

**Discuss.** Post the diagnosis, not replacement prose:

    S4 — Return format (lines 61–74)
    Does: tells the agent how to shape its return message.
    Fails: responsibility, test 3 — S9 already answers how the return is shaped.
    Verdict: MERGE into S9. Evidence: O1.

`Fails` names the check and the numbered test behind the verdict, or `nothing` for
KEEP; `Evidence` reads `—` where no observation bears on the section. A MOVE carries
its destination, a MERGE its partner id, a SPLIT the two boundaries.

**Interpret.** A reaction is not a verdict, and a correction may overturn the
diagnosis rather than the wording. Where the reply is not a closure, restate the
proposal against it and ask again.

**Settle.** The user closes the section under the closure law, or gives it HOLD.

**Draft once.** At closure, write that section's replacement text into the draft,
once; KEEP, REMOVE and HOLD carry none. A MERGE's text is drafted at the partner's
closure, or here when the partner is already closed. A MOVE to another file is
drafted into a second file beside the draft, named for the destination file it feeds
and never the draft's own path.

**Close the ledger.** The ledger opens with the intent anchor and the observation
ids, or `none`, then one row per closure. Write each row at its closure: no proposal is
posted, and no artifact is composed, until the previous closure's row exists.
`reason` is what the section closed on, the user's reason where it differs from
the proposal's; `detail` carries the MOVE destination, MERGE partner, SPLIT halves, or
`—`. The ledger records closed decisions, not conversation.

| id | title | verdict | reason | evidence | detail |
|---|---|---|---|---|---|
| S4 | Return format | MERGE | S9 already answers how the return is shaped | O1 | partner S9 |
| — | Escalation | GAP | O2 names a failure no section covers | O2 | — |

## Assembly

Assembly changes no closed section on its own: where a step below needs one changed,
post it as a proposal and the user closes it as in the loop, with its own ledger row.
Assembly writes no instruction the user has not closed. Where the scope was named
sections, the affected context joins it here — sections sharing a question, a
reference, an ordering, or an overlapping instruction with a reviewed one; any the
user closes here stops being UNREVIEWED.

1. **Resolve every HOLD.** The user closes each held section.
2. **Resolve ownership.** One question, one owning section, file-wide. Two owners →
   the user closes which one keeps it.
3. **Resolve cross-section redundancy.** Meaning repeated between sections that each
   survived their own closure → the user closes which one carries it.
4. **Resolve contradictions.** Two closed sections that cannot both be obeyed → the
   user closes which one departs from the intent anchor.
5. **Apply MOVE, MERGE and SPLIT.** Seat each moved section at the destination its
   closure recorded, fold each merged section into its partner, keep split halves
   adjacent. Record each reorder as a MOVE row.
6. **Verify intent and flow.** Against the intent anchor fixed at Start, show the
   outline — one line per surviving section, in the proposed order — and test the
   frontmatter description against what the reworked body now does. The user closes
   the description's verdict and text as a section's, under `DESC`, then closes the
   outline — the order as shown, or with the changes named.
7. **Compose the final artifact.** Write the draft whole, in the closed order:
   instructions acted on first at the top, prohibitions and finish conditions at the
   bottom, optional material marked. Hold it under a body ceiling — the one the
   efficient-md skill states for skill bodies where that skill is installed,
   otherwise a few hundred lines — forking the heaviest detail, long examples and
   tables first, one level down into a `references/` file drafted beside the draft.

## Hand-off

Deliver, then stop: the draft, the ledger and the target, named as the evidence set
for an independent review; observations no verdict cited; verdict counts and the
line count before and after; every GAP and every UNREVIEWED section.

## Prohibitions

- Never write to the target path. Every change lands in the draft.
- Never judge a section before Start closes.
- Never dispatch the independent review, and never name a specific one: this file
  ships outside the repo it was written in, so it may cite only what ships alongside
  it.
