---
name: grind-pro
description: Delegate ONE task needing some local judgment (pattern-matching refactor, tricky edit, small local design choice) to the mid-tier executor in an isolated context; return the result plus any judgment calls. Do NOT use for purely mechanical work — use grind, which is cheaper.
context: fork
agent: executor-smart
argument-hint: [task]
---
TASK: $ARGUMENTS

Do exactly this within its stated boundary; note judgment calls; return the
result, or STATUS: blocked with REASON: <what's missing>.
