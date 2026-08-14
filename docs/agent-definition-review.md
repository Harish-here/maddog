# Reviewing agent definitions — draft checklist

Status: DRAFT — captured 2026-08-14 from two live premortem reviews (executor
family revamp: 18 findings; advisor-mode revamp: 14 findings). To be expanded
and turned into a reusable review contract in a later session.

An agent definition is dispatch logic plus behavior spec. Reviewing one is a
distinct discipline from reviewing code. Eight dimensions, each of which
caught real load-bearing defects in the source reviews:

1. **Spec fidelity** — every element of the binding design present and
   uncontradicted; shared/verbatim texts actually identical across files.
2. **Routing partition** — the frontmatter descriptions across the whole
   family must form a partition: every plausible task shape selects exactly
   one agent. Hunt for keyword monopolies (a word appearing in only one
   description captures every task containing it) and for shapes that match
   two descriptions or none.
3. **Law contradiction** — a rule cancelled by another rule reads as agent
   failure. Check every obligation against every prohibition; prohibition
   wins in practice.
4. **Behavioral realism** — instructions the agent cannot follow as written:
   references to capabilities it lacks, unfillable return-contract fields,
   undetectable trigger conditions, thresholds with no test.
5. **Obligation-weakness audit** — list every affirmative obligation whose
   skipping is silent; for each, name the structure (hook, tool removal,
   artifact-first ordering, file layout) that could convert it to a
   prohibition or make skipping loud.
6. **Doc coherence** — README, CLAUDE.md, plugin/marketplace manifests, and
   the agent files must tell one story: same family membership, same role
   identities, no stale claims, model pins stated where the doctrine says
   and nowhere else.
7. **Decoupling** — no dependency on any consumer's implementation (workflow
   names, artifact formats); capability references must name the capability
   and carry a real degraded fallback.
8. **Token-weight audit** — for always-resident text (skills, descriptions):
   line by line, what could be pay-per-use, what duplicates what the
   registry already injects, and — the reverse check — what pay-per-use
   text MUST be resident because the agent needs it before it knows to load
   the reference. Beware partial duplication: an incomplete copy of another
   file's rules actively teaches the wrong closure.

## Open design question (to settle in the follow-up session)

Where should this checklist live?
- **Option A — dedicated reviewer agent**: bakes the discipline in; routable
  by description; but one more agent to maintain, eval, and keep coherent.
- **Option B — dispatch-time contract**: keep executor-judge DESIGN-REVIEW
  generic and hand it this file as the contract in the dispatch prompt;
  domain knowledge stays in data, the judge stays universal.
Current lean: Option B — the two source reviews were exactly this shape
(generic opus reviewer + explicit dimension list) and both performed well.

## Evidence base

- Family premortem (agents/executor-lead.md, executor-judge.md, README):
  18 findings, 13 load-bearing — including a law-cancels-law defect and two
  routing keyword monopolies.
- Advisor premortem (skills/advisor-mode): 14 findings, 11 load-bearing —
  including an obligation cancelled by a prohibition and a trigger condition
  that missed the two most dangerous absence shapes.
