# When a person reads the text

Read this first when a person is the main reader, or reads the text
alongside an agent (a README, a report for the user, a handover a person
will read). A text whose purpose is to be loaded by an agent (an
instruction file, a skill body, a brief) follows its own recipe alone,
even when people also read it.

## A person is the main reader

- Wording follows plain-english where installed. Otherwise: the outcome
  first, full sentences, structure kept.
- Placement still follows this skill: a digest in the file, the bulk
  behind a link.
- Narrative and history may stay when they are what the person came for.
  The agent recipes' rules against them do not apply.
- No agent size rule applies.

## A person and an agent both read it

Split the text. Each reader gets its own section or file, written for
that reader and held to that reader's rules. The agent's part follows the
recipe for its kind.

Where the text cannot split (one message read by both), a person's
wording rules govern the form, and the recipe for its kind governs what
goes in.

## Keep test

For the person's part: would the person decide or act differently without
this paragraph?

## Example

A README that both read:

```text
# Ledger tools

Ledger tools turns supplier invoices into rows of your ledger sheet.
Install it, point it at a folder of invoices, and check the rows it
writes.

(the rest of the person's part: install, first run, where to get help)

## For agents

`docs/agents/commands.md`: every command and flag. Read before running
any command.
`docs/agents/layout.md`: where each kind of file lives. Read before
adding a file.
```

## Finishing check

- A person who stops after the first lines has the outcome.
- No table or list in the person's part exists only for an agent; that
  goes in the agent's part.

## Never

Never hold a person's document to an agent's size rule.
