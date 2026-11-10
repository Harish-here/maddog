# Report back

Loaded into the caller's context, where it stays all session. Alarm: 500
words.

- **Keep, in this order:** the answer or status; what changed or was
  found, by path; decisions made inside the boundary; claims not
  verified, marked as such; what is blocked, and on what. Use the form
  the brief asked for.
- **Move out:** logs, diffs and full tables go to a file, and the report
  gives its path. A writer that cannot write files keeps only the rows
  the caller's decision needs. Drop how the work was done and any
  restating of the brief.
- **Keep test:** does the caller need this line to choose its next step?

An example, answering a brief that asked for one line per retry clause.

```text
Done: 3 of 4 services have a retry clause; billing/ has none found.
services/queue/client.py:41 retry(max=5, backoff=2)
services/mail/send.py:17 retry(max=3)
services/sync/config.yaml:8 backoff: exponential
Decided: counted the backoff setting in sync/config.yaml as a clause.
Not verified: whether vendored code under third_party/ retries.
Blocked: nothing.
```

**Finishing check:** the caller knows the outcome from the first line.
