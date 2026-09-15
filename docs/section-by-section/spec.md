# section-by-section — design spec

Date: 2026-09-15. Status: approved; authored through the author-agent
CREATE (skill) loop (verdicts SBS-GATE-1..3). Binding design artifact.

## 1. Purpose

A shipped skill (`skills/section-by-section/SKILL.md`) that reviews ONE
existing skill or agent file with the user, one section at a time. Each
section is tested against the file's stated intent and closed by the user
with one verdict from a fixed vocabulary. The skill produces a draft of the
reworked file and a verdict ledger. It never edits the target. The draft is
the input to an independent review that the skill does not run.

Protects PHILOSOPHY.md points 1 (judgment spent on decisions: the user
decides, the skill proposes), 2 (the ledger is the record of accepted
findings, reused by the later authoring pass), 4 (the user sees a compressed
proposal per section, never raw uncertainty), and 6 (every section must earn
its place).

## 2. Scope

In scope:

- one target file per run: a `SKILL.md` or an `agents/*.md` file, by path
- the target's frontmatter description, reviewed last
- observations of how the target performed, supplied by the user at the start

Out of scope:

- authoring a new file (a GAP is recorded, never drafted)
- a `references/` file, unless the user names it as the target of its own run
- applying the draft to the target, or dispatching the independent review
- running unattended: the user closes every section

## 3. Verdict vocabulary (locked)

Eight verdicts. One per section. The right-hand column is the sentence the
user would naturally say; it is the test for choosing between them.

| Verdict | Meaning | The user says |
|---|---|---|
| KEEP | unchanged | "This earns its place as is." |
| REMOVE | deleted | "Intent survives without this." |
| COMPRESS | same instruction, fewer words | "Say it once." |
| REWORD | same instruction, clearer words | "Too vague to act on." |
| RESHAPE | same content, a form that matches it (prose to bullets, cases to a table, a buried rule to one sentence) | "That's a list." |
| MOVE | relocated, unchanged; destination is a position in the file or another file | "Right rule, wrong place." / "Keep it, but out of the body." |
| MERGE | folded into a named partner section | "Keep one, fold the other in." |
| SPLIT | becomes two sections, each re-entering the loop for its own verdict | "These are two different things." |

Two markers that are not verdicts:

| Marker | Meaning | Rule |
|---|---|---|
| HOLD | user cannot decide yet | resolved with the user at Arrange, before the draft is assembled |
| GAP | intent needs an instruction no section carries | a ledger row with no section; listed in the hand-off; never drafted |

## 4. Inputs

- **Target.** One file path. Read whole before anything is judged.
- **Observations (optional).** Notes on how the target performed: a transcript
  excerpt, a failure, a complaint. Asked for once at the start; each gets an
  id `O1..On`. Every proposal cites the observation ids that support it. An
  observation no verdict cites is reported at the end as unaddressed.
- **Intent anchor.** One line derived from the frontmatter description and
  the observations. The user confirms or corrects it before section one. A
  wrong anchor spoils the pass, so nothing is judged before it is confirmed.
- **Section map.** Proposed by the skill: split by headings; where none, by
  numbered steps; where none, by paragraphs. Shown as a numbered list with a
  one-line summary per section, so the user sees the whole file before
  closing anything. The user may merge or split entries before the walk
  starts. Section ids are `S1..Sn`; a SPLIT yields `S3a`, `S3b`.
- **Paths.** Draft and ledger paths are named at the start. Default: the
  session scratch directory. The user may name a durable path when the pass
  should outlive the session.

## 5. Per-section tests

Run in this order. The verdict follows from the first test that fails.

1. **Removal test.** Would an agent reading the file without this section
   still act on the intent? Yes → REMOVE.
2. **Duplicate test.** Does another section already carry this instruction?
   Yes → MERGE (fold into the partner) or MOVE (relocate, when the section is
   the better home). Two sections doing two jobs each → SPLIT first.
3. **Format test.** Is the content a list, a set of parallel cases, or a
   single rule, in a form that does not match? Yes → RESHAPE. RESHAPE
   outranks COMPRESS and REWORD: a new shape usually fixes length and
   clarity on the way.
4. **Weight test.** Needed but longer than its instruction → COMPRESS.
   Needed but unclear or ambiguous → REWORD. Two sections that contradict
   each other → REWORD the one that departs from the intent, naming the
   other.
5. Otherwise KEEP.

## 6. Flow

### 6.1 Open

1. Read the whole target.
2. Ask once for observations. Assign `O` ids.
3. State the intent anchor. User confirms or corrects.
4. Show the section map with one-line summaries. User confirms, merges, or
   splits entries.
5. Name the draft and ledger paths.

Nothing is judged before step 5 closes.

### 6.2 Walk

For each section in file order:

1. Run the tests of section 5.
2. Post a proposal in the fixed shape:

   ```
   S4 — Return format (lines 61–74)
   Does: tells the agent how to shape its return message.
   Fails: duplicate test — S9 carries the same rule with the envelope fields.
   Verdict: MERGE into S9. Evidence: O1.
   Draft: (none for MERGE; S9's closure carries the merged text)
   ```

   For COMPRESS, REWORD, and RESHAPE the proposal carries the replacement
   text. For MOVE it carries the destination. For MERGE it carries the
   partner id; the merged text is drafted at the partner's closure, or at
   this closure if the partner is already closed. For SPLIT it carries the
   two new sections' boundaries and summaries.
3. Discuss. The user closes with the final verdict, and approves the
   replacement text on the spot where the verdict carries one. Only the
   user's closure counts.
4. Write the ledger row at every closure.

Rules inside the walk:

- HOLD is allowed; the walk continues.
- A SPLIT's two halves re-enter the loop immediately, in order.
- A closed section reopens only on new evidence (a later section, a new
  observation, the Arrange step).
- The advisor never closes a section on the user's behalf, whatever the
  round count.

### 6.3 Description last

After the last body section closes, test the frontmatter description
against what the reworked body actually does, with the same vocabulary. It
is the anchor during the walk, so it is not judged against itself mid-pass.
The user closes its verdict as for a section; its ledger row carries the
reserved id `DESC`, which cannot collide with `S1..Sn` or a split's `S3a`.

### 6.4 Arrange

1. Show the outline: one line per surviving section in the proposed new
   order.
2. Apply the ordering rules for a file an agent acts on top to bottom: the
   instructions acted on first sit at the top; prohibitions and finish
   conditions sit at the bottom; optional material is marked; the whole
   stays under the warm ceiling the efficient-md skill states for skill
   bodies.
3. Resolve every HOLD.
4. Record every reorder as a MOVE row and every gap as a GAP row.
5. The user closes the arrangement.

### 6.5 Assemble and hand off

1. Write the draft file. When a MOVE targets another file, write that file
   too, beside the draft, never at any existing path.
2. Write the final ledger.
3. Report: unaddressed observations; counts per verdict; line count before
   and after.
4. Deliver the hand-off line: the draft, the ledger, and the target are the
   evidence set for an independent review. The skill does not name or
   dispatch that review. In this repo it is the author-agent loop.

## 7. Outputs

- **Draft file(s).** Full reworked text. Never written to the target path.
- **Ledger.** Markdown table, one row per section, written after every
  closure so the pass survives context loss and can resume mid-file:

  ```
  | id | title | verdict | reason | evidence | detail |
  | S4 | Return format | MERGE | duplicate of S9 | O1 | partner S9 |
  | — | Escalation | GAP | O2 names a failure no section covers | O2 | — |
  ```

  `detail` carries the MOVE destination, MERGE partner, or SPLIT children.
  A GAP row has no section id; the description's row uses `DESC`.
  The ledger is the accepted-findings record for the later authoring pass.
- **Closing report.** Unaddressed observations, verdict counts, line counts,
  hand-off line.

## 8. Prohibitions

- Never write to the target path.
- Never close a section without the user.
- Never draft text for a GAP.
- Never dispatch the independent review, and never name a specific one:
  the file ships outside this repo, so it may cite only what ships with it.
- One target file per run.
- Never judge a section before the intent anchor and section map are
  confirmed.

## 9. The skill file

Path: `skills/section-by-section/SKILL.md`. Residency class: WARM (loaded
per invocation). Ceiling: ~150 lines. No `references/` at first; if the
exemplar and ledger format push the body past the warm ceiling, the ledger
format forks to `references/ledger.md`.

Frontmatter:

```yaml
name: section-by-section
description: >
  Reviews ONE existing skill or agent file section by section with the
  user, testing each section against the file's stated intent and closing
  it with one of eight verdicts (KEEP, REMOVE, COMPRESS, REWORD, RESHAPE,
  MOVE, MERGE, SPLIT). Produces a draft file and a verdict ledger for an
  independent review; never edits the target. Use when an existing
  instruction file has grown, drifted, or misbehaved and the user wants to
  decide section by section what stays. Do NOT use to author a new file,
  to review a file without the user present, or to apply the result.
disable-model-invocation: true
argument-hint: [path to SKILL.md or agent file]
```

`disable-model-invocation: true` because this is a long interactive ritual;
auto-triggering it on "review this skill" would hijack a quick review. The
final description text is authored against
`.claude/skills/review-agent/references/description-standard.md` in the
author-agent loop; the text above is the brainstorm draft.

Body order (premium slots at top and bottom per the WARM class):

1. Contract: in, out, never. Then the verdict table from section 3.
2. Open (6.1).
3. Walk (6.2), with the one canonical proposal exemplar.
4. Description last (6.3).
5. Arrange (6.4).
6. Assemble and hand off (6.5), with the ledger row format.
7. Prohibitions (section 8).

The body names capabilities (read, write a draft), never runtime tool
identifiers (CLAUDE.md invariants; PHILOSOPHY.md point 5).

## 10. Validation

There is no test suite (CONTRIBUTING.md §Validation). The skill is validated
by exercising it:

- Run it on one shipped file of each kind: one `skills/*/SKILL.md` and one
  `agents/*.md`, with at least one observation supplied. Confirm the draft
  and ledger land at the named paths and the target is byte-identical
  afterwards.
- Confirm every scenario in the brainstorm table maps to its verdict when
  encountered: preamble → REMOVE; duplicated rule → MERGE; buried rule →
  MOVE; heavy example → MOVE to a references file; paragraph-list → RESHAPE;
  two-job section → SPLIT; uncovered observation → GAP; undecided → HOLD then
  resolved at Arrange; vague wording → REWORD; rule said thrice → COMPRESS.
- Since invocation is slash-only, no fresh-session routing probe is needed
  for auto-triggering; probe only that the name resolves.

## 11. Shipping

SHIPPED surface: `skills/` changes, so the `release` skill applies before
merge. The shipped set changes, so `.claude-plugin/plugin.json` bumps to
3.1.0 and `CHANGELOG.md` and `README.md` §Skills gain an entry.

## 12. Decisions taken in the brainstorm

| Decision | Choice | Alternative rejected |
|---|---|---|
| Location | shipped `skills/` | internal `.claude/skills/` feeding author-agent directly |
| Draft timing | at section closure | one rewrite pass after the walk |
| Judge in the pass | none; hand-off names the evidence set | judge-first scoring; mandatory judge before writing |
| Output | draft + ledger, target untouched | in-place edit on approval |
| Vocabulary | eight verdicts + HOLD/GAP | six verdicts with MERGE and SPLIT folded into MOVE and REWORD |
| Invocation | slash-only | auto-trigger on description |
