# Security

## Reporting a vulnerability

Please report security issues via GitHub's private vulnerability reporting
(Security tab → "Report a vulnerability"), enabled on this repo. Do not open
a public issue for a suspected vulnerability.

There is no SLA on response time — this is a personal project maintained on
a best-effort basis.

## Scope

This project ships prompt/Markdown artifacts (agent and skill definitions)
plus a handful of small shell scripts under `scripts/`. There is no
application code, server, or network service, though
`scripts/watchdog-resume.sh` launches detached `tmux` sessions once wired
up.

Two maintainer-run helpers live in `.claude/scripts/`, not `scripts/`. They
are in the repository but are not plugin scripts: `.claude/` is repo-internal
and is never registered as a plugin surface. `.claude/scripts/tg-notify.sh`
reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the environment or
`~/.claude/channels/telegram/.env` and makes an outbound call to the Telegram
API. `.claude/scripts/setup-watchdog.sh` is the only script you run to
install anything on your machine (if you choose to) — it symlinks the notify
script and `scripts/watchdog-resume.sh` into `~/.claude/` and writes a
LaunchAgent plist; its header comments document what it links and writes.
