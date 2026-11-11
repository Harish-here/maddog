# State file

Loaded at the start of each session that resumes the work (progress
notes, a handover file). It is rewritten in place; that is its job.
Alarm: 400 words.

## Keep

- The current state, in a few lines.
- The next step.
- Open decisions, each with who decides.
- Paths to the spec, the branch, and the files in play.

## Move out

| Content | Where it goes |
|---|---|
| Finished items | delete them; version control holds the past |
| How the work got here | a filed record, when someone will need it; otherwise nowhere |
| A lesson that outlasts this work | wherever lasting guidance is kept |
| Detail of a finished decision | the spec, or a filed record |

## Keep test

Does the next session need this line to continue?

## Example

```text
# Export feature: state

State: endpoint and contract tests merged to branch feat/export. Async
export (spec section 4) not started.

Next: write the job table migration named in spec section 4.1.

Open:
- Retention of finished export files: 7 or 30 days. The product owner
  decides.

Paths: docs/export/spec.md; branch feat/export; tests/export/.
```

## Finishing check

- A fresh agent could continue from this file alone.
- No line describes the past, unless the next step depends on it.
- The next step is one action, not a goal.
