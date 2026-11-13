# Brief or prompt

Loaded once by the receiver; it stays in the caller's context all
session. At 300 words, run the keep test on each line again; the
brief may stay longer only when every line passes.

## Keep test

Would the receiver do the task differently without this line? Every
line in the brief must pass, whatever label it takes.

## Keep: sort each line under a label

Write the lines the receiver needs first, then give each line the
first row that fits. Every new brief carries GOAL, BOUNDARY and
DONE-WHEN; add only the other labels the task yields. Write the
labels in the table's order. Where the caller's instructions or the
receiver's description name other labels, use those instead.

| Label | Holds a line that |
|---|---|
| GOAL | names the task in one sentence, and why it matters |
| DECIDED | closes a choice about how the task is done; to leave the receiver none, close every one, down to the exact command |
| CRITERIA | leaves a choice open and says how to judge it, in priority order |
| FACTS | is a claim with a source: path and line, SHA, or command output |
| CHECK-FIRST | is a claim with no source, or a guess; for a branch, PR or file, names where to check |
| READ-IF | is optional reading: a path and when to open it |
| FORMAT | shapes the receiver's answer, with one example line |
| AUTHORITY | grants an action that changes shared state: which one, and who approved it |
| BOUNDARY | says where the receiver may work and what it must not do |
| DONE-WHEN | is the check: the symptom or result, never a guessed fix |

A line that passes the keep test but fits no label goes under
BOUNDARY if it limits the receiver, else under FACTS.

Where the brief lists files or steps, a FORMAT line asks back only
for the ones that went differently.

## Reasons

A line carries its reason when, without it, the receiver could make a
wrong but plausible choice.

## Move out: what leaves the brief

- File contents and background become READ-IF paths.
- Drop what the receiver already holds, as far as its description or
  the caller's instructions show.
- Leave the diagnosis to the receiver; a guess at the cause stays only
  as a CHECK-FIRST line.
- A record kept in a file, such as a ticket or a review, goes by path,
  or quoted exactly where the receiver must have its words. An earlier
  review verdict with no file is quoted exactly, never summarised.
- On a resume, send what changed and name the rest "as before". A
  note that changes nothing needs no labels.

## Finishing check

The receiver can start without asking a question, and every path it
may read exists.
