# Instruction file

Loaded every session, by every agent that works in the folder (an
AGENTS.md or its equivalent). At 400 words, run the keep test on each
line again; the file may stay longer only when every line passes.
Where the repo, or the tool that loads the file, sets rules for it,
those stand.

## Keep test

Would an agent on an unrelated task in this folder go wrong without
this line? Every line must pass.

## Keep

- A rule whose breach causes harm, and which an agent would not follow
  unprompted.
- A fact an agent cannot find by reading the repo.
- A command needed in most sessions.
- One link per file moved out: its path, what it holds, and when to
  read it. Never a link that loads the file automatically.

Facts, commands and rules that prevent harm go in from the start. Any
other rule goes in when an agent has made the mistake it prevents.
Commands go first, prohibitions last.

## Move out: what leaves the file

A line that fails the keep test moves when you can name the task or
folder that needs it; when you cannot, cut it. The task or folder you
named is the link's "when to read it". Write one file for each "when".

| Content | Where it goes |
|---|---|
| A procedure for one kind of task | a skill, or a linked file |
| Reference detail: flags, formats, lists | a linked file |
| Reasons and history | a linked file |
| A rule for one subfolder, unless its breach causes harm | that folder's own instruction file |
| An overview of the layout or the stack | nowhere; the reader can list the files |
| A style rule a formatter or linter enforces | nowhere; the tool enforces it |
| A rule with no exceptions | an automated check; keep a line only when an agent must know the check exists |

## Finishing check

Every link says when to read it.
