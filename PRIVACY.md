# Privacy

maddog is a set of agent definitions, skills, hooks, workflows and
scripts that run inside Claude Code on your machine. It has no server and
collects no data. It sends nothing anywhere unless you run one of the
steps listed below.

## What runs, and what it touches

- **Hooks.** `scripts/executor-guard.sh` and `scripts/judge-dispatch-guard.sh`
  read the pending tool call that Claude Code passes them, and answer allow
  or deny. They keep nothing. When you set `MADDOG_DISPATCH_PROBE`, the
  dispatch guard appends every agent dispatch it sees, including the full
  prompt text, to `maddog-dispatch-probe.log` in `$TMPDIR` (or `/tmp`) on
  your machine.
- **Agents and skills.** These are instructions that Claude Code loads. Your
  prompts and files go to Anthropic through Claude Code, under Anthropic's
  terms. Some agents use Claude Code's web and browser tools: `researcher`
  and `executor-fast-read` search and fetch web pages, and `product-qa`
  drives a browser. Those requests go to the sites they visit.
- **`sdd-task-loop` ship step (opt-in).** When you run the workflow with
  shipping turned on, an agent pushes your branch to your git remote and
  opens a pull request with `gh`.
- **Telegram notifier (opt-in).** `.claude/scripts/tg-notify.sh` runs only
  if you set it up with `.claude/scripts/setup-watchdog.sh`. It then sends
  the progress messages you configure to the Telegram Bot API, using your
  own bot token and chat ID.

## Contact

Questions: https://github.com/Harish-here/maddog/issues
