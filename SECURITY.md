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
application code, server, or network service. `install.sh`'s behavior —
what it symlinks, writes, and reads on your machine — is documented in
`README.md`.
