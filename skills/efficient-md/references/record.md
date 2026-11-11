# Filed record

Loaded only when a reader follows a link to it (a ruling, a post-mortem,
a transcript, a decision ledger entry). No alarm: a record is as long as
what happened.

## Keep

Everything, in full, as it was said or found: what was asked, what was
decided or found, the evidence, who decided, and the date. A record's
value is that it was not edited.

## Move out

| Content | Where it goes |
|---|---|
| What the work should do next | a state file |
| A lasting rule the record gave rise to | an instruction file or a skill, with a link back |
| A correction to an earlier record | a new record beside the old one |
| How to find this record | one line in an index |

## Keep test

Is this line part of what was asked, found, said or decided? Then it
stays, at any length.

## Example

A record:

```text
# Ruling: gate 3, export format
Date: 2026-03-04. Decided by: the product owner.

Asked: may the export ship as CSV only?
Evidence: 41 of 44 support requests in February asked for CSV
(support/export-requests.csv). XLSX needs a library the security review
has not cleared (reviews/xlsx-lib.md).
Ruling: upheld. CSV only for this release. Reopen when the library
clears review.
```

Its index line, after a later correction:

```text
- [Gate 3 ruling](rulings/gate3.md): export ships CSV only; corrected by [its correction](rulings/gate3-corr.md); open before reopening the format
```

## Finishing check

- An index line points to it.
- No other file holds a shortened copy of it.
- A brief that needs it gives its path. Where the receiver must have its
  words, the brief quotes the passage exactly.

## Never

- Never rewrite or shorten a record after filing. A record found wrong
  stays as it is; the correction is a new record.
- Never pass on a summary in place of the record.
