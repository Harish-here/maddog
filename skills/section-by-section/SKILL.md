---
name: section-by-section
description: >
  Reviews ONE existing skill or agent file section by section with the
  user, who closes each with one of eight verdicts against the file's
  stated intent, producing a draft and a verdict ledger. Use when an
  instruction file has grown, drifted, or misbehaved and the user wants
  to decide what stays. Not for shaping a file by how long it stays
  loaded — that is a separate formatting pass. Not for authoring a new
  file — write it directly. Never edits the target; the draft and ledger
  hand off to a review it does not run.
disable-model-invocation: true
argument-hint: [path to SKILL.md or agent file]
---

One existing instruction file, one section at a time. The skill proposes;
the user closes every section, whatever the round count.

## Contract

IN — one target file per run, by path: a `SKILL.md` or an agent definition
file. Plus the user's observations of how it behaved, optional, asked for
once. A `references/` file is a target only when the user names it as one.
OUT — a draft of the reworked file and a verdict ledger, at paths named
before the walk starts.
NEVER — never write to the target path. Every change lands in the draft.

Eight verdicts, one per section. The right-hand column is the sentence the
user would naturally say; it is the test for choosing between them.

| Verdict | Meaning | The user says |
|---|---|---|
| KEEP | unchanged | "This earns its place as is." |
| REMOVE | deleted | "Intent survives without this." |
| COMPRESS | same instruction, fewer words | "Say it once." |
| REWORD | same instruction, clearer words | "Too vague to act on." |
| RESHAPE | same content, a form that matches it — prose to bullets, cases to a table, a buried rule to one sentence | "That's a list." |
| MOVE | relocated, unchanged; destination is a position in this file or another file | "Right rule, wrong place." / "Keep it, but out of the body." |
| MERGE | folded into a named partner section | "Keep one, fold the other in." |
| SPLIT | two sections, each re-entering the loop for its own verdict | "These are two different things." |

Two markers that are not verdicts:

| Marker | Meaning | Rule |
|---|---|---|
| HOLD | the user cannot decide yet | resolved with the user at Arrange, before the draft is assembled |
| GAP | intent needs an instruction no section carries | a ledger row with no section; listed in the hand-off; never drafted |

## Open

1. Read the whole target. Nothing is judged before step 5 closes.
2. Ask once for observations — a transcript excerpt, a failure, a complaint;
   there may be none. Give each an id `O1..On`. Every proposal cites the ids
   supporting it where any exist; uncited ones are reported as unaddressed.
3. State the intent anchor: one line drawn from the frontmatter description
   and the observations. The user confirms or corrects it.
4. Show the section map — split by headings; failing those, by numbered steps;
   failing those, by paragraphs. A numbered list, one line of summary each. Ids
   are `S1..Sn`; a SPLIT yields `S3a`, `S3b`. The user confirms, merges, splits.
5. Name the draft and ledger paths. Default: the session's scratch directory;
   where the runtime has none, ask the user for one. The user may name a
   durable path when the pass should outlive the session.

## Walk

For each section in file order, run these tests in order. The verdict
follows from the first test that fails.

1. REMOVAL — would an agent reading the file without this section still act
   on the intent? Yes → REMOVE.
2. DUPLICATE — does another section already carry this instruction? Yes →
   MERGE (fold into the partner) or MOVE (relocate, where this section is
   the better home). Two sections doing two jobs each → SPLIT first.
3. FORMAT — is the content a list, a set of parallel cases, or a single rule in
   a form that does not match? Yes → RESHAPE, outranking COMPRESS and REWORD.
4. WEIGHT — needed but longer than its instruction → COMPRESS. Needed but
   unclear or ambiguous → REWORD. Two sections that contradict each other →
   REWORD the one that departs from the intent, naming the other.
5. Otherwise KEEP.

Then post the proposal in this fixed shape:

    S4 — Return format (lines 61–74)
    Does: tells the agent how to shape its return message.
    Fails: duplicate test — S9 carries the same rule with the envelope fields.
    Verdict: MERGE into S9. Evidence: O1.
    Draft: (none for MERGE; S9's closure carries the merged text)

COMPRESS, REWORD and RESHAPE carry the replacement text; MOVE the destination;
MERGE the partner id, whose closure drafts the merged text (or this one if the
partner is closed); SPLIT the two halves' boundaries and summaries. Evidence
reads `—` where no observation bears on the section.

Then close the section:

1. Discuss. The user closes with the final verdict and approves the replacement
   text on the spot where a verdict carries one. Only the user's closure counts.
2. Write the ledger row. The next section's proposal is not posted until the
   previous closure's row is written.

Inside the walk: HOLD is allowed and the walk continues; a SPLIT's two
halves re-enter the loop immediately, in order; a closed section reopens
only on new evidence — a later section, a new observation, or Arrange.

## Description last

After the last body section closes, test the frontmatter description against
what the reworked body now does, with the same vocabulary. Its verdict and
any replacement text are the user's to close, exactly as a section's are, and
its closure writes a ledger row under the reserved id `DESC`.

## Arrange

1. Show the outline: one line per surviving section, in the proposed new order.
2. Order a file an agent acts on top to bottom: instructions acted on first at
   the top, prohibitions and finish conditions at the bottom, optional material
   marked, the whole inside a body ceiling — the one the efficient-md skill
   states for skill bodies where that skill is installed, otherwise a few
   hundred lines, with heavier detail forked one level down into `references/`.
3. Resolve every HOLD: the user closes each held verdict, as in the walk.
4. Record every reorder as a MOVE row, and every gap as a GAP row.
5. The user closes the arrangement, once every closure above has its ledger row.

## Assemble and hand off

1. Write the draft: the full reworked text. Where a MOVE targets another file,
   write that file too — beside the draft, never at any existing path, under a
   name derived from its destination so it cannot collide with the draft.
2. Write the final ledger — a markdown table, one row per section, written
   after every closure so the pass survives context loss and resumes mid-file;
   every closure above has its row before this section starts, HOLDs included.
   `detail` carries the MOVE destination, MERGE partner, or SPLIT children.

       | id | title | verdict | reason | evidence | detail |
       |---|---|---|---|---|---|
       | S4 | Return format | MERGE | duplicate of S9 | O1 | partner S9 |
       | S7 | Escalation | GAP | O2 names a failure no section covers | O2 | — |

3. Report: unaddressed observations, counts per verdict, and the line count
   before and after.
4. Hand off: the draft, the ledger and the target are the evidence set for
   an independent review. Name them; do not run it.

## Prohibitions

- Never write to the target path.
- Never close a section without the user, the description included.
- Never draft text for a GAP.
- Never dispatch the independent review, and never name a specific one:
  this file ships outside the repo it was written in, so it may cite only
  what ships alongside it.
- One target file per run.
- Never judge a section before Open closes: the intent anchor, the section
  map, and the draft and ledger paths are all confirmed.
