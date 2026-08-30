# maddog

Maddog is a place for some really good skills and agents, along with some
no-brainer stuff: four executor tiers, a researcher, and a product pipeline,
written as plain prose any agent runtime can load. Currently we distribute
as a plugin for Claude; soon, for every other ecosystem.

## Design philosophy

- **Intelligence is a budget.** Every task is routed by its shape to the
  cheapest hand that covers it.
- **Tokens are the new currency. Never pay twice.** A token spent on
  something is never spent again on the same thing.
- **Architect the integrity. Don't just instruct the agent.** A rule that
  must hold is built into the structure: the judge holds no edit tools, a
  hook denies the write, a guard blocks the shell form.
- **Spend your attention on what matters.** There is enough technology to
  carry the mechanical work.
- **Harness-neutral core.** The roles, laws, and contracts are plain prose
  that any agent runtime could load.

See `PHILOSOPHY.md` for the full statement of each point.

## Install

```
/plugin marketplace add Harish-here/maddog
/plugin install maddog@maddog
```

The marketplace installs straight from `main` HEAD, so every merge to main
is effectively a publish. Skills arrive namespaced (`/maddog:advisor-mode`).
Update later with `/plugin marketplace update maddog`.

- Agent frontmatter `hooks:` / `permissionMode:` are ignored for
  plugin-shipped agents — the executor guards arrive instead via the
  plugin's `hooks/hooks.json`, and `permissionMode: dontAsk` does not apply,
  so executors may surface permission prompts; add allowlist entries for the
  commands you delegate.
- **Prerequisite:** `product-qa`'s live-drive verification requires the
  playwright MCP browser tools — configure it separately, or `product-qa`
  returns blocked at its prerequisite check.

Restart your Claude Code session after installing or updating — the agent
registry snapshots at session start.

## What ships

### Agents (`agents/`)

**Executor family** (`executor-fast`, `executor-smart`, `executor-lead`,
`executor-judge`) — one ladder of judgment, bought by task shape. Fast and
smart do the work; lead holds memory across a package; lead and judge can
rent fast-tier hands, lead smart-tier too; judge rules on the others'
output and can never edit. The guard scripts enforce the last part.

- **executor-fast** — runs fully-specified mechanical tasks on a cheap, fast
  model: bulk edits, test/lint runs, search, extraction, boilerplate,
  committing, pushing, opening a PR.
- **executor-smart** — runs one delegated task needing local judgment but not
  top-tier reasoning: pattern-matching refactors, context-dependent edits,
  small design choices inside a fixed boundary, debugging, migrations,
  splitting an oversized file, or live/stateful choreography.
- **executor-lead** — holds judgment with memory across one bursted work
  package: freezing an open decomposition into a plan, running an
  unfreezable evidence-driven campaign, or delivering one decided-scope
  package entangled with live/hazardous reality.
- **executor-judge** — renders adversarial gate verdicts on another
  intelligence's output: design review before execution, change review
  after, and adjudication of gating disputes. Cannot fix anything it rules
  on — no Write/Edit.

**Researcher** — exists so the executors stay web-free; the only hand with
web tools, returns capped and cited.

- **researcher** — mechanical web research on a cheap model: runs the
  searches it's handed and returns a capped, source-cited findings table,
  no synthesis.

**Product pipeline** (`product-pm` → `product-ux` → `product-be` →
`product-ui` → `product-qa`) — five ordered stages, each consuming the
previous stage's artifact under `docs/product/<slug>/`; qa is read-only on
code and routes bugs back to the responsible stage.

- **product-pm** — turns one feature/epic into a shippable product spec,
  grounded in research, persona, and app recon. First stage of the
  product-engineering pipeline.
- **product-ux** — designs the user experience for one spec'd feature and
  has the HTML mockup rendered from it. Second stage.
- **product-be** — plans the server-side work for one designed feature into
  a precise backend blueprint. Third stage.
- **product-ui** — plans the implementation of one designed feature,
  mapping every mockup element to real components. Fourth stage.
- **product-qa** — verifies one implemented feature against its product
  artifacts, runs gates and e2e, and opens the PR only at zero open bugs.
  Final stage.

### Workflows and scripts

`workflows/sdd-task-loop.js` ships as the general-usage plan-execution
engine. `workflows/` and `scripts/` (the guard hooks, the watchdog) ship in
the plugin tarball but, unlike `agents/` and `skills/`, are not
auto-registered — the watchdog wiring is `scripts/setup-watchdog.sh`; launch
the workflow via its `scriptPath`.

### Skills (`skills/`)

- **advisor-mode** — runs a session as the Advisor: holds architecture,
  routing, and acceptance judgment while delegating everything else.
- **efficient-md** — authoring doctrine for anything an agent loads
  (CLAUDE.md, a memory index, a frontmatter description, a SKILL.md body, a
  brief, a state file, a decision ledger, a dispatch prompt's output
  format).
- **mine-session** — extracts reusable collaboration patterns from a working
  session; arm it at session start, distill at session end.
- **plain-english** — governs how replies and questions are worded for the
  user.
- **product-engineering** — orchestrates the full PM → UX → BE → UI →
  execution → QA pipeline for one feature; not for small tweaks or single
  bug fixes.

`author-agent`, `release`, and `review-agent` live under `.claude/skills/`
and are repo-internal maintainer tooling — they never ship in the plugin.
`advisor-mode` and `product-engineering` are slash-command only
(`disable-model-invocation: true`) — invoke them by name, they don't
auto-trigger on a matching description.

## Architecture, in brief

Route every task on its *shape*, never the subject's sophistication: a task
with every decision already closed and objective acceptance goes to
`executor-fast`; one task carrying local judgment inside a fixed boundary
goes to `executor-smart`; a package needing judgment with memory across
several steps goes to `executor-lead`; a verdict on another intelligence's
output goes to `executor-judge`. `product-engineering` is a second,
orthogonal axis — a discipline pipeline, not a judgment tier.

## Contributing

`main` is protected — changes land by pull request. See `CONTRIBUTING.md`
for commit style, the no-test-suite validation model, and when to route new
or overhauled agent/skill text through the `author-agent` gated-authoring
loop.

## Releasing

Any change to a SHIPPED surface (`agents/`, `skills/`, `workflows/`,
`.claude-plugin/`) or a GATE-INFRA surface (`.github/`, `hooks/`,
`scripts/`) headed for `main` goes through the `release` skill
(`.claude/skills/release/SKILL.md`) — DECLARE, READY, BEHAVIOR, RULE, and
SHIP before merge, SEAL after. Changes confined to INTERNAL (`.claude/`,
`evals/` — except `.claude/skills/release/`, which is GATE-INFRA) or DOCS
(this file, `CHANGELOG.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`,
`LICENSE`, `.gitignore`, `PHILOSOPHY.md`) take READY alone. The release
skill never merges — it stops at push + open PR; merging is the
maintainer's own hand, on a PR whose verdict names its current head commit.

## License

MIT — see `LICENSE`.
