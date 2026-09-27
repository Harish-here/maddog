---
name: section-by-section
description: >
  Reviews ONE skill or agent file with the user, section by section; the
  user closes each section with one or more verdicts. Then checks the
  reassembled file against its purpose, proposes arrangement fixes, and
  produces a draft and a verdict ledger. Use when an instruction file has
  grown, drifted, or misbehaved. Not for shaping a file by how long it
  stays loaded (efficient-md, where installed), nor for authoring a new
  file (write that directly). Never edits the target.
disable-model-invocation: true
argument-hint: [path to SKILL.md or agent file]
---

This skill reviews one instruction file, the target, with the user. It first
works through the target section by section, and each section closes with one
or more verdicts. It then puts the closed sections back together. It checks
whether the whole file delivers its purpose, the intent anchor fixed at Start,
and proposes fixes to the arrangement where it does not.

**Closure law.** The skill proposes; the user closes. A section is closed when
the user gives its verdicts and approves any replacement text they carry. A gap
and the outline (Assembly step 3) are closed when the user approves their
text. No verdict the
user did not give reaches the ledger. Every "closed" below means this.

**Check-table law.** Every diagnosis, and every text this skill proposes for
the draft, including the outline and the composed draft, shows a check table
with three columns: Check, Looked at, Result.

- One row per check, every time: redundancy, responsibility, coherence,
  ambiguity, correctness, clarity, pointers, names, form, deletions. Diagnose
  defines each check. Correctness runs only on a diagnosis, because it needs
  evidence that new text cannot have. Deletions runs only on proposed text.
- `Looked at` names what the check examined: the words, the lines, the other
  section. A bare `clean` is not a result.
- Rows keep the order above, so a missing row shows. Each table has nine
  rows: a diagnosis leaves out deletions, and proposed text leaves out
  correctness.
- On a diagnosis, each finding ends in → and its verdict. On proposed text,
  each row ends in what changed. The table covers the whole text, including
  words kept from the old version, and each check reads the text against
  itself as well as the rest of the file. At Compose it covers only the
  joins, since closed text was already checked.

## Start

Read the target whole. The user gives it by path: a `SKILL.md`, an agent
file, or a file in a skill's `references/` folder when the user names that
file.

Then post one setup message. Diagnose no section until the user has answered
every item it asks about, however many replies that takes.

The setup message carries four things:

- **Intent anchor.** Ask the user, in their own words, what this file exists
  to make an agent do. Show no line of your own yet. From the reply, write
  one line and ask the user to confirm it. Once confirmed, it is fixed: it
  does not change for the rest of the run, and every check below measures
  against it.
- **Section map.** A list covering the file end to end, one line of summary
  each.
  - Ids: `S1..Sn` in file order, and `DESC` for the frontmatter description.
    A SPLIT verdict later yields `S3a` and `S3b`.
  - Divide by heading; where there are none, by numbered step; failing those,
    by paragraph. Divide further any heading that carries its own named or
    numbered steps, or runs past about thirty lines: by its steps, or else by
    paragraph.
  - The user confirms the map, joins or divides entries, and names the review
    scope: the whole file or named sections.
- **Paths.** The draft and the ledger. Default: the session's scratch directory;
  where the runtime has none, ask for one.
- **Observations and outside files.** Ask how the file behaved: a transcript
  excerpt, a failure, a complaint; there may be none. Ids are `O1..On`. Then
  ask which other files the target relies on. The redundancy, pointers and
  names checks read those files, and no other file outside the target. No
  answer means none.

Asking is always open. Ask before going on when:

- the review scope or a section boundary is unclear;
- the description and the body disagree about what the file does;
- an observation contradicts the intent anchor.

## Markers

Three markers, which are not verdicts:

| Marker | Means | Then |
|---|---|---|
| UNREVIEWED | outside this run's review scope | a ledger row, written when the scope is named, with `UNREVIEWED` in its verdicts cell; carried into the draft unchanged, under a line reading `UNREVIEWED` |
| GAP | the intent anchor needs an instruction no section carries | a ledger row |
| HOLD | the user cannot decide yet | the loop goes on, and the section is still open at Assembly |

## Section loop

For each in-scope section, in file order:

```text
DIAGNOSE → SETTLE → WRITE → APPROVE → RECORD → next section
you        user     you     user      you
  ↑          │        ↑        │
  └──────────┘        └────────┘
  not a closure       text sent back
```

Verdicts that carry no text go from SETTLE straight to RECORD.

### Diagnose

Run every check below except deletions, reading the section against the rest
of the section map, each closed section in its closed form. Each finding
carries its verdict. A section takes:

- at most one placement verdict: REMOVE, SPLIT, MERGE or MOVE;
- any number of wording verdicts: REPLACE, RESHAPE, COMPRESS, REWORD;
- KEEP alone, when no check finds anything.

REMOVE takes no wording verdict. SPLIT takes none either: each half is
diagnosed on its own and takes its own verdicts.

Post the diagnosis, with no replacement text yet, in this order:

1. A heading: `<id> — Diagnosed (<title>, <line range>)`.
2. The current text, quoted, or summarised when it runs past ten lines.
3. What the section makes an agent do, in one line.
4. The check table.
5. The verdicts, naming any MERGE partner, MOVE destination or SPLIT
   boundary, and for a clash, the other section and the change it takes.
6. The evidence: observation ids, rulings, or `this run`.
7. One question asking the user to close.

#### Redundancy
Meaning carried nowhere else, in this file or a named outside file; different
wording is not different meaning.

- The whole section is said elsewhere, or the intent anchor needs none of it
  → REMOVE.
- Some sentences are said elsewhere or not needed → COMPRESS: cut them. This
  includes a definition that repeats what its word already says. A sentence
  two sections share is cut only from the one Responsibility says does not
  own it.

A line written to stop a recorded failure is not redundant unless evidence
shows the failure is gone.

#### Responsibility
One question → one owning section. Run it per sentence.

- The section answers two questions → SPLIT. Diagnose the halves at once, in
  order, before the next section.
- Another section already answers its question → MERGE into that owner. Never
  hide an ownership conflict by rewording one of the two.
- One sentence answers another section's question → COMPRESS: cut it here.
  The owner takes it at its closure, or in this section's Write step if the
  owner is already closed.
- Its question is its own but it sits in the wrong place → MOVE; the move
  itself changes no words. A wrong place is a wrong position, a wrong file,
  or this file for detail only some runs need: that detail goes one level
  down, into a `references/` file beside the draft.
- Its own question needs something it does not say → REWORD when a phrase is
  missing, GAP when an instruction is.

#### Coherence
Every instruction here can be obeyed alongside every other section's.

- Two sections clash → name both, and propose which one changes and with
  which verdict. The user closes both. The one that stands takes no verdict
  from this finding. A section the loop has not reached yet takes its change
  when the loop reaches it; unclosed, both carry to Assembly.

#### Ambiguity
Every sentence has one reading.

- A sentence has a second reading → REWORD. The Result cell writes out the
  second reading.

#### Correctness
Following it produces the right result. Judged only on evidence: an
observation, a ruling the user made in this run, a failure this run hit, a
worked case, or a checked fact.

- Evidence shows it produces the wrong result → REPLACE: a different
  instruction takes its place. For a worked case, the Result cell shows the
  input and the wrong output; for a checked fact, what was checked and found.

#### Clarity
Direct, self-consistent, actable without interpretation.

- It says its one thing in more words than it needs → COMPRESS.
- It contradicts itself → REWORD: same instruction, clearer words.
- It asks for judgment where a concrete test exists → REWORD: state the test.

#### Pointers
Every reference reaches its target.

- A reference to a section, step, file or term does not resolve, or resolves
  to the wrong thing → REWORD: point at the real target.

#### Names
One word for one meaning, one meaning for one word.

- A term the reader cannot know is not defined at its first use, one term
  stands for two things, two terms stand for one thing, or a name is too
  narrow for its uses → REWORD.

#### Form
The shape fits the content.

- The content is a list, parallel cases, a sequence or a single rule, in a
  shape that does not match; a fence reads as a template to fill; or the
  heading does not name what the section does → RESHAPE. Compare with
  sections of the same kind in this file.

#### Deletions
Every cut from the old text is named, with why nothing needed is lost.

- A cut drops something the intent anchor needs → put it back before
  showing the text.

### Settle

**A reaction is not a verdict.** At SETTLE or APPROVE, the user's reply
closes, holds (see Markers), or does neither.

- **A closure**: the user gives the verdicts or approves the text; a yes to a
  question that names them counts. If the yes leaves a choice open, name the
  reading taken; the next reply confirms or corrects it.
- **A reopening**: the user reopens a closed section. It goes through the
  loop again from DIAGNOSE.
- **Anything else**: answer any question, then restate the proposal against
  the reply and ask again. A correction may overturn the diagnosis, not only
  the wording. One that applies beyond this section is a ruling: add it to the
  Rulings list when made.

### Write

At each verdict that carries text, write the shortest text that needs no
decoding. KEEP, REMOVE and a MOVE within the file carry none. A KEEP section
enters the draft as it stands when it closes. A SPLIT carries none itself;
its halves enter at their own closures. A MERGE's text is written at the
partner's closure, or here when the partner is already closed.

Post it in this order:

1. A heading: `<id> — Proposed`.
2. The text.
3. The check table.
4. One question asking the user to approve.

The text reaches the draft once, when the user approves it. A MOVE to another
file is written into a second file beside the draft, named for the destination
file it feeds and never the draft's own path.

### Record

The ledger opens with the intent anchor, the observation ids, the named
outside files, the review scope, and a Rulings list (`R1..Rn`, empty at the
start). Every later proposal names any ruling it bends.

Then a row for each closure, each GAP found and each UNREVIEWED section,
written before the next proposal or Assembly step:

```text
| id | title | verdicts | reason | evidence | detail |
```

- `id`: the section id, or `—` for a GAP.
- `verdicts`: the placement verdict first.
- `reason`: why it closed, in the user's words where they differ.
- `evidence`: observation ids, ruling ids, or `this run`.
- `detail`: what the verdicts carry, or `—`.

A gap that closes, or a section that closes again, takes a new row; a written
row is never amended.

## Assembly

Assembly asks whether the closed sections, put back together, deliver the
intent anchor: every question owned once, nothing left unanswered, and an
arrangement in which the reader meets each thing when they need it.

It changes no closed section on its own: a finding re-enters as a proposal,
and the user closes it as in the loop.

Where the scope was named sections, more sections join here: any that share a
question, a reference or an overlapping instruction with a reviewed one, or
must be read before it or after it. A section the user closes here loses its
`UNREVIEWED` line.

1. **HOLD and GAP.** Every held section takes its verdicts. Every open gap
   takes proposed text the user approves, or stays a gap in the ledger.

2. **Every diagnosis check, over the whole file.** Resolve each finding as in
   the loop; in a clash, the intent anchor says which section departs.
   Correctness here is a worked case run through the draft from start to
   finish.

3. **Verify.** Against the intent anchor:
   - Show the outline: one line per surviving section, in the proposed
     arrangement: what an agent acts on first at the top, prohibitions and
     finish conditions at the bottom.
   - Check the description against what the body now does: third person,
     what the file does and when to use it.

   Show each with its check table. The user closes the description under
   `DESC`, then the outline, as shown or with the changes named. The outline
   places each MOVE closed in the loop where its closure said; a reorder the
   user closes here takes a MOVE row.

4. **Compose.** Write the draft whole, in the closed arrangement. Closed text
   is copied as approved; only the joins between sections are new. Every file
   this run produces stays under 500 lines: when the body passes it, propose
   moving detail only some runs need one level down (see Responsibility); when
   a `references/` file passes it, propose splitting that file. Compose again
   once those proposals close. Show the draft with a check table that covers
   the joins.

## Hand-off

Deliver the draft, the ledger, and any second file a MOVE to another file
produced. Name the observations no verdict cited. Then stop.

## Prohibitions

Never write to the target path. Every change lands in the draft.
