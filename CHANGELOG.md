# Changelog

All notable changes to this project are documented in this file, reconstructed
from git history. Each line is traceable to a commit (short sha in parentheses).
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [2.0.0] - 2026-08-16

### Changed
- Plugin and repository renamed `maddog-skills` → `maddog` (breaking for plugin
  installs: reinstall as `maddog@maddog`); the repo URL redirects from the old name.

## [1.9.0] - 2026-08-16

### Added
- `author-agent`: gated authoring loop skill, review-agent partition, routing eval (`6d5a602`)
- `mine-session`: session pattern-mining skill, core-aware routing harness (`91d9368`)

### Fixed
- Law, example, and return-contract hardening across the agent family (`ea780cd`)

### Docs
- Replaced model pins with tier words in `CLAUDE.md` (`c27a893`)

## [1.8.0] - 2026-08-16

### Chore
- Re-homed `review-agent` to `.claude/skills`, added an agent template, pruned dead links (`348b1cc`)

## [1.7.0] - 2026-08-15

### Added
- `review-agent`: TDD-built skill for agent-definition reviews, superseding the draft checklist doc (`abec4ed`)

### Fixed
- Judge return contract and triggers, guard hooks on lead/judge, smart claims routine reviews (`57cae76`)
- `advisor-mode`: absent liturgy header matches the broadened unattended trigger (`37e881d`)
- Applied PR #2 change-review findings (`dee7642`)

### Docs
- Drafted a checklist for reviewing agent definitions (`7dd1ada`)

## [1.6.0] - 2026-08-14

### Added
- Plugin-ready guard hook, portable dual-mode wiring (`113ef57`)
- `executor-lead` as judgment-with-memory; added `executor-judge` (`616da5d`)
- Widened the guard hook to `executor-lead` and `executor-judge` (`9d8fbd4`)
- Lean eval fixture sets for lead and judge, plus harness wiring (`a1ceb9f`)
- `advisor-mode`: three-budget core, 2x2 state model, absent liturgy (`7b9581e`)

### Docs
- Intelligence-budget doctrine documenting the five-role family (`4f61496`)

### Chore
- Plugin description updated to reflect the five-role manifest (`bda5158`)

## [1.5.1] - 2026-08-14

### Added
- `permissionMode: dontAsk` on both executor tiers (`c0b063b`)
- `PreToolUse` guard hook for irreversible commands on `executor-fast` (`3d106bb`)
- `NOTES CONTRACT` happy/trap eval pair for `executor-fast` (`93a0b14`)

### Fixed
- Reverted `executor-smart` to remove the Agent tool and the DELEGATE DOWN law; dropped two stale dispatching references (`7ef7490`, `61ef14a`)
- `executor-fast`: NOTES reports what you did, never what the data means (`b584732`)

### Docs
- README covering modes, delegation and evals (`33dbd10`)

## [1.5.0] - 2026-08-13

### Added
- `executor-fast` classified into eight modes, each with a named law (`73dde95`), later synthesised to four modes with per-task effort and a rebuilt delegation fixture (`db463c3`)
- `executor-smart` given six modes with named laws, plus autonomous delegation to `executor-fast` (`dc9add5`)
- `executor-fast`: stop-don't-guess elevated to a named law, the andon cord (`07cdd2f`)
- `agent-evals` workflow to run 39 behavioural fixtures against the real agents (`eddb251`, `9c811c7`), with effort pinned high and measured, not assumed (`44bb818`)
- `product-*`: closed the mockup-fidelity gaps in the product pipeline (`4f3c3cb`)

### Fixed
- `product-engineering`: unattended watchdog now spans EXECUTE+QA (`cefcdac`)

### Changed
- Executors refactored with a dispatch contract; audited dead weight cut (`e06fd9e`)

### Docs
- Added `CLAUDE.md` — repo orientation, install modes, validation model (`f30ab61`)

## [1.4.0] - 2026-08-11

### Added
- `product-engineering` pipeline extended to BE planning, execution, and QA -> PR (`dcbe6f3`)

### Fixed
- Baked the routing rule into descriptions — prefer a repo-local executor at the same tier (`7d30742`)
- Routed stateful choreography to smart and barred frozen plans from lead — eval-driven description fixes (`1eca87e`)

### Changed
- Renamed the `product-team` skill to `product-engineering` (`f31dfea`)

## [1.3.0] - 2026-08-10

### Added
- `product-team` planning pipeline — PM -> UX -> UI, three discipline agents plus researcher and an orchestrating skill (`43583f7`)

### Docs
- `advisor-mode`: launch-contract pointer, watchdog state carve-out, user doctrine edits (`0716163`)

## [1.2.0] - 2026-08-08

### Added
- `sdd-task-loop`: per-task implementer tier (`tasks[].model`, bounded, flagged-refuses-haiku) (`fff1c47`)
- `watchdog`: tmux auto-resume for session-limit pauses (script + launch-contract item 5) (`ce6d889`)
- `watchdog`: standing-mode resume state — tmux-hosted runs self-heal across host restarts, with crash-loop quarantine (`1c052db`)
- `sdd-task-loop`: escalation-on-red — haiku implementer failures retry once on sonnet before aborting (`6150d60`)

### Fixed
- `watchdog`: launch claude via interactive login shell — cron-stripped env lacks auth vars (`790ac65`)
- `sdd-task-loop` review fixes — fail-closed lint, `implementerAgent` param, up-front validation, blocked-only escalation with trace, parallel fall-through, discipline parameterization, null-review guards, tier polish (`0384952`)
- `watchdog` review fixes — lock breaker, scoped crash-loop guard, verified launch with REPL readiness poll, numeric guards, session param, HOME-templated plist + install wiring, unattended-runs docs (`d19dcd3`)

### Docs
- `watchdog` uses launchd, not cron — keychain auth needs the GUI session, live-tested; plist template (`c33bc6a`)
- `sdd-task-loop`: file-artifact briefs — copy-then-verify convention + lint existence check (`abc7443`)

### Chore
- Deduped agent frontmatter model keys; bumped plugin to 1.2.0 (`8ee340f`)

## [1.1.0] - 2026-08-07

### Added
- `sdd-task-loop` v2 workflow, telegram checkpoint pings, pinned executor model tiers (`733265b`)

## [1.0.0] - 2026-08-01

### Added
- Advisor-executor hierarchy — 3 agents, 3 skills, symlink installer (`ec639bc`, pre-`plugin.json`, folded into this release)
- Packaged as a Claude Code plugin with a self-hosted marketplace (`eb13491`)
