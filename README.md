# maddog

A five-role advisor–executor hierarchy for [Claude Code](https://claude.com/claude-code): global agents and skills that run your coding agent as an **organisation**, not an assistant.

## The hierarchy

| Tier | Judgment class | Role |
|---|---|---|
| **Advisor** | architectural / cross-package | Executive. Holds the full context, owns architecture, scope, and cross-task tradeoffs. Never does mechanical work. |
| **executor-lead** | iterated (judgment with memory) | Judgment with memory, hands always delegated. Dispatched per judgment burst for an open decomposition (PLAN), an unfreezable evidence-driven campaign (CAMPAIGN), or decided-scope delivery entangled with a live/hazardous environment (DELIVER). Continuity lives in artifacts — a plan, a decision ledger — never in a live context. Not an orchestrator: babysitting execution is a workflow script's job. Never touches a file itself. |
| **executor-judge** | adversarial verdict | Adversarial verdicts on another intelligence's output: plan/design review before execution (DESIGN-REVIEW), executed-change review after (CHANGE-REVIEW), or adjudicating a dispute that gates progression (ADJUDICATE). Rules only on primary evidence it reads itself. Cannot fix by construction — no Write/Edit. |
| **executor-smart** | local | Single tasks that still carry local judgment: pattern-matching refactors, context-dependent edits, small design choices inside a fixed boundary. |
| **executor-fast** | none (mechanical) | The default. Everything mechanical with objective acceptance criteria: bulk edits, test/lint runs, search, extraction, boilerplate. |

**The routing rule:** route on the *task's shape*, never the *subject's sophistication*. A deep architecture question answered by "quote the code with file:line" is still extraction — and extraction is fast-tier work.

**Escalation is earned, not assumed:**

- Open decisions confined to one task → `executor-smart`.
- An open decomposition to freeze into a plan, an unfreezable evidence-driven campaign, or decided-scope delivery entangled with a live/hazardous environment → `executor-lead`.
- A verdict on another intelligence's output — before execution, after it, or adjudicating a dispute that gates progression → `executor-judge`.
- A flat parallel fan-out of independent mechanical tasks needs no middle manager — the Advisor dispatches fast-tier directly.
- WHETHER/WHAT to build stays with the Advisor; HOW to build it can go to the lead; whether it PASSED goes to the judge, never to whoever built it.

## Doctrine: intelligence is the budget

Intelligence is the budget, and it has two axes: **tier** (quality of judgment) and
**context** (attention).

- Closed decisions cost zero intelligence — they go to scripts/workflows, or to the
  cheapest tier when a model is needed only for perception.
- Open decisions go to the cheapest tier whose judgment class covers them.
- Judgment that accumulates working state gets a disposable container (a dispatched
  agent), never the caller's context.
- Orchestration/choreography is never an intelligence spend: when decisions are
  closed, a script out-manages any model, for free, deterministically.
- Top-tier intelligence concentrates at exactly three kinds of work: open
  decomposition (including its small, live-entangled form), unfreezable
  evidence-driven campaigns, and adversarial gate verdicts on another
  intelligence's output. Buy the open-decomposition/campaign kind only when
  the package must survive outside the advisor's own context — absence,
  parallelism with the main thread, or context scarcity; an attended
  package held as the session's main thread is judgment the advisor's own
  ledger already carries, and stays with the advisor.

Judgment classes are decoupled from models. The table below is an
**exchange-rate table** — today's cheapest model clearing each class — not the
definition of the role: agent files are defined by judgment class, and re-pinning
a model to a class never touches the role it fills.

| Judgment class | Agent | Today's pin |
|---|---|---|
| none (mechanical, decisions closed) | `executor-fast` | haiku |
| local (one task, fixed boundary) | `executor-smart` | sonnet |
| iterated (judgment with memory, one package) | `executor-lead` | opus |
| adversarial verdict (gates) | `executor-judge` | opus |
| architectural / cross-package | Advisor (session model) | — |
| zero (choreography) | workflow scripts | none |

## Modes and laws

Each executor classifies every task it receives into one of its own **modes**, and each
mode carries one named **law** with a worked example. `executor-fast` has ten: RECON,
EXTRACT, VERIFY, EDIT, TRANSFORM, GATE, OPERATE, RECOVER, DIAGNOSE, IMPLEMENT.
`executor-smart` has eight: BUILD, PORT, AUTHOR, DECOMPOSE, FIX, REVIEW, DIAGNOSE,
CHOREOGRAPH. `executor-lead` has three: PLAN, CAMPAIGN, DELIVER. `executor-judge` has
three: DESIGN-REVIEW, CHANGE-REVIEW, ADJUDICATE.

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

The fast/smart modes were derived from 774 real dispatches in local session history,
then extended with four synthesised forward. Lead's and judge's modes are new, designed
directly against the doctrine's judgment classes rather than mined from history.

## Why not just "use the best model for everything"?

The hierarchy isn't built on models — it's built on the **distillation of intelligence**. The tiers are levels of judgment: who decides what to build, who decides how, who handles ambiguity, who executes what's fully specified. Models just fill the roles; decommission one and you re-hire the role, you don't redesign the org. Spend maximum intelligence only where it's irreplaceable — everything else flows downhill, fully specified, to whoever's cheapest and fastest.

## What's in here

```
agents/
  executor-fast.md    # Mechanical executor, ten modes
  executor-smart.md   # Local-judgment executor, eight modes
  executor-lead.md    # Judgment with memory: PLAN / CAMPAIGN / DELIVER (delegate-only: no Write/Edit)
  executor-judge.md   # Adversarial gate verdicts: DESIGN-REVIEW / CHANGE-REVIEW / ADJUDICATE (cannot fix by construction: no Write/Edit)
  researcher.md       # Mechanical web research (capped, cited, no synthesis)
  product-pm.md       # Feature ask → grounded product spec (product-engineering stage 1)
  product-ux.md       # Spec → UX dossier + rendered HTML mockup (stage 2)
  product-be.md       # UX data needs → server contracts + backend blueprint (stage 3)
  product-ui.md       # Mockup + BE contracts → zero-drift implementation blueprint (stage 4)
  product-qa.md       # Implemented branch → traceability matrix, routed bugs, PR at zero open bugs (final stage)
skills/
  advisor-mode/       # /advisor-mode <goal> — run a session as the Advisor
  mine-session/       # /mine-session — arm capture early, distill at session end; mines surprise, not activity
  product-engineering/       # /product-engineering <feature> — PM → UX → BE → UI planning, sdd-task-loop execution, QA → PR
workflows/
  sdd-task-loop.js    # frozen-brief execution loop (Workflow tool) — see below
  agent-evals.js      # runs evals/ fixtures against the real agents and grades them
evals/
  executor-fast.json  # behavioural fixtures — happy + trap per mode and standing law
  executor-smart.json
  executor-lead.json  # lean set: happy PLAN + trap frozen-plan (RENT HANDS asserted inline)
  executor-judge.json # lean set: happy CHANGE-REVIEW + trap fix-leak
  README.md           # fixture schema, and why the traps are the point
scripts/
  executor-guard.sh                  # PreToolUse hook: denies irreversible Bash commands on executor-fast, executor-lead, executor-judge
  tg-notify.sh                       # fire-and-forget Telegram checkpoint pings (used by the loop)
  watchdog-resume.sh                 # LaunchAgent: relaunches a paused unattended run once resume_at passes
  com.maddog.watchdog-resume.plist   # LaunchAgent template (__HOME__ placeholder — install.sh substitutes it)
```

`review-agent` is repo-internal tooling living in `.claude/skills/review-agent/` —
auto-discovered when working in this repo, not shipped in the plugin.

Agents and skills ship together: `product-engineering` references `product-pm`/`product-ux`/`product-be`/`product-ui`/`product-qa`/`researcher` by name, and `advisor-mode` routes the whole executor family by judgment class and offers the product pipeline when installed — installing only half breaks the other half.

## Install modes

Two mutually exclusive ways to install. Pick ONE — installing both gives you duplicate agents.

**Prerequisite:** `product-qa`'s live-drive verification requires the playwright MCP browser tools. Neither install mode installs it — configure it separately, or `product-qa` returns blocked at its prerequisite check.

**Plugin (recommended):**
```
/plugin marketplace add Harish-here/maddog
/plugin install maddog@maddog
```
- Skills arrive namespaced (`/maddog:advisor-mode`).
- Does NOT ship `workflows/` (`sdd-task-loop`, `agent-evals`) — the plugin format has no workflow component yet; the day it does, we ship them.
- Agent frontmatter `hooks:` / `permissionMode:` are ignored for plugin-shipped agents, so:
  - the executor guard arrives via the plugin's `hooks/hooks.json` instead (session-wide PreToolUse on Bash; the script scopes itself to executor-fast, executor-lead, and executor-judge via the payload's `agent_type`), and
  - `permissionMode: dontAsk` does not apply — executors may surface permission prompts; add allowlist entries for the commands you delegate.
- Update later with `/plugin marketplace update maddog`.

**Symlink (maintainer / power-user mode):**
```bash
git clone https://github.com/Harish-here/maddog.git
cd maddog && ./install.sh
```
- Skills un-namespaced (`/advisor-mode`); the clone stays the single source of truth — edits land in every new session.
- Ships everything the plugin can't: `workflows/`, the watchdog LaunchAgent, the Telegram notify script.
- `permissionMode: dontAsk` is active; the guard is wired via the frontmatter of executor-fast, executor-lead, and executor-judge to `$HOME/.claude/hooks/executor-guard.sh` (linked by `install.sh`).
- Existing real files at the target are backed up to `<name>.bak`, never deleted.

Restart Claude Code sessions after installing (the agent registry snapshots at session start).

### What `install.sh` does to your machine

`install.sh` (symlink mode only) is honest about the surface it touches:

- Symlinks `agents/`, `skills/`, and `workflows/` from this clone into
  `~/.claude/{agents,skills,workflows}` — nothing is copied, so edits here
  reach every new session.
- Writes a LaunchAgent plist for the watchdog to
  `~/Library/LaunchAgents/com.maddog.watchdog-resume.plist` but does **not**
  load it — it prints the `launchctl bootstrap` command as a next step
  instead of running it for you.
- The optional Telegram notifier (`scripts/tg-notify.sh`, symlinked to
  `~/.claude/channels/telegram/notify.sh`) only ever reads its bot token and
  chat ID from `~/.claude/channels/telegram/.env`, which is never versioned
  in this repo.
- Prunes only dangling symlinks that point back into this repo (e.g. a skill
  that moved or was deleted) — it never touches a regular file/dir or a
  symlink owned by another plugin or tool.
- The watchdog writes append-only logs to `~/.claude/watchdogs/resume.log`;
  they're diagnostic only and safe to delete at any time.

## Usage

```
/advisor-mode migrate the config loader to zod and fix every caller
/mine-session
/product-engineering add CSV export to the reports page
```

Or name a tier directly in any prompt: *"Use the executor-fast subagent to …"*.

## The product engineering team

A second axis on the org: discipline agents, not judgment tiers. `/product-engineering <feature>` runs the full pipeline — `product-pm` (top-tier) grounds the ask in industry research, the app's persona (`docs/product/personas.md`), and delegated recon, then interviews you and writes a spec; `product-ux` (top-tier) designs the journey against a baked-in UX charter and has the mockup rendered at mid-tier prices; `product-be` (mid-tier) turns every UX data need into a named server contract (read-path completeness, mandatory migration rehearsal) in `blueprint-be.md`; `product-ui` (mid-tier) maps the mockup to the repo's real components against those contracts, with every screen/state step carrying its pinning e2e in-task. The orchestrator then briefs both blueprints into `sdd-task-loop` for execution, and `product-qa` (top-tier) closes: verifies the branch against the artifacts (gates, e2e coverage audit, live drive, exploratory pass, full traceability matrix), routes typed bugs back to the responsible stage, and opens the PR only at zero open bugs — deferral is the user's call, merge is never the pipeline's. Artifacts land in the target repo under `docs/product/<slug>/`. Top-tier tokens are spent on judgment only: mechanical recon goes to `executor-fast`, web research to `researcher` (cheap-tier), HTML rendering to `executor-smart`. Not for small tweaks — dispatch an executor directly for those.

## The sdd-task-loop workflow

`workflows/sdd-task-loop.js` is the Advisor's unattended execution engine (Claude Code `Workflow` tool): once a plan's briefs are **frozen** (all design decisions closed), it runs a brief-lint entry gate, one fresh implementer per task (dependency-aware parallelism opt-in), immediate reviews for flagged tasks, an end-of-plan review wave (dimension readers + adversarial Opus synthesis on big diffs), one fix round with scoped re-review, and an optional ship tail (push + PR — never merge).

Intelligence is budgeted, never inherited: every `agent()` call pins its model — Haiku for lint/dossier/ship mechanics, Sonnet for implementation and dimension reviews, Opus only for adversarial synthesis and re-reviews. Checkpoints ping Telegram through `scripts/tg-notify.sh` (template `🔁 <run> · ✅ 7/11 task-7 done (sha) · gate ✓`), riding on agents already running — zero extra agents. The launcher's duties (writing `resume.state` for `watchdog-resume.sh`'s LaunchAgent before launch, run-start/complete pings, one auto-`resumeFromRunId` on harness death) are spelled out in the script's `whenToUse` header.

`tg-notify.sh` reads `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` from `~/.claude/channels/telegram/.env` (never versioned) and always exits 0 — a dead network can't fail a run.

**Note:** workflows install in **symlink mode only** — the plugin/marketplace mechanism doesn't ship `workflows/`.

## Evals

`evals/` holds behavioural fixtures — one JSON file per executor plus a schema README.
Every fast/smart mode and standing law carries at least one happy fixture and one **trap**, where
the wrong answer is cheap, plausible and immediately available. Lead and judge carry a deliberately
lean set — opus runs are expensive, so only the main happy path and the instruction-only prohibitions
get fixtures, with secondary assertions folded into the happy rubrics. A fixture that only asks
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

## Model pinning

Currently the agents and workflows are model-pinned to the Claude ecosystem (`haiku` / `sonnet` / `opus` by name) — every dispatch names its tier explicitly. Once the hierarchy matures we will abstract this out to generic capability tiers (fast / smart / lead / judge) so that any model can be pinned to a tier.

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
