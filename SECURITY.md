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
`scripts/tg-notify.sh` makes an outbound call to the Telegram API and
`scripts/watchdog-resume.sh` launches detached `tmux` sessions once wired
up. `scripts/setup-watchdog.sh` is the only script you run to install
anything on your machine (if you choose to) — what it symlinks and writes
is documented in `README.md`.
