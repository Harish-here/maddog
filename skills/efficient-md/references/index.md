# Index

Loaded every session (a memory index, a catalogue of files). Limit: 30 words
per entry. At 150 lines for the whole index, run the keep test on each entry
again; the index may stay longer only when every entry passes.

## Keep

One line per subject: the file's name as a link, what it holds, and when
to open it.

```text
- [Title](file.md): what it holds; open when <condition>
```

## Move out

| Content | Where it goes |
|---|---|
| The content itself | the linked file |
| Status, dates, history of the entry | the linked file |
| An entry whose file is gone or no longer true | delete the entry |
| Two entries for one subject | one entry; merge the files |

Entries for filed records are the exception to the last two rows. The
entry stays, the records are never merged or deleted, and a correction
joins the same entry as a second link.

## Keep test

Can a reader decide to open or skip the file from this line alone?

## Example

Too long, and the reader still cannot tell when to open it:

```text
- [Retry doctrine](retry-doctrine.md): we decided in March after the
  queue outage that backoff is exponential with jitter, capped at 30s,
  and the worker team owns it; revised in May (see PR 212)
```

Right:

```text
- [Retry doctrine](retry-doctrine.md): backoff rules for queue clients; open before changing any retry code
- [Release checks](release-checks.md): what must pass before a tag; open before a release
```

## Finishing check

- Every entry passes the keep test.
- No entry restates what its file says beyond the one clause that names
  it.
- Every linked file exists.
