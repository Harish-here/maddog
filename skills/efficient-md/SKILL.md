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

A text costs its words multiplied by the number of times it is loaded.
Save three ways: cut a line the reader would act the same without; move
detail only some readers need to a file one link away; give a path in
place of text the reader can open, and nothing in place of text it
already holds.

## Find the kind, then read its one recipe

| Kind | Loaded | Recipe |
|---|---|---|
| Instruction file | every session | `references/instruction-file.md` |
| Index | every session | `references/index.md` |
| Description of a skill or agent | every session | `references/description.md` |
| Skill body or agent definition | when triggered, then all session | `references/skill-body.md` |
| Brief or prompt | once by the receiver; stays with the caller | `references/brief.md` |
| Report back (a return) | stays with the caller all session | `references/report.md` |
| Spec, plan or blueprint | per task, one section at a time | `references/spec.md` |
| State file | each session that resumes the work | `references/state-file.md` |
| Filed record | only when a link is followed | `references/record.md` |

The kind belongs to the unit that loads, not the file: a skill's
description and its body are two units.

- `references/person-reader.md`: rules for a text a person reads. Read
  first when a person is the main reader, or reads it alongside an agent.
- `references/special-cases.md`: a text of no listed kind, and content
  that moves to another kind. Read when either applies.

## Rules for every kind

- **Keep test.** The question a line must pass to stay in the text. Each
  recipe names one. Every line must pass it, however short the text.
- **Alarm.** The size a recipe gives, at which the writer checks again.
  Over it, run the recipe's move-out list once more. The text may stay
  over when every line passes the keep test. A size marked "limit" is a
  ceiling: the text must come under it.
- **Link form.** A link names the file, what it holds, and when to read
  it. The reader chooses to open it; a link that loads its file
  automatically saves nothing. The linked file links no further down.

  ```text
  `docs/testing.md`: test flags and known failures. Read when a test fails.
  ```
- **Position.** What the reader acts on first goes at the top.
  Prohibitions go at the bottom, and so does a finish condition when the
  text sets a task. A text that sets no task gets none.
- **One whole example.** A text that asks its reader for an output or a
  form gives one example of it. Readers copy the example before the
  rules, so it shows everything that matters and nothing else.

## Above the recipes

A repo's own written rules beat any recipe. So does a format that another
skill or definition sets for the text, such as a dispatch contract that
names its parts.

- `references/shipping.md`: what a shipped file may cite. Read when
  shipping a file to other users.
- `references/why.md`: reasons and evidence. Read only when changing this
  skill.

## Never

- Never send a reader text it already holds: its own definition, an
  instruction file it loads anyway, or the brief it sent you.
- Never rewrite or shorten a filed record, or pass on a summary in its
  place.

Finished when every line passes its keep test and the recipe's finishing
check holds.
