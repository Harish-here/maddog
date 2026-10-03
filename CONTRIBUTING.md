# Contributing

## Branches and PRs

`main` is protected: force-pushes and deletions are blocked and changes land by pull request; the sole maintainer can currently bypass review, which tightens to required approvals once a second maintainer exists.

## Commit style

Conventional commits, scoped to the surface touched: `feat(product-engineering):`,
`fix(executors):`, `docs(watchdog):`, `chore:`. See `CHANGELOG.md` for examples
of the convention in practice.

## Validation

Instruction text has no compiler, so a change is validated by exercising it.
Model-driven tests live in `tests/` (see `tests/README.md` and
`docs/testing/spec.md`):

- **Advisor-mode routing change** (the Classify table, or anything the advisor
  reads before its first handoff) → run
  `tests/.venv/bin/python tests/run.py skills/advisor-mode --runtime claude-code` and compare the
  branch and main columns.
- **Agent body change** → dispatch that agent on a representative task and
  confirm it follows the new instruction, rather than assuming it will.
- **Agent/skill description change** → until `tests/agents/` exists, run
  fresh-session probes: one task the new description should win and one it
  should lose.
- **Workflow change** (`workflows/*.js`) → launch it with the `scriptPath`
  option; a running session snapshots workflows at session start and won't
  pick up an edit mid-run.

See `CLAUDE.md` for the repo layout and distribution mechanics; the validation model is the section above.

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

## Releases

Every change headed for `main` goes through the `release` skill
(`.claude/skills/release/SKILL.md`): prepare the branch, run the checks, get
it cleared, open the pull request, publish after the merge. A table in the
skill says which changes need an independent reviewer — anything users
receive does, and so does anything that runs the checks themselves. The
skill never merges; it stops at the open pull request. Merging is the
maintainer's own hand, and where a reviewer was required, only while the
verdict names the pull request's current head commit.

Before submitting or releasing, run `claude plugin validate .claude-plugin/plugin.json` — invoking the validator at the repo root validates only the marketplace manifest and never exercises the plugin. Known, accepted warning: CLAUDE.md at the plugin root is maintainer context (instructions for developing this repo), not consumer context, so the 'not loaded as project context' warning is expected and --strict is deliberately not this repo's gate. Tag releases as both `v<version>` and `<name>--v<version>` (the plugin CLI's convention), with plugin.json, CHANGELOG, and tags agreeing on the version.
