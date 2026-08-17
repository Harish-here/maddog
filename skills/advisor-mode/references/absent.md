# Absent liturgy — read before any unattended dispatch (any dispatch whose return the user will not be present for)

You are now the only supervision this work has. This file is procedure for
that condition; it relaxes no law in the core. Absence is not license —
budgets and prohibitions bind exactly as before.

## 1. FIRST ARTIFACT — the supervision stack (before your next dispatch)
No unattended dispatch until all three exist. Evidence: 2026-08-05 lost
11.8 hours to a host restart with no watchdog.
- WATCHDOG + HEARTBEAT: create the stall-detection watcher (LaunchAgent or
  equivalent) and send the run-start ping via the session's notify channel
  — discovered per session, never assumed (e.g.
  ~/.claude/channels/telegram/notify.sh if present; otherwise append to
  the run-state file — never skip signaling entirely). If no stall-detection facility
  exists on this machine, unattended launch is off: say so BEFORE the user
  leaves and get an explicit accept-the-risk, or keep the work attended.
  Per install mode: plugin installs ship no workflows/, no watchdog, no
  notify script, so this trigger fires by default until the user accepts
  the risk; symlink installs get the watchdog LaunchAgent from install.sh,
  but it is not loaded automatically — confirm it is actually bootstrapped
  before assuming coverage.
- RESUME RECORD: the moment any launch returns, persist what a fresh session
  needs to relaunch this exact work — for a workflow harness, its script
  path and run id; for a hosted session, its name and a one-line resume
  prompt; for anything else, the command that restarts it.
- LEDGER DURABILITY: the session's decision ledger already exists (core
  LEDGER LAW — one file; create no second one here). Move it, plus a
  copy of every scratch-resident artifact its entries cite, to a
  durable path outside session scratch (e.g. ~/.claude/ledgers/<slug>/),
  then rewrite those scratch citations to the durable copies — the path
  rewrite is the one sanctioned edit of a filed entry; repo and durable
  citations stay put. A citation the returning user or a fresh session
  cannot open is not a citation.
If the work is a workflow that carries its own LAUNCH CONTRACT in its
whenToUse header, execute that contract too — it encodes post-mortems the
generic stack does not.

If scripts/unattended-start.sh exists in the family repo, run it — it
discharges this whole section in one command.

## 2. DECISIONS WHILE ABSENT (the OPEN + ABSENT cell)
- Within the boundary: decide, append the entry per the core LEDGER LAW,
  continue. No stalls for callable judgment.
- Surface the ledger as ONE batch at closure or on the user's return —
  never as a drip, never silently absorbed.
- HARD BLOCKERS — pause the run and page, never decide alone: boundary-
  crossing scope, security, user data, contract/instruction-file changes,
  and any hard-to-reverse outward action not pre-authorized in the
  front-loaded batch.

## 3. DISPATCH WHILE ABSENT
- Nothing downstream can surface a permission prompt. The pre-clearance and
  pre-authorizations were bought while the user was present (core, BUDGET 3);
  VERIFY they cover every tool this run will need BEFORE launching; run
  write dispatches foreground; then CONFIRM each long dispatch actually
  started — a stuck permission prompt once idled a run for hours. If the
  session had no present phase at all — no pre-clearance was ever bought,
  because there was no one present to buy it from — unattended dispatch is
  limited to tools already allowlisted in settings; anything beyond that
  blocks and goes to the surfacing batch, never gets attempted on a guess.
- Watching and acting are separate invocations: a watch job (CI, deploy,
  queue) is a cron/monitor; the consequent irreversible step waits for the
  user's return or its own pre-authorization. Never bundle them.

## 4. FAILURE AND RECOVERY
- Harness error or restart: attempt ONE cheap resume (cached replay /
  resumeFromRunId) before paging the human.
- When paging: write current state to the resume record FIRST, then ping —
  a page that dies with the session helps nobody.
- Two failures on the same recovery path: stop the run cleanly, record
  state, page, wait.

## 5. CLOSURE
- Send the run-complete (or aborted) ping through the same channel that
  got the run-start.
- The closure report is the batch: ledger decisions, deviations, blocked
  items, and the verification artifacts that prove DONE-WHEN — claims
  cited to artifacts, per the core's acceptance law.
- On the user's return mid-run: interrupt rule from the core applies —
  freeze, then surface this batch immediately.
