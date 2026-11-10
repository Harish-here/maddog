# Brief or prompt

Loaded once by the receiver; it stays in the caller's context all
session. Alarm: 300 words.

- **Keep:** the goal in one sentence; the boundary; a finish condition
  the receiver can check; decisions already made; known facts with path
  and line; what to report and in what form. A brief for a mechanical
  task makes every choice itself, down to the exact command or name.
- **Move out:** file contents and background become paths, background
  marked optional. Drop what the receiver's own definition says. A filed
  record goes by path, or quoted exactly where the receiver must have its
  words. An earlier verdict or ruling that has no file is quoted exactly
  too, never summarised.
- **Keep test:** would the receiver do the task differently without this
  line?

An example. Use the labels the receiver's own definition names;
otherwise any clear labels do.

```text
GOAL: Quote every retry clause under services/, with file and line.
DECIDED: A retry clause is any call to retry() or any backoff setting.
FACTS: services/queue/client.py:41 holds one; use it as the model.
OPTIONAL: services/README.md, for the layout.
REPORT: one line per clause, like this one:
  services/queue/client.py:41 retry(max=5, backoff=2)
Then anything blocked.
BOUNDARY: Read-only. services/ only.
DONE-WHEN: every service has its clause quoted, or "none found".
```

**Finishing check:** the receiver can start without asking a question.
