# maddog Design Decisions

STATUS: ADOPTED 2026-09-11. Supersedes the locked schemas in mechanical-work.md and local-work.md; the production bodies under agents/ and skills/advisor-mode/ are rendered from the contracts this record fixes.

## Purpose

Canonical record of the executor-family redesign decisions. This is the decision layer behind the final contracts; it is not an additional runtime instruction file.

## Architecture

The system routes by **judgment shape**, not task size, token count, or tool count.

```text
READ        → Fast-Read
MECHANICAL  → Fast
BOUNDED     → Smart
EVOLVING    → Lead
INDEPENDENT ACCEPTANCE EVALUATION → Judge
GLOBAL INTENT / AUTHORITY        → Advisor
```

Roles are responsibility boundaries, not model-strength tiers.

## Advisor

- Minimum Necessary Orchestration
- Outcome Over Activity
- Judgment Is Expensive
- Authority Follows Responsibility
- Work Is Paid Once
- Human Judgment Is Scarce
- Advisor owns global intent, routing, authority, acceptance, and escalation.
- Lead owns evolving work inside its delegated boundary.
- No mandatory session-opening or closing ceremony.
- Durable state is created only when continuity or reusable value requires it.
- Judge is optional; risk warrants judging, not ceremony.

## Advisor rendering departures (2026-09-11 review)

- Core Laws are ordered by precedence (authority, outcome, human judgment, judgment, minimum orchestration, work paid once); the earlier law wins. executor-lead's core laws follow the same order.
- Work classification splits by judgment, not state change: read-only reviews and diagnoses route to Smart; a GATE row names Judge. The model-tier axis is one sentence there.
- The dispatch contract is a per-hand table, not a universal field list; byte-identical in advisor-mode and executor-lead.
- A retry counts fresh context as a new basis only when the failure came from stale or exhausted context.
- A dispatch alone never triggers durable state; durable state lives on a path a fresh session can open.
- Unattended/absence rules are a separately acquired skill, not part of Advisor or Lead; advisor-mode's references/absent.md was removed. They also apply when the user leaves mid-run; with none configured, the Advisor tells the user before they leave.
- Questions to the human are Approval, Escalation, or Clarification, under "Asking the Human".
- Advisor carries three user-authority rules beyond the contract: explicit authorization for hard-to-reverse actions, never chained behind a wait; pausing in-flight work on interrupt; instruction-file edits shown verbatim before writing.
- Anti-patterns are reduced to five.

## Lead

- Owns evolving work within a delegated boundary.
- Highest local authority inside its package; cannot expand global scope or intent.
- Delegates Fast-Read, Fast, Smart, and optionally Judge.
- PLAN, CAMPAIGN, DIAGNOSE, and DELIVER are composable work patterns, not mandatory modes.
- No Lead nesting for the same package.
- No self-judging.

## Lead rendering departures (2026-09-11 review)

- Core laws are stated as Lead's own, in the skill's precedence order; package laws follow in impact order (boundary stop, no nesting or self-judging, rent hands never verdicts, evidence drives the next move, do not shadow-orchestrate), and core laws outrank them.
- Boundary stop also covers any hard-to-reverse action or instruction-file edit whose exact action or text the user has not approved through the dispatch; such actions never run behind a wait.
- Each work pattern carries a law: PLAN → Last Responsible Moment, CAMPAIGN → Value of Information, DIAGNOSE → Multiple Working Hypotheses, DELIVER → Fallacy of Composition.
- A frozen plan with no evolving step returns to Advisor with each step classified, unless integration needs judgment carried across steps or the dispatch asked Lead to deliver.
- A slice that is merely hard stays with its hand at a higher model or effort; only an evolving slice is Lead's.
- When its own context nears exhaustion, Lead has a hand write the package state and returns partial.
- For Lead, unattended work is a slice that may outlive its return; with no configured rules, Lead returns to Advisor instead of dispatching it.
- Lead's body uses the skill's layout and ends with five anti-patterns; the dispatch contract is shared byte for byte; the outer return fields stay fixed while the dispatch shapes RESULT.

## Fast

Identity: **executes closed decisions mechanically.**

Action vocabulary:

```text
CHANGE / OPERATE / TRANSFORM / RECOVER / VERIFY / REPRODUCE
```

Specialized laws:
- TRANSFORM → Totality
- RECOVER → Volatility First
- VERIFY → Goodhart
- REPRODUCE → Null Hypothesis

No continuation or session ownership.

## Fast rendering departures (2026-09-11 review)

- The body is rewritten for a low-intelligence model around execution and escalation only, with no identity section; the eval-tuned wording of mechanical-work.md is not kept.
- Core laws are three, ordered one-way doors, stop don't guess, execute only what is closed; the earlier law wins, and core laws outrank pattern laws.
- One-way doors covers every action and instruction-file edits, keeps the prior examples and "copy first", and never runs such an action behind a wait; only the authorization the dispatch carries opens a door.
- A failing VERIFY run or a not-reproduced REPRODUCE is reported, never a stop: done when the done condition only asks for the result, otherwise partial; a doubtful TRANSFORM member is listed and left, never a stop.
- A task holds one or more of six actions and obeys each held action's law; a task that fits none is blocked.
- BLOCKED-ON carries the escalation: the gap or door, what was attempted, and the evidence.

## Fast-Read

Identity: **reports evidence mechanically.**

Action vocabulary:

```text
RECON / EXTRACT / VERIFY
```

Specialized laws:
- RECON → Totality + Effective Value
- EXTRACT → Diplomatic Transcription
- VERIFY → Null Hypothesis

Fast-Read establishes facts; it does not synthesize facts into substantive judgment.

## Fast-Read rendering departures (2026-09-11 review)

- The body is rewritten for a low-intelligence model around reporting evidence and escalation only, with no identity section; the eval-tuned wording of mechanical-work.md is not kept.
- Core laws are three, ordered evidence never judgment, stop don't guess, read only what the question needs; the earlier law wins, and core laws outrank pattern laws.
- No Mutation is not stated as a law because the tools already make Fast-Read read-only; it produces no task artifact, since it holds no write tool.
- A task holds one or more of three actions and obeys each held action's law; a task that fits none is blocked.
- BLOCKED-ON carries the escalation: the gap, what was read, and the evidence so far.
- A claim the evidence contradicts is a VERIFY result, not a stop; a doubtful RECON item is listed and left, never a stop.

## Smart

Identity: **owns bounded judgment.**

Boundary: decides HOW, not WHETHER the package should exist or what the global outcome should be.

Action vocabulary:

```text
BUILD / TRANSFORM / DIAGNOSE / REVIEW
```

Core laws:
- Bounded Decision
- Judgment Earns Its Cost
- Evidence Before Choice
- Do Not Guess
- Boundary Stop

Action-specific laws:
- BUILD → YAGNI
- TRANSFORM → Invariant Preservation
- DIAGNOSE → Falsification
- REVIEW → Normalization of Deviance

## Smart rendering departures (2026-09-11 review)

- Core laws are ordered by impact (bounded decision, boundary stop, do not guess, evidence before choice, judgment is expensive); the earlier law wins, and core laws outrank pattern laws.
- "Judgment Earns Its Cost" is renamed "Judgment is expensive" to match the family, keeping Smart's clause against manufacturing alternatives past the first that clears the bar.
- Boundary stop also covers any hard-to-reverse action or instruction-file edit whose exact action or text the user has not approved through the dispatch; such actions never run behind a wait, and Smart passes a rented hand no more authority than it holds.
- The may / may-not list is dropped; its one unique ban (no product, architectural, or cross-task decisions) joins the bounded-decision law.
- Action types are called action patterns.
- Smart cannot load efficient-md unless the dispatch names it, so the Fast and Fast-Read dispatch fields are stated inline.
- A missing outcome, decision boundary, or DONE-WHEN is a stop condition; Smart never hands blocked work to another hand itself.
- Decisions go in DECISIONS; a durable artifact is written only when the dispatch requires one.
- The body uses the skill's layout and ends with five anti-patterns; the description routes by judgment shape instead of "correctness matters more than cost".

## Judge

Identity: **independently determines whether a delegated target clears its acceptance bar.**

Action vocabulary:

```text
PLAN-REVIEW → Premortem
OUTCOME-REVIEW → Null Hypothesis
```

Judge evaluates; it does not execute, modify, remediate, redefine the acceptance bar, or delegate the verdict.

Verdicts:
- PASS
- FAIL
- STOP when a trustworthy verdict cannot be established

`INCONCLUSIVE` is not a verdict.

## Judge rendering departures (2026-09-11 review)

- Judge runs on opus, not the spec's sonnet: it is called only for high-impact, irreversible, or one-way results, and eval baselines pin it there.
- Core laws gain a fourth, Judgment is expensive, ranked last so independence and evidence always win; the earlier law wins.
- The may-list is dropped; the evaluation boundary is five bans in order of harm, including no scope or architecture decisions and no unrequested implementation advice.
- Review types are called action patterns; PLAN-REVIEW passes only a plan none of its failure paths defeats.
- No dispatch section: Judge holds no Skill tool, so efficient-md is not cited; missing inputs are the first stop condition, and the one outbound dispatch (to Fast-Read) is one line in Evidence.
- Judge rents Fast-Read for mechanical gathering but runs gate commands itself, since Fast-Read holds no shell; a re-gate without its prior verdict is judged fresh and said so in NOTES.
- STOP covers a dispatch pointing at the wrong target or scope; evidence contradicting a claimed result is FAIL.
- A re-gate or dispute counts a prior verdict only when the dispatch restates it, even when the same Judge is resumed for a back-to-back re-gate.
- A verdict is returned, never filed, since Judge holds no write capability. The body uses the skill's layout and ends with five anti-patterns; the dispatch may rename verdicts and shape FINDINGS while the fields stay fixed.

## Shared Laws / Normalization

- **Completion Is a State, Not Ceremony.**
- **RENT HANDS, NEVER VERDICTS.**
- `Do Not Guess` is role-specific: missing decision → Fast stops; missing evidence → Fast-Read reports insufficiency; material uncertainty → Smart investigates within boundary.
- `Null Hypothesis` is intentionally reused where the falsification object differs.
- Dispatches are contracts, not forms. Advisor and Lead use a byte-identical delegation contract.
- The receiving hand executes within the dispatch boundary; it does not redefine the contract.
- Capabilities and constraints are separate axes.
- `efficient-md` is a dispatch dependency, not a session dependency.
- Complexity does not determine intelligence tier.
- Completion does not trigger ceremony.

## Explicit Non-Decisions

The redesign intentionally does **not** introduce:

- a Researcher role
- mandatory session ledgers
- mandatory memory files
- mandatory Judge after delegation
- universal dispatch forms
- automatic Lead escalation for difficult work
- Lead mode-transition ceremony
- continuation for Fast / Fast-Read / Smart / Judge
- speculative Smart abstractions
- separate MIGRATE / RECOVER / VALIDATE Lead patterns
