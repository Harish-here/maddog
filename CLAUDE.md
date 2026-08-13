# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

maddog-skills is a Claude Code plugin: agent definitions, skills, and one workflow
script that install into `~/.claude/`. There is **no application code** — the
deliverables are Markdown prompts. Nothing here compiles, and nothing runs in CI.

## Commands

```bash
./install.sh    # symlink agents/, skills/, workflows/ into ~/.claude (idempotent)
```

That is the only command. There is no package.json, test suite, linter, or CI —
do not go looking for one, and do not invent a build or test command. Changes are
verified by exercising them (see Validation).

`install.sh` writes the watchdog LaunchAgent plist but deliberately does not load
it; it prints the next step:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.maddog.watchdog-resume.plist
```

## The two install modes are mutually exclusive

- **Plugin:** `/plugin marketplace add Harish-here/maddog-skills` then
  `/plugin install maddog-skills@maddog`. Skills arrive namespaced
  (`/maddog-skills:grind`). **Does not ship `workflows/`.**
- **Symlink:** `./install.sh`. Skills un-namespaced (`/grind`). The clone stays the
  single source of truth — edit here, every session reads the latest.

Installing both ways gives you duplicate agents.

## Things that are easy to get wrong

**A running session snapshots agents, skills, and workflows at session start.**
Editing a file mid-session does not affect the live session — restart it. To test a
workflow edit immediately, launch it via the `scriptPath` option instead of relying
on a running session to pick up the rewritten file.

**The frontmatter `description` is the router; the body is the behavior.** Claude
Code selects a subagent by matching its `description`, so description wording is
load-bearing dispatch logic, not documentation — it gets tuned against evals (see
commits `1eca87e`, `7d30742`). Change behavior in the body; change routing in the
description. Do not casually reword a description while editing the body.

**`executor-lead` has no `Write`/`Edit` in its `tools:` list.** Delegate-only is
enforced by tool restriction, not by instruction. Granting it those tools would
silently dissolve the hierarchy's central invariant.

**Agents and skills ship as a unit.** `grind`/`grind-pro` name
`executor-fast`/`executor-smart`; `product-engineering` names all five `product-*`
agents plus `researcher`; `advisor-mode` orchestrates all of them. Renaming an agent
means updating every by-name reference across `skills/` and `workflows/`.

## Architecture

Two orthogonal axes.

**Judgment tiers** — route on the task's *shape*, never the subject's sophistication.
A deep architecture question answered by "quote the code with file:line" is still
extraction, and extraction is fast-tier.

| Agent | Model | Takes |
|---|---|---|
| `executor-fast` | haiku | mechanical work with objective acceptance criteria |
| `executor-smart` | sonnet | one task carrying local judgment inside a fixed boundary |
| `executor-lead` | opus | a package needing multiple tasks AND mid-flight judgment |

`executor-fast` classifies every task into one of ten modes — RECON, EXTRACT, VERIFY,
EDIT, TRANSFORM, GATE, OPERATE, RECOVER, DIAGNOSE, IMPLEMENT — each carrying one named
law.
The mode set was derived from real dispatch history; add a mode only when a genuine
usage cluster demands it, not to cover a hypothetical.

**Discipline agents** — the `product-engineering` pipeline. Strictly ordered, each
stage gated by the orchestrator skill and requiring the prior stage's artifacts:

`product-pm` (spec.md) → `product-ux` (ux-notes.md + mockup.html) → `product-be`
(blueprint-be.md) → `product-ui` (blueprint.md) → `sdd-task-loop` execution →
`product-qa` (qa-report.md, opens the PR at zero open bugs)

Artifacts land in the **target** repo under `docs/product/<slug>/`, never in this
one. The per-stage gates live in `skills/product-engineering/SKILL.md`.

**Intelligence is budgeted, never inherited.** Every dispatch pins its model
explicitly — in `workflows/sdd-task-loop.js`, haiku for lint/dossier/ship mechanics,
sonnet for implementation and dimension reviews, opus only for adversarial synthesis.
When adding a dispatch, pin the tier deliberately; silently inheriting the caller's
model is a bug, not a default.

## sdd-task-loop

`workflows/sdd-task-loop.js` executes **frozen** briefs — all design decisions closed
— through: brief lint → implement (deps-aware parallelism) → flagged review → end-of-plan
review wave → one fix round → optional ship (push + PR, **never merge**).

Its `meta.whenToUse` header carries a **LAUNCH CONTRACT**: duties the script cannot
perform for itself (watchdog LaunchAgent, run-start/complete pings, persisting
`scriptPath` + `runId`, the `resume.state` lifecycle). Read that header before
launching, and keep it in sync when you change launch behavior — it encodes
post-mortems, not preferences.

## Validation

There are no tests. A change is validated by exercising it:

- **Agent body change** → dispatch that agent on a representative task; confirm it
  obeys the new instruction rather than assuming it will.
- **Agent description change** → this is routing. Confirm the intended task shape
  still selects it, and that neighbouring shapes still don't.
- **Workflow change** → launch with `scriptPath`. `resumeFromRunId` replays cached
  agent calls for free, so iterating on a late phase costs nothing to re-reach.

## Conventions

Conventional commits, scoped to the surface touched: `feat(product-engineering):`,
`fix(executors):`, `docs(watchdog):`, `chore:`. Bump `version` in
`.claude-plugin/plugin.json` when the shipped agent/skill set changes.
