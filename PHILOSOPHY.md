# Philosophy

> This file states the beliefs this repository is designed under — reread it
> when a design choice is unclear. It is written for the author,
> contributors, and adopters of this repo.
>
> This is a philosophy of **delegated intelligence**, not merely multi-agent
> orchestration.

## 1. Judgment is expensive

Spend intelligence where decisions change outcomes.

Task difficulty is not the routing signal. **Judgment shape is.**

- Closed decisions → mechanical execution.
- Bounded local decisions → smart execution.
- Decisions that evolve with discovery → persistent/iterated execution.
- Consequential product or architectural decisions → retained by the
  appropriate authority.

More intelligence is not inherently better. Excess intelligence creates
cost, latency, over-analysis, and unnecessary decisions.

**Rule:** Spend intelligence on decisions, not mechanics.

### Consequences

- Hard subject does not automatically require stronger model.
- Ambiguous intent is not solved by thinking harder; it may require missing
  context or authority.
- A Judge should not become an architect merely because it can reason about
  architecture.
- Model tier follows responsibility and judgment shape.

## 2. Work is paid once

Preserve useful work so downstream agents build on it instead of
rediscovering it.

Reusable work includes:

- evidence
- decisions
- constraints
- failed paths that eliminate future options
- artifacts
- verification results

Raw reasoning transcripts and exploratory noise are not automatically
reusable.

**Rule:** Reuse completed work until its basis changes.

New evidence may invalidate prior work. When it does, spend intelligence
again only on the affected decision.

### Consequences

```text
reason → useful result → durable artifact → reuse
```

A downstream agent should not repeat research merely because it cannot see
the original conversation.

Human decisions are work too. Once a human resolves a question, record that
decision so later agents do not ask again.

## 3. Authority follows responsibility

An agent gets only the authority and capabilities required by its
responsibility.

```text
responsibility → authority → capability
```

Role instructions alone are weak. Structural boundaries are stronger.

Examples:

- A Judge cannot edit the work it judges.
- An Executor cannot silently redefine product requirements.
- A local executor cannot make package-wide architectural decisions.
- A Lead can delegate hands/evidence, but retains judgment within its
  boundary.

**Rule:** Do not grant authority merely because an agent is capable of
using it.

This preserves independence, accountability, and containment.

## 4. Human judgment is scarce

Spend human judgment only on decisions requiring human authority.

Before interrupting a human:

1. Check existing decisions and artifacts.
2. Resolve mechanical uncertainty.
3. Let the appropriate agent resolve engineering judgment.
4. Escalate only when the unresolved decision crosses the agent's authority
   boundary or carries human/business consequence.

Human should receive a **compressed decision**, not raw uncertainty.

Bad:

> What should I do?

Better:

> A preserves compatibility; B reduces complexity but requires migration.
> Recommend A. Confirm?

**Rule:** Human is not an execution API. Human is the authority for
decisions agents do not own.

Human decisions become durable work and should not be repeatedly requested.

## 5. Separate responsibility from mechanism

Roles, responsibilities, authority, and contracts define system behavior.
Runtime mechanisms implement them.

The core should not depend on one harness's mechanics.

```text
roles / contracts / laws
          ↓
      runtime adapter
          ↓
Claude / Codex / future runtime
```

Harness neutrality is therefore an **architectural consequence**, not the
deepest reason for the system.

**Rule:** Abstract responsibility and authority; adapt mechanics.

Harness-specific capabilities may be exploited when useful. Portability
must not become a reason to reject useful runtime capabilities.

## 6. Outcome over activity

Agent activity is not progress.

Every action must earn its cost by doing at least one of:

- changing the outcome
- resolving meaningful uncertainty
- producing reusable evidence/artifact
- enforcing a real safety boundary
- establishing that work is complete

Otherwise, do not do it.

**Rule:** Use the minimum orchestration required for a trustworthy outcome.

This does **not** mean shortest path or fewest agents. Complex, risky work
may legitimately require more reasoning, delegation, and verification.

It means every layer must justify its existence.

### Anti-bureaucracy test

Never:

```text
role → find something for role to do
```

Prefer:

```text
need → responsibility → minimum required activity
```

Stopping is a successful outcome when the requirement is already satisfied.

# The resulting system model

These principles form a distributed decision system:

```text
                    USER
                      │
             intent / human authority
                      ↓
                   ADVISOR
       allocates cognition + authority
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        FAST        SMART        LEAD
      execute      decide       evolve
          │           │           │
          └───────────┼───────────┘
                      ↓
                work products
                      ↓
               acceptance / gate
                      ↓
                    DONE
```

The executor tiers are not simply a ladder of intelligence.

```text
FAST  = closed decisions
SMART = bounded decisions
LEAD  = evolving decisions
```

The Advisor is not a manager supervising every action.

It is an **allocator of cognition and authority**.

# Design test

When a new rule is proposed, ask:

1. Which principle does it protect?
2. What concrete failure does it prevent?
3. What cost does it introduce?
4. Can structural design enforce it instead of prose?
5. Does it remain necessary for this task shape?
6. Can the system stop earlier without reducing trustworthiness?

If no concrete answer exists, the rule is probably ceremony.
