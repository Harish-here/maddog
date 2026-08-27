# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

maddog is a Claude Code plugin: agent definitions, skills, and one workflow
script that install into `~/.claude/` via `/plugin install`. There is **no
application code** — the deliverables are Markdown prompts. Nothing here
compiles, and nothing runs in CI.

## Install

```
/plugin marketplace add Harish-here/maddog
/plugin install maddog@maddog
```

Skills arrive namespaced (`/maddog:advisor-mode`). Ships
`workflows/sdd-task-loop.js` (general-usage plan execution) but not
`agent-evals` — that lives in `.claude/workflows/`, invoked only via
`scriptPath` for maintainer use, never auto-registered for installers.

## Commands

There is no package.json, test suite, linter, or CI — do not go looking for
one, and do not invent a build or test command. Changes are verified by
exercising them (see Validation).

`scripts/setup-watchdog.sh` is the one script a user runs by hand — it wires
the watchdog LaunchAgent and Telegram notify script for unattended
`sdd-task-loop` runs. It writes the plist but deliberately does not load it;
it prints the next step:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.maddog.watchdog-resume.plist
```

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

**`executor-lead` and `executor-judge` have no `Write`/`Edit` in their `tools:` lists.**
The lead is delegate-only (every file change flows through an executor it spawns); the
judge is fix-less (it rules, it never repairs — findings route back to the caller).
Removing those tools is half the enforcement: both hold `Bash`, so
`scripts/executor-guard.sh` also denies the common file-writing Bash forms for lead and
judge — redirection (including the glued `echo x>f`), `tee`, `sed -i`, `rm`, `cp`, `mv`,
`git add/commit/rm/mv`, and inline interpreters (`python`, `node`, `perl`, `ed`, `xargs`).
It is a guard, not a proof: only the first token of each command segment is
classified, so anything that shifts the dangerous verb off that position —
command substitution, `bash -c`, a `git -C` global option, a `sudo`/`env`/`time`
prefix, shell grouping — passes unexamined, and hooks fail open on a payload
they cannot read. Granting either agent `Write`/`Edit`, or weakening that layer,
silently dissolves the family's central invariants. One route stays open by
design: the judge holds `Agent` and may rent `executor-fast`, which can write —
that containment is instruction, not structure. The shared RENT HANDS, NEVER
VERDICTS law is verbatim-identical in both files — edit it in both or neither.
`scripts/executor-guard.sh` covers all four executors: irreversible commands
(`git merge` and `git worktree remove` included) for every one, plus the
file-write denial for lead and judge alone.

**Agents and skills ship as a unit.** `product-engineering` names all five
`product-*` agents plus `researcher`; `advisor-mode` routes the whole executor
family by judgment class and offers the product pipeline when installed.
Renaming an agent means updating every by-name reference across `skills/` and
`workflows/`.

## Architecture

Two orthogonal axes.

**Judgment tiers** — route on the task's *shape*, never the subject's sophistication.
A deep architecture question answered by "quote the code with file:line" is still
extraction, and extraction is fast-tier.

| Agent | Tier | Takes |
|---|---|---|
| `executor-fast` | cheap | mechanical work with objective acceptance criteria |
| `executor-smart` | mid | one task carrying local judgment inside a fixed boundary |
| `executor-lead` | top | judgment with memory for ONE package: PLAN (open decomposition → frozen plan), CAMPAIGN (unfreezable, evidence-driven probes), DELIVER (decided scope entangled with live reality). Burst-dispatched; never orchestrates — execution belongs to workflow scripts |
| `executor-judge` | top | adversarial gate verdicts on another intelligence's output: DESIGN-REVIEW, CHANGE-REVIEW, ADJUDICATE. Cannot fix by construction |

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
explicitly — in `workflows/sdd-task-loop.js`, cheap-tier for lint/dossier/ship mechanics,
mid-tier for implementation and dimension reviews, top-tier only for adversarial synthesis.
When adding a dispatch, pin the tier deliberately; silently inheriting the caller's
model is a bug, not a default. The full doctrine — judgment classes as identity, model pins as an exchange-rate
table stated once — lives in the README; agent files are defined by judgment class
and must never treat a model name as identity.

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
