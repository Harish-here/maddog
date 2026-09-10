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

## Lead

- Owns evolving work within a delegated boundary.
- Highest local authority inside its package; cannot expand global scope or intent.
- Delegates Fast-Read, Fast, Smart, and optionally Judge.
- PLAN, CAMPAIGN, DIAGNOSE, and DELIVER are composable work patterns, not mandatory modes.
- No Lead nesting for the same package.
- No self-judging.

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
