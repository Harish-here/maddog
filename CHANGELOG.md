# Changelog

All notable changes to this project are documented in this file, reconstructed
from git history. Each line is traceable to a commit (short sha in parentheses).
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [2.12.1] - 2026-08-30

### Added
- `PHILOSOPHY.md` — five design points, harness-neutral (`f4c4d7a`)

### Changed
- `README.md` — rewritten with a philosophy section and agents grouped by family (`f4c4d7a`)
- `CLAUDE.md` — rewritten under the efficient-md HOT law: pointers to PHILOSOPHY.md, README.md, CONTRIBUTING.md; publishing rule; three invariants (lead/judge no-edit, adapter set, .claude/ not a plugin surface); distribution mechanics verified against the plugin docs (`ecc93d8`, `feed37d`)
- `CONTRIBUTING.md` — stale pointer retargeted (`f4c4d7a`)
- `.claude/skills/release/SKILL.md`, `references/release-model.md` — `PHILOSOPHY.md` classed DOCS; `install.sh`, the E16 populated-fixture probe, and the symlink clause removed (gone since 2.11.0); release model revision bumped to 11 (`f4c4d7a`)
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — descriptions rewritten for adopters: what it does, not a list of component names (`6a95e31`)

## [2.12.0] - 2026-08-27

### Added
- `scripts/judge-dispatch-guard.sh` — a PreToolUse hook on the `Agent` tool denying `executor-judge` any dispatch target but `executor-fast` or `researcher`, including a dispatch naming no target at all (which runs the default general-purpose agent, holding every tool); payload field names confirmed against captured live payloads
- `evals/`: 16 behavioural fixtures covering the eight mode laws that had none — fast TRANSFORM/RECOVER, smart PORT/DECOMPOSE, lead CAMPAIGN/DELIVER, judge DESIGN-REVIEW/ADJUDICATE — one happy case and one trap each, all core
- `advisor-mode`: gains the named rule ONE TASK, ONE HAND — a task that already has a hand keeps it; a fresh dispatch is now the exception and must name its reason (class change, spent ceiling, half-full context, a rejected or failed return, or a long idle). Note: 2.11.1's prohibition on opening a fresh dispatch for resumable work did not bind in practice — this rule inverts the default instead of restating the prohibition

### Changed
- `agents/executor-fast.md`, `executor-smart.md`, `executor-lead.md`, `executor-judge.md`: all four descriptions rewritten against the description standard and the checklist's five-slot shape — family resident cost fell from 4,567 to about 3,380 characters while gaining positive claimants for debugging, git/operations work, migrations, splitting and authoring, which no description previously claimed; `executor-lead` fell from 1,786 to 861 characters, and all four are now under the 1,024-character cap

### Fixed
- `scripts/executor-guard.sh`: now denies the common file-writing Bash forms for lead and judge (glued redirects, inline interpreters, `git rm`/`git mv`), extends irreversible-command coverage to `executor-smart`, denies `git merge` and `git worktree remove`/`prune` for all four, catches the `+ref` force-push form and `find -delete` and `git branch --delete --force`, and matches the temp carve-out on a path component rather than a substring; a quote-handling bug in its command splitter that blocked legitimate searches containing a pipe is fixed
- `agents/executor-lead.md`: regains the precedence clause its satisficing law had lost
- `CLAUDE.md`, `README.md`: no longer claim enforcement the guards did not deliver

## [2.11.1] - 2026-08-27

### Fixed
- `advisor-mode`: the general resume rule was stated as a permission ("a dependency test decides whether B MAY resume A's agent"), so it never fired reliably — only the judge's resume (stated as an instruction) did; in one session, 19 dispatches produced exactly 1 resume, though 4 more passed the dependency test and were spawned fresh anyway. The Resume section's first paragraph now ends with an explicit prohibition: "Never open a fresh dispatch for work that passes the dependency test while that hand may still be resumed." (`f067e54`)
- `advisor-mode`: the ceilings paragraph never stated what its counts are measured against — "per class, never per session" read as either per-task or per-session; now explicit: "count per task chain, never per session." Replaced the token-budget numbers (which had silently replaced the hard counts on harnesses reporting spend in tokens, and which were meaningless without a context-window size the advisor never receives) with a softer, harness-agnostic brake: stop when the hand's context is half full, dispatch fresh after a long idle with prior findings supplied verbatim (`f067e54`)
- `advisor-mode`: the judge paragraph's long-idle rule is now stated once, in the general ceilings paragraph, instead of being duplicated with a judge-specific token number (`f067e54`)

## [2.11.0] - 2026-08-27

### Fixed
- `README.md`: the documented watchdog-setup command no longer globs blindly across every cached plugin version — it now picks the newest cache directory, avoiding a silent wrong-version pick once a second release ships (RULE finding)
- `SECURITY.md`: corrected the claim that `setup-watchdog.sh` is the only script touching the machine outside the repo — `tg-notify.sh` and `watchdog-resume.sh` also do, once wired up (RULE finding)
- `scripts/executor-guard.sh`: header comment no longer describes the deleted symlink-mode wiring path (RULE finding)
- `permissionMode: dontAsk` removed from `executor-fast`, `executor-smart`, `executor-lead`, `executor-judge` frontmatter — it only ever took effect under symlink installs, which no longer exist (RULE finding)

### Removed
- `install.sh` and the symlink install mode — plugin-only distribution now; the two-install-modes framing is gone from `README.md` and `CLAUDE.md` (`0fe22f2`)
- dead `hooks:` frontmatter blocks in `agents/executor-fast.md`, `agents/executor-lead.md`, `agents/executor-judge.md` — ignored under plugin installs already, and now unused since symlink mode is gone (`0fe22f2`)

### Added
- `scripts/setup-watchdog.sh` — optional, maintainer-run script that wires the watchdog LaunchAgent and Telegram notify script, since a plugin install can't do this automatically; extracted from `install.sh`'s watchdog/notify logic only (`0fe22f2`)

### Changed
- `README.md`, `SECURITY.md`, `skills/advisor-mode/references/absent.md`: symlink-mode references replaced with the opt-in watchdog-setup story (`0fe22f2`)

## [2.10.0] - 2026-08-27

### Changed
- `advisor-mode`: the binding record is no longer written to a file at session open — the advisor binds at session open and holds the record in context, writing it once as the ledger's first entry when a ledger opens; Own Hands' Write allowance no longer names a binding record file
- `advisor-mode`: Session Open gains a scope line — efficient-md governs artifacts, this skill's own contracts govern its own: dispatch prompts and returns follow the Dispatch Contract, the ledger follows `references/ledger.md`
- `advisor-mode`: Own Hands now permits the advisor to run a read-only command itself, both conditions required — it only reads, and it checks a claim in a return the advisor holds; previously reading a cited file:line was allowed but every command was forbidden, leaving command-only verification unsettled; the Survey bullet's blanket "No other command is yours" is removed, since it contradicted this exception
- `advisor-mode`: the Dispatch Contract gains three rules — name the authoritative source instead of pasting when a file is out of date, a dispatch authoring a markdown artifact names the artifact's class so a hand holding the Skill tool invokes efficient-md and any other hand is given the path to that class's reference, and every OUTPUT FORMAT heading carries its own ceiling (`OUTPUT FORMAT (< 600 words)`, the number set per task)
- `references/ledger.md`: BINDING RECORD and ROUTING PRECONDITION rewritten to match the binding-record change — bound at session open and held in context, written as the ledger's first entry once a ledger opens
- `executor-fast`, `executor-smart`: `Skill` added to `tools:`, with the law "Never invoke a skill the dispatch did not name" — the grant lets them invoke efficient-md when a dispatch names it, the prohibition stops a cheap hand pulling in skills nobody asked for
- `agent-evals`: the workflow moves from `workflows/` to `.claude/workflows/` — it is maintainer-only, invoked via `scriptPath`, and no longer part of the shipped set; `.gitignore`, `README`, `CLAUDE.md`, and `evals/author-agent.json` updated to match (`edb58cf`, `2e725dc`)

## [2.9.0] - 2026-08-26

### Changed
- `advisor-mode`: memory write is no longer a CLOSE obligation — a one-line candidate batch is presented at CLOSE and written only with the user's approval; a zero-memory session is steady state, not a failure (D1)
- `advisor-mode`: resume extended to every hand — a dependency test decides reuse, ceilings set per class (mechanical 2, local 4, iterated 2, web-perception 2 resumes, adversarial 3 rounds per artifact, with a token-spend override), and the judge gets three rounds per artifact with a tighter running-skill bound always winning (D2)
- `advisor-mode`: context overhead ruled tolerable at current levels — the existing laws (return cap, give-the-path, filed rulings, artifacts not conversation) stay as-is; the resume rule is the new saving lever (D3)
- `advisor-mode`: implementation detail removed from the body — the "nothing enforces this" disclaimer, the gate-filing mechanism's literal wording, the State section's unattended-procedure contents list, and the "guarantees live in tool restrictions" line; DELEGATION LOG stays named as a guaranteed family return slot, and the one-sentence definition of "unattended" stays resident in State (D4)
- `advisor-mode`: body cut from 2,621 words to 2,495 words. The cut removed justification and implementation detail. Every example and edge case survived. New Resume and Session Open sections were added (D5)
- `advisor-mode`: body restructured — the Budgets frame is dropped (Own Context and User Attention are top-level), Iterated Trigger folds into Routing, a new Session Open section covers efficient-md/survey/bind, and a new Resume section covers D2; the binding record is now written silently to the advisor's own scratchpad file at session open and stated only on request or when degraded/unbound (R-F15), and the Ledger section's opening narrative moves to `references/ledger.md` (D6)
- `advisor-mode`: body rewritten to a plain declarative standard — one rule per sentence, active voice, the doer named, no nested clauses, no parentheticals, at most one em-dash per sentence; every example and "the thought that means you are about to break this rule" line survives (D7)
- `references/ledger.md`: CLOSE's discharge condition now matches D1 — the surfacing batch plus any user-approved memory candidate while the user is present, the surfacing batch alone while absent
- `references/ledger.md`: the routing gate now keys on the binding record existing (the session-open scratchpad file, or the ledger's first entry), never on the record being spoken to the user; gains an Opening section carrying the ledger's open-trigger and departure-shape narrative moved from `SKILL.md`

### Added
- `evals/advisor-mode.json`: three behaviour fixtures pinning D1 and D2 — `memory-bar-close` (no memory write before approval), `resume-fresh-after-rejection`, and `resume-dependent-task-same-class`


## [2.8.0] - 2026-08-26

### Changed
- `advisor-mode`: description rewritten to the description-standard contract — "Use when …" triggers replace imperative second person and the restated body norms, and the family names it dropped so it stops contradicting "this table names no agents" (F8, F9)
- `advisor-mode`: the ledger now opens at the launch decision for a dispatch the user will not be present for, not after they have already left; USER PRESENCE flips only on the actual departure, so a scope call raised at launch still reaches the user attended (F1, F6)
- `absent.md` gains §6 MID-FLIGHT DEPARTURE — a user leaving mid-dispatch now opens the ledger and starts the watchdog/resume record without killing the running dispatch
- `advisor-mode`: Bind's `kept` class is stated Exempt rather than left unroutable — `kept` is never for sale and could never satisfy "name a hand for every class" (F3)
- `advisor-mode`: Survey now names reading agents' frontmatter `tools:` line alongside descriptions, matching what Bind's verification actually demands; Own Hands' Read allowance closes the same way Survey's does (F2, F5)
- `advisor-mode`: efficient-md's BIND invocation now cites the installed-skill list already in session context as its discovery evidence (F4)
- `advisor-mode`: Gates permits and requires glossing a finding ID in one plain-word line at first use per message, resolving the contradiction with plain-english's session-coined-label rule (F7)
- `advisor-mode`: the iterated buy-in test and the same-file dispatch rule each collapse to one statement, cutting their near-duplicate copies (F10, F11)
- `README.md`: Advisor row notes the one-time Survey as its sole exception to "never does mechanical work" (F13)

### Added
- `evals/advisor-mode.json`: behaviour fixtures pinning F1/F6, F3, and F7 against regression, no runner exists for behaviour fixtures (debt E24); hand-executed status is recorded in the release PR

## [2.7.0] - 2026-08-25

### Added
- `plain-english`: skill governing the wording of replies and questions to the user — answer first, explain every term the reader may not know, spell out session-coined labels at first use in each message, no coined terms or metaphors, full short active sentences, no "not X, but Y", say it once, one em-dash per sentence, caveats only when they change the decision, and a 2–5 sentence preamble before every question to the user. Session-wide use needs an invoke-first line in the user's CLAUDE.md; nothing shipped invokes it automatically.
- `evals/plain-english.json`: routing fixtures against efficient-md and mine-session for `evals/run-skill-routing.sh`, plus behaviour fixtures recorded as runner debt

## [2.6.0] - 2026-08-25

### Changed
- `advisor-mode`: OWN HANDS rewritten as WHEN / WHEN NOT closed lists — the advisor writes only the ledger, memory, and the handover file, reads only user-given material, its own references, and a return's cited line, and runs no command except the one BIND survey; the Coase cost clause and the "short synchronous probes" category are removed, and no enforcement hook is claimed (`6f374cc`)
- `advisor-mode`: GATES section replaces "never self-judge" — an independent verdict is bought only when the user is absent for the run, the act is irreversible, or a running skill names a judge; command-answerable questions are mechanical VERIFY; one re-gate per artifact, a second BLOCKED goes to the user; the routing table's adversarial example now shows an unattended-run prompt instead of self-review (`6f374cc`)
- `advisor-mode`: the decision ledger opens only when USER PRESENCE flips to absent and is prohibited while the user is present; attended decisions go to the surfacing batch and memory; CLOSE binds per package on those two acts and at session end on "dispatched anything → memory written", replacing the non-empty-ledger trigger (`6f374cc`)
- `advisor-mode`: LEDGER LAW body moved from SKILL.md into `references/ledger.md` (Law + Contract sections); `references/contract-decision-ledger.md` removed; `absent.md`'s move-the-ledger durability procedure replaced (the ledger is born on the durable path) (`6f374cc`)
- `advisor-mode`: `absent.md`'s watchdog, run-start/complete pings, resume-record writes, cheap-resume attempt, dispatch-start confirmation, and `unattended-start.sh` are now run by mechanical hands — the advisor's own-hands law admits no command but the BIND survey (`52383d8`, `5ab9f1d`)
- `advisor-mode`: Dispatch Contract's efficient-md clause restated — invoke-at-BIND kept as an unenforced obligation, plus two prohibitions (never inline what a path can carry; never accept an uncapped return); Bind, Dispatch Contract, Own Hands, Gates, The Ledger headings gain plain descriptors (`6f374cc`)
- `executor-lead` description, README, Iterated Trigger: an attended main-thread package stays with the advisor "while the advisor's own context suffices" — the "own decision ledger" qualifier is gone with the attended ledger (`6f374cc`)

## [2.5.2] - 2026-08-24

### Fixed
- `release`: the `maddog--vX.Y.Z` tag was modelled as a "directory submission pin" — Anthropic's docs say the directory CI re-pins on every push and that tag serves dependents' semver constraints (`plugin-dependencies.md`); E3/D2 corrected, new evidence E21
- `release`: SEAL now runs `claude plugin tag --push` beside the `vX.Y.Z` tag; the second-channel check is retired (L12: one mechanism in, one out)

## [2.5.1] - 2026-08-24

### Fixed
- `.claude-plugin`: `plugin.json` and `marketplace.json` descriptions now list the `efficient-md` skill, shipped since 2.5.0 but absent from both manifest texts

## [2.5.0] - 2026-08-18

### Added
- `efficient-md`: new skill — context-residency authoring doctrine (HOT/WARM/COLD/CHANNEL + HUMAN overlay classification, canonical model, per-class exemplar references), shipped initially as `skills/token-residency` (`84350a2`)
- `advisor-mode`: repo-specific decision-ledger contract split out of the generic doctrine into `skills/advisor-mode/references/contract-decision-ledger.md`, so no reader holds a contract citing law they cannot load (`84350a2`)

### Changed
- `token-residency` renamed to `efficient-md` (the handle optimizes for the person; the doctrine keeps its Token-Residency name in the references); description rewritten generic — no internal-only skill names in a shipped skill's routing text; inbound pointers added from `advisor-mode`'s DISPATCH CONTRACT and `author-agent`'s CREATE branch (`4a3c32d`)
- `author-agent`: prohibition-shaped all three rework-budget scope brakes — step 0's cost line must quote an exact count of covered rework rounds before a mid-loop thread or overage round may run; step 1's model-artifact build is prohibited until its own green-lit cost line exists; the covered-round unit is every gate-ruling request after the first, refusals included, closing the apply-with-cuts dodge (`599ae67`, `d72df67`)
- `efficient-md`: dropped the `references/evidence.md` research-table digest; primary-source pointers now ride each Grounding bullet inline (`f41e1f5`)

## [2.4.0] - 2026-08-17

### Added
- `advisor-mode`: THE LEDGER LAW — when/what/how-often contract for the session decision ledger: entries only at decision events, aggregated by event; rationale + reopen-condition per decision; citations as pointers, never restated content; prunable OPEN index; filed entries immutable (`8f81d18`)

### Changed
- `absent.md`: §1 LEDGER FILE → LEDGER DURABILITY — the ledger already exists per the core law; going unattended relocates it plus scratch-cited artifacts to a durable path and re-points citations, the sole sanctioned edit of a filed entry (`8f81d18`)

## [2.3.0] - 2026-08-17

### Added
- `release`: internal release-engineering skill (`/release`) encoding the six-phase ritual (DECLARE→SEAL), REMEDY incident lane, and twelve laws; locked design model committed alongside as its reference (`f736c6a`)

## [2.2.0] - 2026-08-17

### Removed
- `grind`, `grind-pro` skills — `advisor-mode`'s judgment-class routing supersedes the two thin dispatch skills; agents (`executor-fast`, `executor-smart`) unchanged (`849edbb`)

## [2.1.0] - 2026-08-17

### Changed
- `advisor-mode`: full SKILL.md rewrite — BIND contract-checked class binding with visible degradation, never silent substitution; routing redefined as six classes bonded by judgment (mechanical/local/iterated) or structural property (adversarial/web-perception/kept), each with a tier-matched temptation example; four-category own-hands charter (claim verification, state artifacts, session bootstrap, short synchronous probes); PURPOSE line added to the dispatch contract; proportional acceptance spot-checking; BIND and CLOSE stated as prohibitions, not procedures (`367b92d`)
- `absent.md`: channel discovery is per-session, never assumed, with a per-install-mode trigger — plugin installs ship no watchdog/notify script by default; symlink installs must confirm the watchdog LaunchAgent is actually bootstrapped, not just written (`367b92d`)
- `executor-lead`, README: iterated class gains the attended/context qualifier — buy lead only when the package must survive outside the advisor's own context (absence, parallelism with the main thread, context scarcity); an attended package held as the session's main thread stays with the advisor's own ledger (`dde6b4f`)

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
