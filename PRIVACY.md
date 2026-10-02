# Privacy

maddog is a set of agent definitions, skills, hooks and scripts that run
inside Claude Code on your machine. It has no server, collects no data,
and sends nothing anywhere on its own.

## What runs, and what it touches

- **Hooks.** `scripts/executor-guard.sh` and `scripts/judge-dispatch-guard.sh`
  read the pending tool call that Claude Code passes them, and answer allow
  or deny. They keep nothing. When you set `MADDOG_DISPATCH_PROBE`, the
  dispatch guard appends debug lines to `$TMPDIR/maddog-dispatch-probe.log`
  on your machine.
- **Agents and skills.** These are instructions that Claude Code loads. Your
  prompts and files go to Anthropic through Claude Code itself, under
  Anthropic's terms, never through maddog.
- **Telegram notifier (opt-in).** `.claude/scripts/tg-notify.sh` runs only
  if you set it up with `.claude/scripts/setup-watchdog.sh`. It then sends
  the progress messages you configure to the Telegram Bot API, using your
  own bot token and chat ID. Nothing else in maddog makes a network call.

## Contact

Questions: https://github.com/Harish-here/maddog/issues
