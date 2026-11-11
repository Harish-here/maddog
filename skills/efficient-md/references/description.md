# Description of a skill or agent

Loaded every session, beside every other description. The reader uses it
for one thing: to choose this skill or agent, or a neighbour. Limit: 100
words, and under any character limit the platform sets.

## Keep

- What it does, in one sentence, in the third person.
- When to use it, in the words a request would use.
- When not to use it, naming what to use then.

## Move out

| Content | Where it goes |
|---|---|
| How it works; its steps | the body |
| Examples of its output | the body |
| Its reasons | the body, or a linked file |

## Keep test

Would the reader choose differently between this and its neighbours
without this phrase?

## Example

Says how, not when; the border with its neighbour is missing:

```text
A powerful helper that parses the changelog, groups commits by type
using conventional-commit prefixes, and renders release notes.
```

Right:

```text
Writes release notes from the commits since the last tag. Use when a
release is being prepared and its notes are not yet written. Do not use
to decide the version number: that is the versioning skill.
```

## Finishing check

Read it beside its neighbours' descriptions. Write three sample requests:
one it should take, one a neighbour should take, one near the border. The
choice is clear for all three.
