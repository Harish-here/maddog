# Why these rules

Read only when changing this skill. A writer never needs this file.

Sections: the model; what the main file holds; why a size sentence;
evidence of 2026-11-10; evidence of 2026-11-13; why brief and report
mirror each other; evidence of 2026-11-16 for spec and for instruction
file; where the sizes come from; published sources.

## The model

The cost of a text is its words multiplied by its loads. A writer can cut
words, move words to a place that loads less often, or point to text the
reader can already reach. Every recipe applies those three moves to one
kind of text.

An earlier version sorted texts into four classes by how long they stay
loaded. Load frequency alone could not tell a writer how to write: a
skill description and an instruction file load equally often and need
different recipes. The kind of text now picks the recipe, and each
recipe's opening line says who loads it.

Rules of the earlier version left out on purpose:

- "A line where a table tempts": the index recipe's entry form covers it.
- Marking skippable sections "Optional": kept only as the brief's
  READ-IF label; elsewhere such a section moves one link down.
- "A contract lives beside the law it extends": a note for contract
  authors, not for a writer following a recipe.
- The directive on how this skill is packaged, and "a maintainer reading
  source is not an audience": notes for this skill's author.
- Messages to the user in conversation: the earlier version covered them;
  they now belong to the plain-english skill, where installed. This skill
  covers a person only as the reader of a file.

## What the main file holds

The core that every kind shares, then the routing table: cost, the three
ways to save, the link form, and the order rule.
Every recipe sits one link away, most-used first, so brief and report
lead and the index comes last.

Three rules left the main file on 2026-11-13. The keep test: every
recipe states its own question. The alarm: every recipe now spells out
its size sentence. One whole example: whether a recipe carries an
example is decided per recipe, by test.

Writers had been skipping the recipe, because the main file alone felt
like enough to write from. The heading now orders the read, the text
says the recipe holds the rest, and the writer states which recipe it
read. In one test a fast-tier model opened the right recipe in 4 of 4
runs on the new main file; one run that read the old main file skipped
the recipe and wrote unlabelled prose. The stated line appeared in 2 of
the 4 and never in the form shown, so the heading and the routing
sentence do most of the work.

The stated line left the main file on 2026-11-16. In four live runs a
fast-tier agent loaded this skill to write its return. All four opened
the report recipe, and two wrote the stated line inside the return, once
ahead of STATUS. A subagent's last message is its return, so the line
had nowhere else to go.

The precedence line stays in the main file until every recipe carries
its own, as brief and report do.

## Why a size sentence, not a bare number

A rule with no number changed nothing in testing: told that reports are
"capped", an agent wrote a longer report. A hard number has the opposite
fault: it cuts content the reader needs, and an agent under it stops
checking. So each recipe names a size at which the writer runs the keep
test on each line again, and the text may stay longer only when every
line passes. The keep test is the real rule. Only the index entry and
the description are hard limits; both are small by nature and paid for
in every session.

The word "alarm" named this size until 2026-11-13. It needed a
definition in the main file, so a writer holding only the recipe met a
term with no meaning. Each recipe now carries the whole sentence.

## Evidence of 2026-11-10: with and without the skill

One run per side, a mid-tier model, the earlier version of this skill.

| Task | Without | With | Change |
|---|---|---|---|
| Instruction file | 737 words | 433 words | detail moved behind a link |
| Brief | 270 words | 297 words | labels copied from the example; one choice left open |
| Report | about 450 words | about 600 words | labels copied; longer |

Lessons taken: agents copy the example before the rules; agents already
write sound briefs, so that recipe covers only the slips seen; a rule
needs a number or a test to have an effect.

## Evidence of 2026-11-13: the brief and report rebuild

A fast-tier model unless noted, writing from the recipe alone. Each
situation ran once per version, so a single fault is a hint, not proof.

| Question | Result | What the recipe does now |
|---|---|---|
| Does an example with every label make writers over-label? | 1 brief of 5 lifted example lines into a similar task | The paragraph says to write the lines first and add only the labels the task yields; then 0 of 5 |
| Do writers keep the table's label order? | Fast tier: 1 to 2 briefs of 5. Mid tier: 3 of the 4 that used FORMAT | The order rule stays; the fault is the weaker model's |
| Does a report account for every finish condition? | 5 of 5, in two runs | Every report carries STATUS, the work under its label, and each DONE-WHEN item under CHECKED or NOT DONE |
| Does "write no none lines" matter? | Cut once: "NEXT: nothing" appeared. Restored: gone | The phrase stays |
| What happens on large work? | A report re-listed 30 files the brief had named; 2 of 4 echoed the boundary. A 60-hit search the brief asked for came back whole | A guard rail in each recipe |
| Does the guard rail work? | A brief gained the FORMAT line unprompted, and an agent reading no recipe followed it. The 30-file report fell from 14 lines to 4 | Kept. "Drop any restating of the brief" had not fired; naming "a list or boundary the brief gave you" did |
| Is the brief's example needed? | Without it: the same label counts in all 5, the same order accuracy, the same layout, and no lifted content | The brief has no example |
| Is the report's example needed? | Without it: content held, but the STATUS line was misformed in 4 of 5 | The report keeps an example |
| How short can the report's example be? | Five lines showing CHANGED as a list of paths: layout right in 12 of 12, but all 3 large-work reports re-listed. Four lines showing CHANGED as "the pages the brief named": right in 6 of 6 | The four-line example |

Lessons taken:

- Agents copy an example's content as well as its form. So an example
  shows the behaviour that is hardest to get, or the recipe has none.
- The table tells a writer which labels to use. The example tells it
  the layout. Test each separately.
- A general rule did not fire where a named thing did.
- A brief is the only guard rail that reaches a receiver that reads no
  recipe. A dispatch with a FORMAT line brought one agent's return from
  about 45 lines to about 6.

## Why brief and report mirror each other

A report answers a brief, so each required part of a brief has its
answer. GOAL is answered by STATUS. BOUNDARY is answered by the work
under its label. DONE-WHEN is answered item by item, under CHECKED when
met and NOT DONE when unmet. The test for the set was a brief holding
only its three required labels: what must come back?

Each line takes the first row that fits, so a wide row placed early
swallows narrow ones. Three rows were narrowed for that reason. DECIDED
"closes a choice about how the task is done", so a limit or a grant
cannot land there. ACTIONS holds only a command that changed state, so
a test run goes under CHECKED. LOCATED holds only where a thing is, so
a review finding goes under FINDINGS.

The report's rows were checked against every operation of five agents
that carry a fixed report block of their own. Seven rows were widened
and RESULT was added, for a plan or a draft the brief asked for. Those
agents keep their own blocks for now; the recipe says an agent's own
labels win.

## Evidence of 2026-11-16: the spec rebuild

A fast-tier model wrote a spec, plan or blueprint from five sets of
planning notes, about 380 words each. Three sets came with a format a
planning skill would set. Each set hid an open choice, a rejected
option, a debate, a fact one section needs from another, and an exact
interface. A second agent scored the texts without knowing which
recipe wrote which. Each run is five texts, so a single fault is a
hint, not proof.

| Question | Result | What the recipe does now |
|---|---|---|
| Is the recipe needed beside a planning format? | With no spec recipe: 0 of 5 texts listed the open choice with who decides, 3 of 5 writers opened the brief recipe in its place, and 3 of 5 argued the rejected option out | The recipe stays |
| Does the open-choice rule fire? | 5 of 5 in four runs that carried it, 4 of 5 in the fifth | Kept |
| Do writers invent who decides? | "Each with who decides": 6, 7 and 9 invented deciders in three runs, such as "Callum (proposed)". With "or no one named": 0 in two runs | The phrase is in the rule |
| Is the example needed? | Without it: the same open-choice lists and interfaces. Rejected options were argued out less often, and left out altogether in 9 of 15 texts against 1 of 10; writers had no place to file a record | The recipe has no example |
| Is the interfaces line needed? | Without it: exact name, path and format kept in 15 of 15 | Cut |
| Is the research row needed? | No text of 30 carried the debate, with or without a recipe | Cut |
| Is the dependency clause needed? | With it: 0 of 15 texts dropped the fact one section needs from another. Without it: 1 of 15 | Kept, on a hint |
| Can the recipe add a finish condition to a format with no place for one? | A contracts format of four fixed lines: written in 1 of 4 runs that asked for it, under three wordings | The recipe asks only where the format has a place, and adds only the list of open choices |
| Does the size sentence matter? | Not tested alone. Average text: 629 and 589 words with it, 590, 563 and 579 without | Cut; a set format decides the length |

Lessons taken:

- A recipe cannot beat a format that fixes its parts. It can append a
  list; it cannot add a line inside a fixed block.
- Asking for a name invites an invented one. Give the writer the words
  for "none".
- With no recipe for a kind, a writer opens the nearest recipe and
  writes that kind instead.

## Evidence of 2026-11-16: the instruction-file rebuild

A fast-tier model rewrote five overlong instruction files, 708 to 784
words each, for invented repos. Each file hid one item for every Keep
bullet and Move-out row, and a rule for one subfolder; three repeated
a rule from a parent file. Writers could create other files. A second
agent scored where each item went, without knowing which recipe wrote
which. Each run is five rewrites, so a single fault is a hint, not
proof.

| Question | Result | What the recipe does now |
|---|---|---|
| Is the recipe needed? | With none: a main file of 533 words on average, against 263 to 282 with one. The overview stayed in 5 of 5, and procedures, references and history stayed in the main file in 11 of 15 cases | The recipe stays |
| Is the example needed? | Without it: no count worse by more than one, and 282 words against 263 | The recipe has no example |
| Do links hold? | 39 links under three versions of the recipe: all gave path, contents and when to read; none named a missing file; none loaded automatically | The link form is spelled out in the Keep list |
| Is the parent row needed? | With no recipe, the rule repeated from a parent file was cut in 3 of 3 | Cut; the main file's Never list covers it |
| Do writers use a subfolder's own file? | With no row for it: 0 of 15 rewrites. With the row: 4 subfolder files in 3 of 5 rewrites, and no harm rule moved | The row is in the table, with its harm exception |
| Is content lost on the way out? | With only a table of homes: a procedure vanished in 1 of 5 and history in 1 or 2 of 5. With the test "moves when you can name the task or folder that needs it; when you cannot, cut it": none vanished | The paragraph above the table |
| Do prohibitions reach the bottom? | 3 of 5 as a finishing check, and 3 of 5 as "Commands go first, prohibitions last" | Kept as the sentence; unsolved |
| Do writers invent rules? | 0 and 1 under the earlier versions, 2 with no recipe, 4 under the final text | Unsolved; watch it |

Lessons taken:

- A home with no row is never used. No writer made a subfolder file
  until the table named one.
- A table of homes does not say whether to move a line or cut it. One
  question does: can you name the task or folder that needs it?
- Writers keep harm rules, facts and the daily command with no recipe
  at all. The recipe's work is in what leaves the file.

## Where the sizes come from

Measured in the repo this skill was written in, then set beside
published figures. They are starting points; adjust them after use.

| Kind | Measured | Published | Size or limit |
|---|---|---|---|
| Instruction file | 334 words | under 200 lines; 100 to 150 lines scored best in one study | 400 words |
| Index entry | typical 22 words | only the first 200 lines of one vendor's memory index load | 30 words; 150 lines |
| Description | typical 81 words | 1,024 characters at most | 100 words |
| Skill body | typical 118 lines | under 500 lines | 150 lines |
| Brief | 61 to 297 words | no number | 300 words |
| Report | about 450 words, one sample | often 1,000 to 2,000 tokens | 500 words |
| Spec section | typical 198 words | no number | none since 2026-11-16; a set format decides the length |
| State file | no sound sample | no number | 400 words, a guess |

## Published sources

Paraphrased. Recheck each against its page before quoting it.

- Instruction files should hold what the agent needs every session, and
  shorter files are followed better (code.claude.com/docs/en/memory;
  checked against the page text).
- A file that imports another loads both, so an import saves nothing
  (same page; checked).
- A rule that must hold every time belongs in a hook or a deny rule,
  because an instruction file is guidance
  (code.claude.com/docs/en/best-practices; checked).
- Add a rule only when the agent repeats a mistake
  (cursor.com/docs/context/rules).
- Context files did not raise task success in general and added over 20%
  cost; repo overviews did not help (arxiv.org/abs/2602.11988).
- Instruction files of 100 to 150 lines with a few focused reference
  files did best in one vendor's study
  (augmentcode.com/blog/how-to-write-good-agents-dot-md-files).
- Skill descriptions say what the skill does and when to use it, in the
  third person; bodies stay under 500 lines with references one level
  deep; a reference file over 100 lines gets a table of contents
  (agentskills.io/specification;
  platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- A subagent needs an objective, an output format, guidance on tools and
  sources, and clear boundaries; subagents store work outside the
  conversation and pass back light references
  (anthropic.com/engineering/multi-agent-research-system).
- A subagent returns a condensed summary, often 1,000 to 2,000 tokens
  (anthropic.com/engineering/effective-context-engineering-for-ai-agents).
- Accuracy falls as input grows, and one distracting passage is enough to
  lower it (trychroma.com/research/context-rot).
- Models recall the start and end of a long input better than the middle
  (arxiv.org/abs/2307.03172).
- Accuracy falls as the number of instructions rises
  (arxiv.org/abs/2507.11538).
- A subfolder can hold its own instruction file, and the nearest file
  applies to work there (agents.md; the same is described for four
  agent tools in their own docs).
- In a study of over 2,500 agent files, the good ones put runnable
  commands early and stated boundaries; vague files failed
  (github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories).
- Other size guidance is looser than this skill's: under 200 lines,
  under 300 lines, two pages (code.claude.com/docs/en/memory;
  humanlayer.dev/blog/writing-a-good-claude-md; docs.github.com,
  repository custom instructions).
