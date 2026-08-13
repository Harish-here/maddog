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

## Modes and laws

Each executor classifies every task it receives into one of its own **modes**, and each
mode carries one named **law** with a worked example. `executor-fast` has ten: RECON,
EXTRACT, VERIFY, EDIT, TRANSFORM, GATE, OPERATE, RECOVER, DIAGNOSE, IMPLEMENT.
`executor-smart` has eight: BUILD, PORT, AUTHOR, DECOMPOSE, FIX, REVIEW, DIAGNOSE,
CHOREOGRAPH.

The laws are established principles rather than invented jargon — Goodhart's Law for a
gate you must not tune to make green, Chesterton's Fence for an edit whose anchor has
moved, Order of Volatility (RFC 3227) for a cleanup that would destroy the evidence of
what broke, Parnas's information hiding for choosing where to split a file. A model has
real priors on those and none at all on a coined phrase.

**Classification belongs to the agent, not the caller.** A dispatching agent sees only
the frontmatter `description`, never the mode list — so a mode named in a prompt is a
hint from someone who probably has not read the file, and the agent is told to classify
on the task and flag the mismatch. Call sites stay decoupled from each agent's internal
taxonomy.

The modes were derived from 774 real dispatches in local session history, then extended
with four synthesised forward.

## Why not just "use the best model for everything"?

The hierarchy isn't built on models — it's built on the **distillation of intelligence**. The tiers are levels of judgment: who decides what to build, who decides how, who handles ambiguity, who executes what's fully specified. Models just fill the roles; decommission one and you re-hire the role, you don't redesign the org. Spend maximum intelligence only where it's irreplaceable — everything else flows downhill, fully specified, to whoever's cheapest and fastest.

## What's in here

```
agents/
  executor-fast.md    # Haiku — mechanical executor, ten modes
  executor-smart.md   # Sonnet — local-judgment executor, eight modes
  executor-lead.md    # Opus — package lead (delegate-only: no Write/Edit)
  researcher.md       # Haiku — mechanical web research (capped, cited, no synthesis)
  product-pm.md       # Opus — feature ask → grounded product spec (product-engineering stage 1)
  product-ux.md       # Opus — spec → UX dossier + rendered HTML mockup (stage 2)
  product-be.md       # Sonnet — UX data needs → server contracts + backend blueprint (stage 3)
  product-ui.md       # Sonnet — mockup + BE contracts → zero-drift implementation blueprint (stage 4)
  product-qa.md       # Opus — implemented branch → traceability matrix, routed bugs, PR at zero open bugs (final stage)
skills/
  advisor-mode/       # /advisor-mode <goal> — run a session as the Advisor
  grind/              # /grind <task> — one mechanical task, isolated context
  grind-pro/          # /grind-pro <task> — one local-judgment task, isolated context
  product-engineering/       # /product-engineering <feature> — PM → UX → BE → UI planning, sdd-task-loop execution, QA → PR
workflows/
  sdd-task-loop.js    # frozen-brief execution loop (Workflow tool) — see below
  agent-evals.js      # runs evals/ fixtures against the real agents and grades them
evals/
  executor-fast.json  # behavioural fixtures — happy + trap per mode and standing law
  executor-smart.json
  README.md           # fixture schema, and why the traps are the point
scripts/
  executor-guard.sh                  # PreToolUse hook: denies irreversible Bash commands on executor-fast
  tg-notify.sh                       # fire-and-forget Telegram checkpoint pings (used by the loop)
  watchdog-resume.sh                 # LaunchAgent: relaunches a paused unattended run once resume_at passes
  com.maddog.watchdog-resume.plist   # LaunchAgent template (__HOME__ placeholder — install.sh substitutes it)
```

Agents and skills ship together: `grind`/`grind-pro` reference `executor-fast`/`executor-smart` by name, `product-engineering` references `product-pm`/`product-ux`/`product-be`/`product-ui`/`product-qa`/`researcher` by name, and `advisor-mode` orchestrates all three — installing only half breaks the other half.

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

## The product engineering team

A second axis on the org: discipline agents, not judgment tiers. `/product-engineering <feature>` runs the full pipeline — `product-pm` (Opus) grounds the ask in industry research, the app's persona (`docs/product/personas.md`), and delegated recon, then interviews you and writes a spec; `product-ux` (Opus) designs the journey against a baked-in UX charter and has the mockup rendered at Sonnet prices; `product-be` (Sonnet) turns every UX data need into a named server contract (read-path completeness, mandatory migration rehearsal) in `blueprint-be.md`; `product-ui` (Sonnet) maps the mockup to the repo's real components against those contracts, with every screen/state step carrying its pinning e2e in-task. The orchestrator then briefs both blueprints into `sdd-task-loop` for execution, and `product-qa` (Opus) closes: verifies the branch against the artifacts (gates, e2e coverage audit, live drive, exploratory pass, full traceability matrix), routes typed bugs back to the responsible stage, and opens the PR only at zero open bugs — deferral is the user's call, merge is never the pipeline's. Artifacts land in the target repo under `docs/product/<slug>/`. Opus tokens are spent on judgment only: mechanical recon goes to `executor-fast`, web research to `researcher` (Haiku), HTML rendering to `executor-smart`. Not for small tweaks — dispatch an executor directly for those.

## The sdd-task-loop workflow

`workflows/sdd-task-loop.js` is the Advisor's unattended execution engine (Claude Code `Workflow` tool): once a plan's briefs are **frozen** (all design decisions closed), it runs a brief-lint entry gate, one fresh implementer per task (dependency-aware parallelism opt-in), immediate reviews for flagged tasks, an end-of-plan review wave (dimension readers + adversarial Opus synthesis on big diffs), one fix round with scoped re-review, and an optional ship tail (push + PR — never merge).

Intelligence is budgeted, never inherited: every `agent()` call pins its model — Haiku for lint/dossier/ship mechanics, Sonnet for implementation and dimension reviews, Opus only for adversarial synthesis and re-reviews. Checkpoints ping Telegram through `scripts/tg-notify.sh` (template `🔁 <run> · ✅ 7/11 task-7 done (sha) · gate ✓`), riding on agents already running — zero extra agents. The launcher's duties (writing `resume.state` for `watchdog-resume.sh`'s LaunchAgent before launch, run-start/complete pings, one auto-`resumeFromRunId` on harness death) are spelled out in the script's `whenToUse` header.

`tg-notify.sh` reads `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from `~/.claude/channels/telegram/.env` (never versioned) and always exits 0 — a dead network can't fail a run.

**Note:** workflows install in **symlink mode only** — the plugin/marketplace mechanism doesn't ship `workflows/`.

## Evals

`evals/` holds behavioural fixtures — one JSON file per executor plus a schema README.
Every mode and standing law carries at least one happy fixture and one **trap**, where
the wrong answer is cheap, plausible and immediately available. A fixture that only asks
an agent to do the obvious right thing proves nothing, because the wrong answer was never
attractive.

`workflows/agent-evals.js` runs them: it materialises each fixture's files into a fresh
temp directory, dispatches the prompt to the real agent, and grades the return against
the fixture's expectations with a judge. Model and reasoning effort are pinned per
fixture — an eval of a Haiku agent that runs on Opus measures nothing — and the harness
stages deliberately avoid the agents under test, so a broken executor cannot masquerade
as fixture failures. Fixtures carry a `core` flag and the runner defaults to the
discriminating subset; `args.all` runs everything.

They found real defects. At low effort `executor-fast` deleted a directory holding
uncommitted work and reported done; at medium `executor-smart` verified a review finding
was refuted and then applied it anyway. Both agents pin `effort: high` because of that.

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
