# Report back

Loaded into the caller's context, where it stays all session. At 500
words, run the keep test on each line again; the report may stay
longer only when every line passes.

## Keep test

Does the caller need this line to choose its next step? Every line in
the report must pass, whatever label it takes.

## Keep: sort each line under a label

Write the lines the caller needs first, then give each line the
first row that fits. Every report carries STATUS, the work under its
label, and each DONE-WHEN item under CHECKED or NOT DONE; add only
the other labels the work yields, and write no "none" lines. Write
the labels in the table's order. Where the brief or your own
instructions name other labels, use those instead.

| Label | Holds a line that |
|---|---|
| STATUS | opens the report: done when every DONE-WHEN item is met, partial when one is unmet and nothing stops it, blocked when something does; then a dash and the outcome against the GOAL in one line |
| BLOCKED-ON | says what would unblock an unmet item: a decision, a fact, a grant, or cannot be done; then the detail |
| NOT DONE | names something asked for and left out: skipped, not reached or not found, with why; at any status |
| ALERTS | tells the caller something beyond the task: an anomaly, a safety notice, a change you did not cause, a guard refusal and what you did instead |
| LOCATED | gives where an item is, by path and line or URL, with its exact words if asked |
| CHANGED | names a path changed or created |
| ACTIONS | gives a command that changed state, or a dispatch, with its SHA, link, exit code or result |
| RESULT | gives text the brief asked you to write: a plan or a draft |
| CHECKED | gives a check or search run and its outcome; each CHECK-FIRST item as confirmed, ruled out, or untested |
| FINDINGS | gives a conclusion: a finding against a criterion the brief set, or a cause, with its evidence |
| DECISIONS | gives a choice or assumption you made, and what decided it |
| DETAIL | gives the path to long output: logs, diffs, full tables |
| NEXT | suggests optional work left, or a step outside the boundary |

A line that passes the keep test but fits no label goes under ALERTS.
The brief's FORMAT shapes the lines under LOCATED, CHANGED, RESULT
and FINDINGS.

## Move out: what leaves the report

- Logs, diffs and full tables go to a file, named under DETAIL. A
  writer that cannot write files keeps only the rows the caller's
  next step needs.
- Drop how the work was done, unless a step went wrong in a way that
  changed the result; that goes under ALERTS.
- Drop what the caller holds or can work out for itself: a list or
  boundary the brief gave you, a command it could write. Name an item
  from the brief only when the caller must know something about it.
- A claim you did not test is marked untested under CHECKED, never
  stated as fact.

## Example

This report answers a brief to stop an order summary showing another
account's items. Its CHECK-FIRST guessed the memo, its CRITERIA
preferred fewer files, and its DONE-WHEN asked for a clean repro and
a test. A clean report needs STATUS and two more.

```text
STATUS: blocked — the summary now shows only the current account's
  items; the test is not written and nothing is committed.
BLOCKED-ON: a grant — the test needs a second account in
  test/fixtures/accounts.ts, outside src/summary/.
NOT DONE: the test that follows the repro — not reached: blocked above.
ALERTS: src/summary/Total.test.tsx failed before my change; I left it.
CHANGED: src/summary/ItemList.tsx
CHECKED:
  repro shows the new account's items — confirmed, docs/bugs/412.md:3.
  the memo misses selectedIds — confirmed, src/summary/ItemList.tsx:40.
  query cache keeps no old items — untested: the fix did not touch it.
FINDINGS:
  src/summary/ItemList.tsx:40 memo leaves out selectedIds
  src/summary/ItemList.tsx:40 selectedIds added to the memo's inputs
DECISIONS: fixed the memo, not the query cache: one file against three.
NEXT: src/cart/Mini.tsx:22 memoises the same way; worth the same check.
```

## Finishing check

The caller knows the outcome from the first line, the first line
agrees with the body, and every claim names where to check it.
