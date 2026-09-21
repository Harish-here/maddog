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

This skill reviews one instruction file that has grown, drifted, or misbehaved.
It walks the file section by section with the user, and every section leaves the
review with exactly one verdict.

**Closure law.** The skill proposes; the user closes. A section is closed when the
user gives its verdict and approves any replacement text that verdict carries. No
verdict the user did not give reaches the ledger. Every "closed" below means this.

**Progressive disclosure law.** Keep the file minimal: each thing sits where it
is used, and detail only some runs need sits one level down.

**Tested-text law.** Text this skill proposes for the file is run over the axes
first, every axis but correctness, which needs evidence new text cannot have.
Show the result above the text, `clean` where an axis found nothing. An axis
absent from the block did not run.

```text
Tested:  redundancy — <what it caught and what changed, or `clean`>
         responsibility — <...>
         coherence — <...>
         clarity — <...>
```

## Inputs and outputs

IN — one target file per run, by path: a `SKILL.md` or an agent definition file.
A `references/` file is a target only when the user names it. Start collects the
review scope and the user's observations.
OUT — a draft of the reworked file and a verdict ledger.

## Start

Read the target whole, then post one setup message and wait for one reply. Judge
nothing until that reply lands.

The setup message carries four things:

- **Intent anchor.** One line from the frontmatter description and the user's
  observations: what this file exists to make an agent do. Once the user confirms
  or corrects it, it is fixed, and every test below is against it.
- **Section map.** A numbered list covering the file end to end, one line of
  summary each. Ids are `S1..Sn`, a SPLIT yields `S3a` and `S3b`, the frontmatter
  description is `DESC`. Split by heading. Where there are no headings, split by
  numbered step; failing those, by paragraph. Split any heading that carries its
  own named or numbered steps, or that runs past about thirty lines, by those
  steps. The user confirms the map, merges or splits entries, and names the
  review scope, whole file or named sections.
- **Paths.** The draft and the ledger. Default: the session's scratch directory;
  where the runtime has none, ask for one.
- **One question.** How the file behaved — a transcript excerpt, a failure, a
  complaint; there may be none. Ids are `O1..On`, and each proposal cites the ids
  bearing on it.

Ask whenever intent, scope or a section boundary is unclear, whenever the
description and the body disagree about what the file does, and whenever an
observation contradicts the intent anchor. Asking is always open; these three make
it obligatory.

## Markers

Three markers, which are not verdicts:

| Marker | Means | Then |
|---|---|---|
| UNREVIEWED | outside this run's review scope | a ledger row; carried into the draft unchanged and marked there |
| GAP | the intent needs an instruction no section carries | a ledger row with no section id; drafted only when the user approves text for it |
| HOLD | the user cannot decide yet | the loop goes on, and the section is still open at Assembly |

## Section loop

For each in-scope section, in file order:

```text
DIAGNOSE → DISCUSS → SETTLE → WRITE → APPROVE → RECORD → next section
you        you       user     you     user      you
           ↑           │      ↑         │
           └───────────┘      └─────────┘
           not a closure      text sent back
```

### Diagnose

First read this section against the rest of the section map, and report what
any other section already answers on the diagnosis's `Elsewhere:` line. Then go
down the axes in order and stop at the first line that describes the section.
That line's verdict is the section's verdict. Lines below it may describe the
section too; they give no verdict, and the diagnosis names them on its Also
line.

#### Redundancy
Meaning this file carries nowhere else; different wording is not different
meaning.

- The intent needs nothing this section says, or another section already says
  all of it → REMOVE.

#### Responsibility
One question → one owning section.

- It answers two questions → SPLIT. The halves re-enter the loop immediately, in
  order, before the next section.
- Another section already answers its question → MERGE into that owner. Never
  hide an ownership conflict by rewording one of the two.
- Its question is its own but it sits in the wrong place — wrong position, wrong
  file, or detail belonging one level down → MOVE, unchanged.

#### Coherence
No other section issues an order that cannot be obeyed alongside it.

- Another section's order cannot be obeyed alongside this one → name both and
  propose which one changes and with which verdict. The user closes both: the
  one that changes takes that verdict, the one that stands takes KEEP.
  Unclosed, both carry to Assembly.

#### Correctness
Following it produces the right result. Judged only on evidence: an observation,
or a failure this run hit. Never on preference.

- Evidence shows it produces the wrong result → REPLACE: a different instruction
  takes its place.

#### Clarity
Direct, self-consistent, actable without interpretation.

- Its content is a list, parallel cases, or a single rule, in a form that does
  not match → RESHAPE.
- It says its one thing in more words than it needs → COMPRESS.
- It is vague, ambiguous, or contradicts itself → REWORD: same instruction,
  clearer words.

No line above is true → KEEP.

### Discuss

Post the diagnosis, not replacement prose:

```text
Section:   <id — title (line range in the target)>
Elsewhere: <what other sections already answer that bears on this one, or `nothing`>
Does:      <what the section makes an agent do, one line>
Fails:     <axis — the reason, or `nothing` for a KEEP>
Also:      <axes below the verdict's that also fired, or drop the line>
Verdict:   <the verdict, with the MERGE partner, MOVE destination or SPLIT
            boundaries where it carries one>
Evidence:  <observation ids bearing on it, or —>
```

A coherence pair is one post: both ids on the Section line, a verdict for each
on the Verdict line.

### Settle

**A reaction is not a verdict.** The user's reply is one of five things.

- **A closure** — the verdict is given, and the section closes under the closure
  law.
- **HOLD** — the user cannot decide yet.
- **A question** — answer it, then restate the proposal against the answer and
  ask again.
- **A correction** — it may overturn the diagnosis rather than the wording.
  Restate the proposal against it and ask again.
- **Anything else** — agreement with no verdict named, a comment, a reaction.
  Restate the proposal and ask again.

### Write

At each verdict that carries text, write the replacement and show it with its
`Tested:` block. It reaches the draft once, when the user approves it. KEEP,
REMOVE and HOLD carry no text.

Where a shorter line has to be decoded, keep the longer one.

A MERGE's text is written at the partner's closure, or here when the partner is
already closed. A MOVE to another file is written into a second file beside the
draft, named for the destination file it feeds and never the draft's own path.

### Record

The ledger opens with the intent anchor, the observation ids or `none`, and the
review scope. Then one row per closure, and one per GAP:

```text
| id | title | verdict | reason | evidence | detail |
```

- `id` — the section id, or `—` for a GAP.
- `reason` — what the section closed on, the user's reason where it differs
  from the proposal's.
- `evidence` — observation ids, `this run` for a failure found during the
  review, or `—`.
- `detail` — whatever the verdict carries, as the diagnosis named it, or `—`.

Write each row at its closure, and a GAP's row when the gap is found. A gap
that later takes approved text closes and takes a second row. No
proposal is posted, and no part of the final file is composed, until the
previous closure's row exists. A section that closes
again takes a new row; a written row is never amended. The ledger records closed
decisions, not conversation.

## Assembly

Assembly changes no closed section on its own: a finding re-enters as a proposal
and the user closes it as in the loop.

Where the scope was named sections, more sections join the review here: any that
share a question, a reference, an ordering, or an overlapping instruction with a
reviewed one. Those the user closes here stop being UNREVIEWED.

The loop judged each section alone. Assembly asks whether the sections make one
file: every question owned once, nothing left unanswered, and the reader meeting
things in the order they need them.

### Close what is open
The user closes both.

1. **HOLD.** Every held section takes a verdict.
2. **GAP.** Every recorded gap takes drafted text the user approves, or stays a
   gap in the ledger.

### Resolve across sections
Run each over the whole file. Where one fires, name both sections and propose a
verdict for each. The user closes both.

3. **The cross-section axes** — responsibility, redundancy, coherence. On
   coherence, the intent anchor says which section departs.
4. **Terminology.** One thing named two ways.

### Rebuild
The agent's, except where a step says otherwise.

5. **Apply MOVE, MERGE and SPLIT.** Seat each moved section where its closure
   said, fold each merged section into its partner, keep split halves adjacent.
   Each reorder takes a MOVE row.
6. **Verify.** Against the intent anchor fixed at Start:
   - Show the outline, one line per surviving section in the proposed order.
   - Test the description against what the body now does: third person, what the
     file does and when to use it.

   Show each with its `Tested:` block. The user closes the description under
   `DESC`, then the outline, as shown or with the changes named.
7. **Compose.** Write the draft whole, in the closed order: what an agent acts
   on first at the top, prohibitions and finish conditions at the bottom,
   optional material marked. Composing writes the order and the joins: show the
   draft with its `Tested:` block. Closed text is copied as approved, never
   re-tested.

## Hand-off

Deliver the draft, the ledger, and any second file a cross-file move produced.
Name the observations no verdict cited. Then stop.

## Prohibitions

Never write to the target path. Every change lands in the draft.
