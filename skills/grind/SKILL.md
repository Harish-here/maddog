---
name: grind
description: Delegate ONE fully-specified mechanical task (bulk edit, test run, search, extraction) to the cheap fast-tier executor in an isolated context; return only the distilled result. Do NOT use for ambiguous or judgment tasks — use grind-pro.
context: fork
agent: executor-fast
argument-hint: [task]
---
TASK: $ARGUMENTS

Do exactly this, nothing more; don't attempt actions needing approval; return a
concise result, or STATUS: blocked with REASON: <what's missing>.
