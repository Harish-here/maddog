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
```

Agents and skills ship together: `grind`/`grind-pro` reference `executor-fast`/`executor-smart` by name, and `advisor-mode` orchestrates all three — installing only half breaks the other half.

## Install

```bash
git clone https://github.com/Harish-here/maddog-skills.git
cd maddog-skills && ./install.sh
```

`install.sh` symlinks `agents/*` and `skills/*` into `~/.claude/`, so the clone stays the single source of truth — edit here, commit here, every session reads the latest. Existing real files at the target are backed up to `<name>.bak`, never deleted. Restart Claude Code sessions to pick up changes (the agent registry snapshots at session start).

## Usage

```
/advisor-mode migrate the config loader to zod and fix every caller
/grind run the test suite and summarize failures
/grind-pro refactor src/http/retry.ts to match the backoff pattern in src/queue/
```

Or name a tier directly in any prompt: *"Use the executor-fast subagent to …"*.
