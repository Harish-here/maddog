# Contributing

## Branches and PRs

`main` is protected — changes land by pull request, not by pushing directly.

## Commit style

Conventional commits, scoped to the surface touched: `feat(product-engineering):`,
`fix(executors):`, `docs(watchdog):`, `chore:`. See `CHANGELOG.md` for examples
of the convention in practice.

## Validation — there is no test suite

This repo has no application code, so there's nothing to run through a linter
or a test runner. A change is validated by exercising it:

- **Agent body change** → dispatch that agent on a representative task and
  confirm it follows the new instruction, rather than assuming it will.
- **Agent/skill description change** → this is routing, not documentation.
  Confirm the intended task shape still selects the agent and neighbouring
  shapes still don't — `evals/run-skill-routing.sh` runs the routing probes.
- **Workflow change** (`workflows/*.js`) → launch it with the `scriptPath`
  option; a running session snapshots workflows at session start and won't
  pick up an edit mid-run.

See `CLAUDE.md` for the full validation model and repo architecture.

## Authoring agent/skill instruction text

Load-bearing instruction text — a new agent, or an overhaul of an existing
agent, skill, or reference contract — goes through the gated authoring loop
in `.claude/skills/author-agent`, which routes to `review-agent` as an
independent gate before the text ships. Small, low-stakes edits to existing
text don't need the loop; use judgment, and prefer it when the defect would
be silent in production.

## Shipping a change to the agent/skill set

When the shipped set of agents or skills changes (added, renamed, removed),
bump `version` in `.claude-plugin/plugin.json` and add an entry to
`CHANGELOG.md`.
