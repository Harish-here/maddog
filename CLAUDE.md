# CLAUDE.md

Beliefs: `PHILOSOPHY.md`. Visual identity and user-facing wording: `DESIGN.md`.
Layout and routing: `README.md`. How a change is validated — there is no
test suite and nothing compiles: `CONTRIBUTING.md` §Validation.

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
- `.claude/` is repo-internal and is never registered as a plugin surface.

## Distribution mechanics

A plugin install auto-registers `agents/`, `skills/`, `commands/`, `hooks/`,
and `.mcp.json`; `workflows/` and `scripts/` ship in the tarball but are not
auto-wired (undocumented). Agent frontmatter `hooks:` and `permissionMode:`
are ignored in plugin agents — guard hooks arrive via `hooks/hooks.json`.
Skill edits take effect immediately; agent edits need `/reload-plugins` or a
restart; workflow reload is undocumented, so restart to be sure.
