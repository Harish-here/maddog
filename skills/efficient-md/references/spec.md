# Spec, plan or blueprint

Loaded per task, usually one section at a time, by each agent that builds
from it. At 500 words in a section, run the keep test on each of its lines
again; the section may stay longer only when every line passes.

## Keep

- Decisions, stated as decided.
- Interfaces: names, paths, formats.
- A finish condition per section.
- Open decisions, listed in one place, each with who decides.

Each section stands alone under a heading a brief can cite.

## Move out

| Content | Where it goes |
|---|---|
| The discussion behind a decision | a filed record, linked |
| Research and comparisons | a linked table |
| How the spec changed over time | version control |
| Options that were rejected | a filed record, linked, when a builder might retry them; otherwise nowhere |

## Keep test

Would a builder build something different without this line?

## Example

One section:

```text
## 3. Export endpoint

GET /reports/{id}/export returns the report as CSV.

- Columns, in order: date, account, amount_minor, currency.
- Rows sort by date, oldest first.
- A report over 50,000 rows returns 413; the client then uses the
  async export in section 4.
- Auth: the same token scope as GET /reports/{id}.

Done when: the contract test in tests/export/ passes for an empty
report, a 3-row report, and a 50,001-row report.

Why CSV and not XLSX: `docs/decisions/export-format.md`. Read only when
reopening the format.
```

## Finishing check

- A brief can cite one section, and the receiver needs nothing else.
- No section depends on a sentence in another section without naming it.
- Nothing undecided is written as if decided.
