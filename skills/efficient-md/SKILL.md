---
name: efficient-md
description: >
  Tells an agent how to write text that another agent will load: what to
  keep, what to move behind a link, and when the text is too long. Use
  before writing or restructuring an AGENTS.md or other instruction file,
  a memory index, a skill or agent description or body, a brief or
  dispatch prompt, a report back, a spec, plan or blueprint, a state or
  handover file, a filed record or ledger, or a README a person reads.
  Not for replies to the user in conversation (plain-english, where
  installed), nor for reviewing existing text (do that directly).
---

## Rules for every kind

A text costs its words multiplied by the number of times it is loaded.
Save three ways:

- Cut a line the reader would act the same without. Each recipe gives
  this as its keep test.
- Move detail only some readers need to a file one link away, in the
  link form: the link names the file, what it holds, and when to read
  it, and never loads it automatically.
- Give a path in place of text the reader can open, and nothing in
  place of text it already holds.

Put what the reader acts on first at the top, and prohibitions and any
finish condition at the bottom.

A repo's own rules, or a format another skill sets for the text, beat
any recipe.

## Read the recipe before you write

These rules are the base; the recipe holds the rest. Find your text in
the table, read its recipe, then state which one you read:

```text
brief → references/brief.md
```

| You are writing | Recipe |
|---|---|
| Brief or prompt | `references/brief.md` |
| Report back (a return) | `references/report.md` |
| Spec, plan or blueprint | `references/spec.md` |
| State file | `references/state-file.md` |
| Filed record | `references/record.md` |
| Skill body or agent definition | `references/skill-body.md` |
| Description of a skill or agent | `references/description.md` |
| Instruction file | `references/instruction-file.md` |
| Index | `references/index.md` |

The kind belongs to the unit that loads, not the file: a skill's
description and its body are two units.

- `references/person-reader.md`: rules for a text a person reads. Read
  first when a person is the main reader, or reads it alongside an agent.
- `references/special-cases.md`: a text of no listed kind, and content
  that moves to another kind. Read when either applies.
- `references/shipping.md`: what a shipped file may cite. Read when
  shipping a file to other users.
- `references/why.md`: reasons and evidence. Read only when changing this
  skill.

## Never

- Never send a reader text it already holds: its own definition, an
  instruction file it loads anyway, or the brief it sent you.
- Never rewrite or shorten a filed record, or pass on a summary in its
  place.

Finished when you have stated the recipe you read, every line passes its
keep test, and the recipe's finishing check holds.
