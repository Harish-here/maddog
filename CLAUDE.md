# CLAUDE.md

Beliefs: `PHILOSOPHY.md`. Layout and routing: `README.md`. How a change is
validated — there is no test suite and nothing compiles: `CONTRIBUTING.md`
§Validation.

## Publishing

Merging to main publishes: the marketplace installs from main HEAD. Run the
`release` skill before merging a SHIPPED or GATE-INFRA change — taxonomy in
`.claude/skills/release/SKILL.md` §0. Load-bearing instruction text goes
through `.claude/skills/author-agent`, which gates via `review-agent`.

## Invariants

- `executor-lead` and `executor-judge` hold no Write/Edit, and
  `scripts/executor-guard.sh` denies their Bash write-forms too. Granting
  either tool dissolves the invariant.
- Adapter set — the only paths where runtime mechanics may live: agent and
  skill frontmatter, `hooks/`, `scripts/`, `workflows/`, `.github/`,
  `.claude/`, `.claude-plugin/`. Shipped bodies (`agents/*.md`, `skills/**`)
  name capabilities (write, edit, shell, web), never runtime tool
  identifiers, settings keys, or APIs (`PHILOSOPHY.md` point 5).
- `.claude/` is repo-internal and never ships.

## Distribution mechanics

Only `agents/` and `skills/` auto-register on install; `workflows/` and
`scripts/` ship in the tarball but need manual wiring. Agent frontmatter
`hooks:` and `permissionMode:` are inert — guard hooks arrive via
`hooks/hooks.json`. A session snapshots agents, skills, and workflows at
start; restart it before an edit to any of them takes effect.
