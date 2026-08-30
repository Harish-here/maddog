# CLAUDE.md

This file guides Claude Code working IN this repo (maddog plugin source) —
not consumer context for the plugin itself.

## What this is

No application code — deliverables are Markdown agent/skill prompts, one
Workflow script, and shell scripts, installed via `/plugin install`. Nothing
compiles; CI is limited to `.github/workflows/validate.yml`. No test suite —
see `CONTRIBUTING.md` §Validation for how a change is checked instead.
Design choices follow `PHILOSOPHY.md`.

## Release rule

The plugin marketplace installs from `main` HEAD — every merge to main is a
publish. Before merging a change to a SHIPPED or GATE-INFRA surface (taxonomy
defined in `.claude/skills/release/SKILL.md` section 0 — cite it, never
re-enumerate here), run the `release` skill. A change confined to INTERNAL or
DOCS takes READY alone (release skill's own D1).

## Harness-neutral core

Design under `PHILOSOPHY.md` point 5. This repo is one distribution, held
behind an adapter.

Adapter set — the only places runtime mechanics may live: agent and skill
frontmatter, `hooks/`, `scripts/`, `workflows/`, `.github/`, `.claude/`,
`.claude-plugin/`. Shipped bodies (`agents/*.md`, `skills/**`) name
capabilities (write, edit, shell, web), never runtime tool identifiers,
settings keys, or APIs.

Test before adding anything runtime-specific: would this survive a port to
another runtime? If not, it goes in the adapter set or it goes nowhere.

## Where things live

- `agents/` — shipped agents: the four executors, `researcher`, the
  `product-*` pipeline. `executor-lead`/`executor-judge` hold no Write/Edit
  by design; `scripts/executor-guard.sh` denies the Bash write-forms for
  them too — granting either tool dissolves the invariant.
- `skills/` — shipped skills.
- `.claude/skills/` — repo-internal only, never shipped: `author-agent`,
  `release`, `review-agent`.
- `evals/` — behavioural fixtures; run via `.claude/workflows/agent-evals.js`.

## Gate skills — invoke and when

- `author-agent` — creating a new agent, or overhauling existing agent,
  skill, or reference-contract text; gates through `review-agent` before it
  lands.
- `review-agent` — standalone design-review verdict on agent-definition,
  routing-description, or always-resident skill text, when it isn't already
  part of an `author-agent` run.
- `release` — any change to a SHIPPED or GATE-INFRA surface headed for main
  (see Release rule above).

## Plugin-only distribution

Only `agents/` and `skills/` auto-register on install; `workflows/`
and `scripts/` ship in the tarball but need manual wiring. Agent
frontmatter `hooks:` / `permissionMode:` are ignored under plugin
installs — guard hooks arrive instead via `hooks/hooks.json`.

A running session snapshots agents, skills, and workflows at start — restart
it before an edit to any of those is picked up.
