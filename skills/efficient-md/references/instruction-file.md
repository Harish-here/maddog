# Instruction file

Loaded every session, by every agent that works in the folder (an
AGENTS.md or its equivalent). Alarm: 400 words.

## Keep

- A rule whose breach causes harm, and which an agent would not follow
  unprompted.
- A fact an agent cannot find by reading the repo.
- A command needed in most sessions.
- One link per file moved out, in the link form.

Facts, commands and rules that prevent harm go in from the start. Any
other rule goes in when an agent has made the mistake it prevents.

## Move out

| Content | Where it goes |
|---|---|
| A procedure for one kind of task | a skill, or a linked file |
| Reference detail: flags, formats, lists | a linked file |
| Reasons and history | a linked file |
| An overview of the layout or the stack | nowhere; the reader can list the files |
| A style rule a formatter or linter enforces | nowhere; the tool enforces it |
| A rule with no exceptions | an automated check; keep a line only when an agent must know the check exists |
| Anything a parent instruction file states | nowhere; the reader holds it |

## Keep test

Would an agent on an unrelated task in this folder go wrong without this
line?

## Example

Before, with its longest parts cut short:

```text
# Project guide
This is a payments service written in Go. It has an api/ folder, a
worker/ folder and a db/ folder. We started it in 2022 and moved from
REST to gRPC last year.

## Testing
Run `make test` before every commit. To run one package use
`go test ./api/...`.
-race turns on the race detector. -count=1 turns off the cache.
(18 more lines of flags and fixes for known failures)

## Releases
1. Bump the number in VERSION.
(11 more steps)

## Style
Format with gofmt. Group imports the way gofmt does.

## Rules
Never edit a merged file under db/migrations/; add a new migration. CI
rejects the edit.
Amounts of money are integers in minor units, never floats.
```

After, the whole file:

```text
# Project guide
- Run `make test` before every commit.
- Amounts of money are integers in minor units, never floats.

`docs/testing.md`: test flags and fixes for known failures. Read when a
test fails.
`docs/release.md`: the release steps. Read before cutting a release.

- Never edit a merged file under db/migrations/; add a new migration. CI
  rejects the edit.
```

Where each cut went: the overview and the history, nowhere; the
single-package command and the flags, `docs/testing.md`; the release
steps, `docs/release.md`; the style rules, nowhere, because the formatter
enforces them. The migrations rule has no exceptions, so a check enforces
it, and its line stays because an agent must know the check exists.

## Finishing check

- Every line passes the keep test.
- No line repeats a parent instruction file.
- Every link says when to read it.
- Prohibitions sit at the bottom.
