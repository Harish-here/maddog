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
| CHECKED | gives a check or search run and its outcome; each CHECK-FIRST item and each claim of your own as confirmed, ruled out, or untested |
| FINDINGS | gives a conclusion: a finding against a criterion the brief set, or a cause, with its evidence |
| DECISIONS | gives a choice or assumption you made, and what decided it |
| DETAIL | gives the path to long output: logs, diffs, full tables |
| NEXT | suggests optional work left, or a step outside the boundary |

A line that passes the keep test but fits no label goes under ALERTS.
The brief's FORMAT shapes the lines under LOCATED, CHANGED, RESULT
and FINDINGS.

## Move out: what leaves the report

- How the work was done.
- What the caller holds or can work out for itself: a list or boundary
  the brief gave you, a command it could write. Name an item from the
  brief only when the caller must know something about it.
- Long output: it goes to a file, named under DETAIL. A writer that
  cannot write files keeps only the rows the caller's next step needs.

## Example

A clean report needs STATUS and two more.

```text
STATUS: done — all 14 guide pages the brief named use the new error shape.
CHANGED: the 14 pages the brief named.
CHECKED:
  scripts/check-docs.sh exits 0 — confirmed.
```

## Finishing check

The caller knows the outcome from the first line, the first line
agrees with the body, and every claim names where to check it.
