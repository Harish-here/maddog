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
`scripts/dev/watchdog-resume.sh` launches detached `tmux` sessions once wired
up.

One maintainer-run helper lives in `.claude/scripts/`, not `scripts/`. It is
in the repository but is not a plugin script: `.claude/` is repo-internal
and is never registered as a plugin surface.
`.claude/scripts/setup-watchdog.sh` is the only script you run to install
anything on your machine (if you choose to) — it symlinks
`scripts/dev/watchdog-resume.sh` into `~/.claude/` and writes a LaunchAgent
plist; its header comments document what it links and writes. The
repository ships no notification script and reads no credentials. The
maintainer's own Telegram notify script lives outside the repository.
