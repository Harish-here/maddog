# Why these rules

Read only when changing this skill. A writer never needs this file.

## The model

The cost of a text is its words multiplied by its loads. A writer can cut
words, move words to a place that loads less often, or point to text the
reader can already reach. Every recipe applies those three moves to one
kind of text.

An earlier version sorted texts into four classes by how long they stay
loaded. Load frequency alone could not tell a writer how to write: a
skill description and an instruction file load equally often and need
different recipes. The kind of text now picks the recipe, and load
frequency is one column of the table.

Rules of the earlier version left out on purpose:

- "A line where a table tempts": the index recipe's entry form covers it.
- Marking skippable sections "Optional": kept for a brief's background
  only; elsewhere such a section moves one link down.
- "A contract lives beside the law it extends": a note for contract
  authors, not for a writer following a recipe.
- The directive on how this skill is packaged, and "a maintainer reading
  source is not an audience": notes for this skill's author.
- Messages to the user in conversation: the earlier version covered them;
  they now belong to the plain-english skill, where installed. This skill
  covers a person only as the reader of a file.

Every recipe sits one link away, brief and report included. The main
file holds the concept: the cost of a text, the table of kinds, and the
rules every kind shares. An agent about to dispatch pays one extra read;
every other writer stops loading two recipes it does not use.

## Why alarms, not limits

A rule with no number changed nothing in testing: told that reports are
"capped", an agent wrote a longer report. A hard number has the opposite
fault: it cuts content the reader needs, and an agent under it stops
checking. So each number is an alarm that sends the writer back to the
move-out list, and the keep test is the real rule. Only the index entry
and the description are hard limits; both are small by nature and paid
for in every session.

## Evidence from a with-and-without test

2026-11-10, one run per side, a mid-tier model, the earlier version of
this skill.

| Task | Without | With | Change |
|---|---|---|---|
| Instruction file | 737 words | 433 words | detail moved behind a link |
| Brief | 270 words | 297 words | labels copied from the example; one choice left open |
| Report | about 450 words | about 600 words | labels copied; longer |

Lessons taken: agents copy the example before the rules, so each recipe
carries one whole example; agents already write sound briefs, so that
recipe covers only the slips seen; a rule needs a number or a test to
have an effect.

## Where the alarms come from

Measured in the repo this skill was written in, then set beside
published figures. They are starting points; adjust them after use.

| Kind | Measured | Published | Alarm or limit |
|---|---|---|---|
| Instruction file | 334 words | under 200 lines; 100 to 150 lines scored best in one study | 400 words |
| Index entry | typical 22 words | only the first 200 lines of one vendor's memory index load | 30 words; 150 lines |
| Description | typical 81 words | 1,024 characters at most | 100 words |
| Skill body | typical 118 lines | under 500 lines | 150 lines |
| Brief | 61 to 297 words | no number | 300 words |
| Report | about 450 words, one sample | often 1,000 to 2,000 tokens | 500 words |
| Spec section | typical 198 words | no number | 500 words |
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
