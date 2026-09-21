<table align="center"><tr><td>

<pre>
███╗   ███╗ █████╗ ██████╗ ██████╗  ██████╗  ██████╗
████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔════╝
██╔████╔██║███████║██║  ██║██║  ██║██║   ██║██║  ███╗
██║╚██╔╝██║██╔══██║██║  ██║██║  ██║██║   ██║██║   ██║
██║ ╚═╝ ██║██║  ██║██████╔╝██████╔╝╚██████╔╝╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝

═════════════════════════════════════════════════════
            S K I L L S   &amp;   A G E N T S
═════════════════════════════════════════════════════
</pre>

</td></tr></table>

# maddog

maddog is a place for some really good skills and agents, along with some
no-brainer stuff: four executor tiers, a researcher, and a product pipeline,
written as plain prose any agent runtime can load. It ships adapters for both
Claude and Codex.

## Design philosophy

- **Judgment is expensive.** Spend intelligence where decisions change
  outcomes — judgment shape routes the task, not subject difficulty.
- **Work is paid once.** Reuse completed work — evidence, decisions,
  artifacts — until its basis changes; a downstream agent should not
  rediscover it.
- **Authority follows responsibility.** An agent gets only the authority
  and capabilities its responsibility requires; structural boundaries hold
  this, not role instructions alone.
- **Human judgment is scarce.** Spend human judgment only on decisions
  requiring human authority; escalate a compressed decision, not raw
  uncertainty.
- **Separate responsibility from mechanism.** Roles, responsibilities,
  authority, and contracts define behavior; runtime mechanisms implement
  them, so the core never depends on one harness's mechanics.
- **Outcome over activity.** Every action must earn its cost — change the
  outcome, resolve uncertainty, or produce reusable evidence — or it does
  not happen.

See `PHILOSOPHY.md` for the full statement of each point.

See `DESIGN.md` for the visual identity: wordmark, colour, type, and the wording rules for user-facing text.

## Install

### Codex

This checkout is ready for Codex. Run Codex from the repository root; it
auto-discovers project skills in `.agents/skills/` and custom subagents in
`.codex/agents/`. Start a workflow with `$advisor-mode`, or ask Codex to
delegate to a named agent such as `executor-smart` or `product-pm`.

The shared contracts remain under `skills/` and `agents/`. The Codex adapter
layers contain runtime configuration, model tiers, sandbox boundaries, and
small translations for Claude-only mechanics. See `AGENTS.md` for the
operating rules.

### Claude

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

After installing or updating, run `/reload-plugins` or restart the
session: agents load at session start, skills reload live.

**Also on skills.sh:**

```
npx skills add Harish-here/maddog
```

This installs the maddog skills into other agent runtimes. The executor and
product agents that `advisor-mode` and `product-engineering` dispatch come
only with the plugin install above.

## What ships

### Agents (`agents/`)

**Executor family** (`executor-fast`, `executor-fast-read`, `executor-smart`, `executor-lead`,
`executor-judge`) — one ladder of judgment, bought by task shape. Fast and
smart do the work; lead holds memory across a package and orchestrates
fast-read, fast, smart, and judge inside it; judge can rent only the
read-only fast-tier hand and rules on the others' output with a PASS,
FAIL, or STOP verdict — it can never edit. The guard scripts enforce the
last part.

- **executor-fast** — runs fully-specified mechanical tasks on a cheap,
  fast model: a decided edit, one rule across many files, test and build
  runs, git and service operations, state recovery, bug reproduction, code
  from a frozen brief.
- **executor-fast-read** — runs fully-specified read-only mechanical tasks
  on the same cheap, fast tier, holding no shell and no edit: where
  something lives, what the source says verbatim, whether a claim holds;
  holds web access (WebSearch, WebFetch) when the dispatch names web
  sources.
- **executor-smart** — runs one delegated task needing local judgment but
  inside a fixed boundary, on a mid-tier model: a feature or refactor
  matching existing patterns, transforming a structure across versions or
  modules without losing behavior, diagnosing an uncertain cause from
  bounded evidence, or reviewing an artifact against explicit criteria.
- **executor-lead** — owns evolving work inside a delegated boundary on a
  high-tier model: adaptive decomposition, evidence-driven sequencing,
  package-level judgment with memory across steps; orchestrates
  executor-fast-read, executor-fast, executor-smart, and executor-judge
  inside its package, and never judges its own package.
- **executor-judge** — renders independent acceptance verdicts on another
  intelligence's output, on a high-tier model: plan/design review before
  execution, and review of an executed outcome against its acceptance bar;
  issues PASS, FAIL, or STOP, can rent only executor-fast-read, and holds
  no Write/Edit — it cannot fix anything it rules on.

**Researcher** — a separate role from executor routing, kept for the
product pipeline's web research needs; web access inside executor routing
lives on `executor-fast-read` when a dispatch names web sources.

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

- **advisor-mode** — runs a session as the Advisor: classifies work by
  judgment shape, delegates it or does small work directly, and accepts
  what comes back.
- **efficient-md** — shapes a markdown artifact's length and structure by how
  long it stays loaded and who reads it, agent or person (AGENTS.md or README,
  a memory index, a frontmatter description, a SKILL.md body, a brief, a state
  file, a decision ledger, a dispatch prompt's output format).
- **mine-session** — extracts reusable collaboration patterns from a working
  session; arm it at session start, distill at session end.
- **plain-english** — governs how replies and questions are worded for the
  user.
- **product-engineering** — orchestrates the full PM → UX → BE → UI →
  execution → QA pipeline for one feature; not for small tweaks or single
  bug fixes.
- **section-by-section** — walks one existing skill or agent file with the
  user, section by section; the user closes each section with one verdict,
  and the run produces a draft and a verdict ledger, never editing the target.

`author-agent`, `release`, and `review-agent` live under `.claude/skills/`
and are repo-internal maintainer tooling — they never ship in the plugin.
`advisor-mode`, `product-engineering` and `section-by-section` are
slash-command only (`disable-model-invocation: true`) — invoke them by
name, they don't auto-trigger on a matching description.

## Architecture, in brief

Route every task on its *shape*, never the subject's sophistication: a task
with every decision already closed and objective acceptance goes to
`executor-fast`; the read-only slice of that shape — locating,
quoting, or verifying, with no shell and nothing to write — goes to
`executor-fast-read`; one task carrying local judgment inside a fixed
boundary goes to `executor-smart`; a package needing judgment with memory
across several steps goes to `executor-lead`; a verdict on another
intelligence's output goes to `executor-judge`. `product-engineering` is a
second, orthogonal axis — a discipline pipeline, not a judgment tier.

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
SHIP before merge, SEAL after. Changes confined to INTERNAL (`.claude/` —
except `.claude/skills/release/`, which is GATE-INFRA) or DOCS
(this file, `CHANGELOG.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`,
`LICENSE`, `.gitignore`, `PHILOSOPHY.md`, `DESIGN.md`, `assets/`,
`skills.sh.json`) take READY alone. The release
skill never merges — it stops at push + open PR; merging is the
maintainer's own hand, on a PR whose verdict names its current head commit.

## License

MIT — see `LICENSE`.
