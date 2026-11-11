# Skill body or agent definition

Loaded when the skill or agent is triggered, and it then stays for the
whole session. Alarm: 150 lines.

## Keep

- The steps and rules every use needs.
- One whole example of the output.
- One link per file moved out, in the link form.

An agent definition also says what the agent starts with. It begins with
no conversation, so the definition names what a dispatch must give it and
what it returns.

## Move out

| Content | Where it goes |
|---|---|
| Detail only some uses need | a file one link away, with its read-when condition |
| Reasons and evidence | a separate file, marked "read only when changing this" |
| What the description already says | nowhere |
| What another skill holds | the skill's name, guarded by "where installed" |

## Keep test

Do most loads of this file use this section? Within it, would the agent
act differently without this line?

## Example

A whole body that sends rare detail down a level:

```text
Turns an invoice file into one row of the ledger sheet.

## Steps
1. Read the invoice. If it is a scan, read `references/scanned.md`
   first.
2. Take the supplier name, invoice number, date, total and currency.
3. If any of the five is missing, stop and report which.
4. Write the row.

## Output
Acme Ltd | INV-2041 | 2026-02-11 | 1840.00 | EUR

`references/scanned.md`: reading a scanned invoice. Read only at step 1.
`references/why.md`: reasons for these steps. Read only when changing
this skill.

## Never
- Never guess a missing value.
- Never convert the currency.

Done when the row is written, or the missing value is reported.
```

## Finishing check

- Every section passes the keep test.
- What the agent does first is at the top; prohibitions and the finish
  condition are at the bottom.
- Every instruction names an output the agent produces or an action it
  takes. A line that only says how to feel about the work changes
  nothing.
- Each linked file is one link deep.
