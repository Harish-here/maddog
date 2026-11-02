---
name: memory-refine
description: >
  Audits saved memory notes, returns a keep, rewrite, or delete verdict
  per note with evidence, and applies the changes the user approves. Use
  when the user asks to clean up, refine, or audit memory notes, or when a
  stale memory note just led to a wrong decision. Not for writing new
  memory notes, and not for editing instruction files.
argument-hint: [where the memory notes are]
---

## 1. Scope
Audit the memory notes the user names. If the user names none, find the
memory notes that apply to the current project. If you cannot find them,
ask the user. Where memory is kept per project, cover other projects
only when asked.
Done: you can state where the notes in scope are, and you can read them.

## 2. Count first
Count the notes in scope with a tool, never by eye. An index is not a
note. If the count is zero or the tool reports an error, recheck where
the notes are before going on.
Done: the count came from error-free tool output, and you have the list
of notes it counted.

## 3. Check each note
Answer three questions per note.
- a. Does it tell the next session what to do, or only what happened?
- b. Is each fact it states still true today? Catch a note that says
  something is missing when it now exists, as well as one that names
  something gone. Check the real thing each fact is about, such as the
  file, tool, or record, at most three checks per note. Write "could not
  check" for any fact left unchecked, whether access was missing or the
  limit ran out.
- c. Does another note say the opposite? Search the other notes for the
  same subject words.
Done: each note has answers to a, b, and c. Each fact in b has evidence
or "could not check", and c has evidence.

## 4. Give verdicts and report
Give each note one verdict: keep, rewrite, or delete. Add a one-line reason
and the evidence, meaning what you checked.

Verdict rules:
- A note that only records what happened: rewrite to its lesson if it
  has one, otherwise delete.
- A false fact or rule: rewrite if the rest is useful, otherwise delete.
- Two notes that disagree: find the false one with the evidence, then use
  the rule above. If the evidence cannot decide, keep both and say why.
- A "could not check" fact alone never decides rewrite or delete. Name
  it in the reason.

Search for every phrase you quote. It must appear in the note.

Report one table: note | verdict | reason | evidence.
Done: every note on the list from step 2 is one row, and every quoted
phrase was found in its note.

## 5. Wait, then apply
Change nothing until the user approves. Each deletion needs approval that
names the note; one approval may name several notes. Show rewritten text,
and save it only after the user approves it. If the notes have an index,
keep it matching: remove a deleted note's entry, and update a rewritten
note's entry when its summary changed. Finish by reporting how many notes
were kept, rewritten, and deleted.
Done: each deleted note and its index entry are gone, each rewrite was
approved before saving, the index matches the notes, and the totals are
reported.

DONE-WHEN: the user has one table with a verdict and evidence for every
note, and every approved change is applied, including any index entry it
affects. Nothing else was touched.
