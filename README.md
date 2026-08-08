# maddog-skills

A four-tier advisor–executor hierarchy for [Claude Code](https://claude.com/claude-code): global agents and skills that run your coding agent as an **organisation**, not an assistant.

## The hierarchy

| Tier | Model | Role |
|---|---|---|
| **Advisor** | your session model (skill: `advisor-mode`) | Executive. Holds the full context, owns architecture, scope, and cross-task tradeoffs. Never does mechanical work. |
| **executor-lead** | Opus | Package lead. Takes ONE complex work package (goal + boundary + DONE-WHEN), makes the within-package design calls, and dispatches executors for every edit and every recon step. Never touches a file itself. |
| **executor-smart** | Sonnet | Single tasks that still carry local judgment: pattern-matching refactors, context-dependent edits, small design choices inside a fixed boundary. |
| **executor-fast** | Haiku | The default. Everything mechanical with objective acceptance criteria: bulk edits, test/lint runs, search, extraction, boilerplate. |

**The routing rule:** route on the *task's shape*, never the *subject's sophistication*. A deep architecture question answered by "quote the code with file:line" is still extraction — and extraction is fast-tier work.

**Escalation is earned, not assumed:**

- Open decisions confined to one task → `executor-smart`.
- Multiple tasks AND mid-flight judgment (step N's result shapes step N+1) → `executor-lead`.
- A flat parallel fan-out of independent mechanical tasks needs no middle manager — the Advisor dispatches fast-tier directly.
- WHETHER/WHAT to build stays with the Advisor; HOW to build it can go to the lead.

## Why not just "use the best model for everything"?

The hierarchy isn't built on models — it's built on the **distillation of intelligence**. The tiers are levels of judgment: who decides what to build, who decides how, who handles ambiguity, who executes what's fully specified. Models just fill the roles; decommission one and you re-hire the role, you don't redesign the org. Spend maximum intelligence only where it's irreplaceable — everything else flows downhill, fully specified, to whoever's cheapest and fastest.

## What's in here

```
agents/
  executor-fast.md    # Haiku — mechanical executor
  executor-smart.md   # Sonnet — local-judgment executor
  executor-lead.md    # Opus — package lead (delegate-only: no Write/Edit)
skills/
  advisor-mode/       # /advisor-mode <goal> — run a session as the Advisor
  grind/              # /grind <task> — one mechanical task, isolated context
  grind-pro/          # /grind-pro <task> — one local-judgment task, isolated context
workflows/
  sdd-task-loop.js    # frozen-brief execution loop (Workflow tool) — see below
scripts/
  tg-notify.sh                       # fire-and-forget Telegram checkpoint pings (used by the loop)
  watchdog-resume.sh                 # LaunchAgent: relaunches a paused unattended run once resume_at passes
  com.maddog.watchdog-resume.plist   # LaunchAgent template (__HOME__ placeholder — install.sh substitutes it)
```

Agents and skills ship together: `grind`/`grind-pro` reference `executor-fast`/`executor-smart` by name, and `advisor-mode` orchestrates all three — installing only half breaks the other half.

## Install

**As a plugin (recommended)** — inside any Claude Code session:

```
/plugin marketplace add Harish-here/maddog-skills
/plugin install maddog-skills@maddog
```

Skills arrive namespaced (`/maddog-skills:advisor-mode`, `/maddog-skills:grind`, …). Update later with `/plugin marketplace update maddog`.

**As plain files (symlink mode)** — if you'd rather own the files in `~/.claude/` and hack on them:

```bash
git clone https://github.com/Harish-here/maddog-skills.git
cd maddog-skills && ./install.sh
```

`install.sh` symlinks `agents/*` and `skills/*` into `~/.claude/`, so the clone stays the single source of truth — edit here, commit here, every session reads the latest. Existing real files at the target are backed up to `<name>.bak`, never deleted. Skills are un-namespaced in this mode (`/advisor-mode`, `/grind`).

Pick one mode, not both — installing both ways gives you duplicate agents. Restart Claude Code sessions after installing (the agent registry snapshots at session start).

## Usage

```
/advisor-mode migrate the config loader to zod and fix every caller
/grind run the test suite and summarize failures
/grind-pro refactor src/http/retry.ts to match the backoff pattern in src/queue/
```

Or name a tier directly in any prompt: *"Use the executor-fast subagent to …"*.

## The sdd-task-loop workflow

`workflows/sdd-task-loop.js` is the Advisor's unattended execution engine (Claude Code `Workflow` tool): once a plan's briefs are **frozen** (all design decisions closed), it runs a brief-lint entry gate, one fresh implementer per task (dependency-aware parallelism opt-in), immediate reviews for flagged tasks, an end-of-plan review wave (dimension readers + adversarial Opus synthesis on big diffs), one fix round with scoped re-review, and an optional ship tail (push + PR — never merge).

Intelligence is budgeted, never inherited: every `agent()` call pins its model — Haiku for lint/dossier/ship mechanics, Sonnet for implementation and dimension reviews, Opus only for adversarial synthesis and re-reviews. Checkpoints ping Telegram through `scripts/tg-notify.sh` (template `🔁 <run> · ✅ 7/11 task-7 done (sha) · gate ✓`), riding on agents already running — zero extra agents. The launcher's duties (writing `resume.state` for `watchdog-resume.sh`'s LaunchAgent before launch, run-start/complete pings, one auto-`resumeFromRunId` on harness death) are spelled out in the script's `whenToUse` header.

`tg-notify.sh` reads `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from `~/.claude/channels/telegram/.env` (never versioned) and always exits 0 — a dead network can't fail a run.

**Note:** workflows install in **symlink mode only** — the plugin/marketplace mechanism doesn't ship `workflows/`.

## Unattended runs

`watchdog-resume.sh` relaunches a paused unattended Claude session once its resume
time passes — inside detached tmux, so permission prompts still wait for a human
(Telegram pages you) while everything else proceeds unattended.

It runs as a **LaunchAgent, not cron**: launchd `gui/` sessions reach the login
keychain, cron does not (live-tested 2026-08-08: cron → `Not logged in`; LaunchAgent
→ authenticated, prompt answered). `install.sh` symlinks the script into
`~/.claude/watchdogs/` and generates the LaunchAgent plist from
`scripts/com.maddog.watchdog-resume.plist` (its `__HOME__` placeholder gets
substituted with your `$HOME`); it prints the `launchctl bootstrap` command as a
next step rather than running it for you.

**`resume.state` contract** (one `key=value` per line, written by the agent at pause
time, consumed on a verified relaunch):

- `mode=standing|<anything else>` — `standing` persists across relaunches (e.g. a
  crash-loop guard, not a one-shot resume); anything else is one-shot.
- `resume_at=<epoch seconds>` — must be all-digits or the run is treated as malformed.
- `cwd=<path>` — working directory for the relaunched session.
- `prompt=<text>` — **must be a single line**; it's sent verbatim via
  `tmux send-keys -l`, so a newline would submit early.
- `session=<tmux session name>` — optional, defaults to `claude-resume`.

Attach to a relaunched session with `tmux attach -t <session>` (from Ghostty, SSH,
or your phone).

**Workflow/launch-contract changes need a session restart.** A running Claude Code
session snapshots `workflows/sdd-task-loop.js` and its launch contract at session
start — editing the workflow mid-run doesn't reach the live session. Use the
workflow's `scriptPath` option to launch same-session edits instead of relying on a
running session to pick up a rewritten workflow file.
