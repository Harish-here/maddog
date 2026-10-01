---
name: memory-refine
description: >
  Audits saved memory notes and returns a keep, rewrite, or delete call
  per note, with evidence. Use when the user asks to clean up, refine,
  or audit memory notes, or when a stale memory just led to a wrong
  decision. Changes nothing until the user approves. Not for writing
  new memory, and not for editing CLAUDE.md or other instruction files.
argument-hint: [path to a memory folder]
---

DONE-WHEN: the user has one table with a call and evidence for every note,
and every approved change is applied. Nothing else was touched.

## 1. Scope
Use the folder the user names. If none, use the current project's memory
folder. Cover all projects only when asked.
Done: you can state each folder path, and each exists.

## 2. Count first
Count with a script, never by reading a list by eye. With DIR set to the folder from step 1:

    N() { find "$DIR" -name '*.md' ! -name MEMORY.md; }
    N | wc -l
    N | xargs grep -h '^ *type:' | sort | uniq -c
    N | xargs grep -L 'Why:'

These give total notes, notes per type, and notes with no "Why:" line.
No "Why:" line is a signal to look closer, not a verdict.
Done: all three counts came from script output.

## 3. Check each note
Answer three questions per note.
- a. Does it tell the next session what to do, or only what happened?
- b. Is what it says about a file, flag, skill, tool, or pull request still
  true today? Catch a note that says something is missing when it now
  exists, as well as one that names something gone. Check live state, at
  most three checks per note. Write "could not check" when access is
  missing. Never guess.
- c. Does another note say the opposite? Search the other notes for the
  same subject words.
Done: each note has answers to a, b, and c, with evidence for b and c.

## 4. Call and report
Give each note one call: keep, rewrite, or delete. Add a one-line reason
and the evidence (a file or a command).
- A note that only records what happened is deleted, or cut to its one lesson.
- A rule that is no longer true is deleted or corrected.
- Grep every phrase you quote. It must appear in the note.

Report one table: note | call | reason | evidence.
Done: every note is one row, and every quoted phrase was grepped.

## 5. Wait, then apply
Change nothing until the user approves. The user approves each deletion
per note. Show rewritten text before saving it. After an approved
deletion, remove that note's line from the folder's MEMORY.md index.
Done: each deleted note's file and index line are gone, and each rewrite
was shown and approved first.
Finish by reporting how many notes were kept, rewritten, and deleted.
