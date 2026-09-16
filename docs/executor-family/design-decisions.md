# maddog Design Decisions

STATUS: ADOPTED 2026-09-16. Supersedes the 2026-09-11 record and the locked
schemas in mechanical-work.md and local-work.md. The production bodies under
agents/ and skills/advisor-mode/ are rendered from the contracts this record
fixes; the four shared fragments are rendered from
docs/executor-family/constitution.md and checked by scripts/fragment-check.py.

## Purpose

Canonical record of the executor-family design as of the advisor-mode
compression and the shared constitution. This is the decision layer behind
the contracts; it is not a runtime instruction file and nothing loads it.

## Architecture

The system routes by **judgment shape**, not task size, difficulty, or
subject.

```text
READ        → Fast-Read     facts as found; no judgment
MECHANICAL  → Fast          decisions all closed
BOUNDED     → Smart         implementation choice, criteria review,
                            diagnosis with a known evidence surface
EVOLVING    → Lead          next action depends on discovery
GATE        → Judge         independent verdict before one-way outcomes
GLOBAL      → Advisor       outcome, scope, routing, acceptance
```

Roles are responsibility boundaries, not model-strength tiers. Mechanical
work ALWAYS goes to the fast tier and bounded work to Smart; the sole
exception is work so small that dispatching costs more than doing it. The
exception carries no size threshold by decision (see Non-Decisions).

## Shared constitution

Text that every dispatcher or every executor needs is written once and
carried byte-identically. Four fragments, canonical in
docs/executor-family/constitution.md:

| Fragment | Content | Carriers |
|---|---|---|
| LAWS | completion is a state; never retry blindly; durable state off by default; authority (hard-to-reverse, instruction files, reversibility test, exact-action or standing grant, no inference, no waiting) | all six |
| ROUTE | route by shape; fast-tier ALWAYS with the sole exception; never do a hand's work; the shape table; hand preference order; no more authority than held | Advisor, Lead, Smart, Judge |
| CONTRACT | OUTCOME, BOUNDARY, DONE-WHEN; add only what is useful; cite by path; capped returns | Advisor, Lead, Smart, Judge |
| VERIFY | a return is evidence, not proof; check against DONE-WHEN; verify load-bearing claims at cited evidence; never reproduce; keep observed, produced, concluded apart | Advisor, Lead, Smart, Judge |

Decisions that fix the mechanism:

- Fragments hold no role-relative words (no "you", "your package", no role
  name as subject). Headings around a fragment belong to the carrying file.
- No tier-specific additions inside a fragment. What varies by role is
  stated in the role's own body in one line each: which hands it may rent,
  what its direct work is, what acceptance means for it.
- The fast tier carries LAWS only; it dispatches nothing.
- A fragment is edited in constitution.md and propagated; a copy is never
  edited in place. `scripts/fragment-check.py` byte-compares every
  (carrier, fragment) pair and is the conformance gate for this family.
  `scripts/conformance-check.py` and the Part II schemas it reads are
  superseded and report NONCONFORMING against the current bodies; they are
  retained as history, not as a gate.
- A shared reference file was rejected: Smart may not load a skill the
  dispatch did not name, and agent bodies may not cite a plugin-root path.
  Resident text was the only way to reach the whole family.
- The reversibility test is stated without git vocabulary: hard-to-reverse
  means publishing, deleting, or changing state others depend on; a change
  confined to a user-named workspace is reversible. Git specifics live only
  in Fast's one-way-doors law.
- A standing grant is a defined form of authorization: it names the action,
  the workspace, and its limits. A grant without limits is not a grant.

## Advisor

advisor-mode is always-resident once invoked and is held under 500 words on
the strictest count (headings, table rows, and arrow glyphs included). It
carries the four fragments plus Advisor-only text:

- the loop: OUTCOME → CLASSIFY → ASSIGN → DISPATCH → EVALUATE → DONE
- dispatch first; routing inspection transfers no ownership; when
  uncertain, dispatch; after context compaction, re-read the skill file
- the efficient-md line, scoped to prompt construction, no reread if loaded
- acceptance outcomes: ACCEPT / CONTINUE same owner / REROUTE / blocked by
  whose call it is (Advisor's, user's, the hand's) / JUDGE
- the gate ladder: factual → command or evidence; reversible → user's
  review; irreversible or one-way → Judge; repo instruction files set floors
  the ladder cannot lower, only the user can waive one, recorded where the
  change lands
- ownership: Advisor accepts the package; Lead owns routing inside it; no
  shadow-orchestration; acceptance checks DONE-WHEN and cited evidence,
  quality judgment beyond that is a hand's
- uncertainty order: existing decisions, then artifacts, targeted reads,
  delegated investigation; ask only for ambiguous intent or the user's
  authority; compressed questions; do not invent requirements
- finish: stop when the outcome is satisfied and accepted

Departures from the 2026-09-11 rendering, each dropped as non-behavioral or
superseded by a fragment: the six core laws with precedence (PHILOSOPHY.md
holds them; the body carries one law, route by shape); the per-hand dispatch
table (CONTRACT is the universal triad; the dispatcher decides the rest);
capability and constraint enumeration; the session-start do-not list;
batching permission; anti-patterns; the configured unattended procedure
(reduced to "never infer approval from absence" in LAWS); interrupt handling;
the Approval / Escalation / Clarification labels (the triggers stay, the
labels went); "capabilities are not roles" (never cited by a probe).

Added since 2026-09-11: the explicit loop; hand preference order (repository
hand, installed family, built-in equivalent); gate floors from repo files and
the user's waiver; blocked routing by whose call it is; compaction reload;
the acceptance boundary; instruction files defined; the reversibility test;
standing grants; BOUNDED diagnosis qualified by a known evidence surface.

CLAUDE.md carries one Advisor line so the compaction reload survives
compaction: the skill body cannot preserve a rule that compaction removes.

## Lead

Unchanged: identity, core laws in precedence order, package laws in impact
order, the four work patterns with their laws, batching prohibition, gates,
continuation and retry, ambiguity and escalation, durable state, unattended
work, completion, anti-patterns, return envelope.

Rendered from fragments: Orchestration keeps Lead's three lines (classify
each slice never the whole package; a merely hard slice is not Lead's; direct
work is reading, read-only commands, reasoning) above ROUTE. Dispatch Contract
is CONTRACT plus Lead's efficient-md line and "each slice independently
executable." Returns is Lead's acceptance line (a slice is accepted only to
decide the next move; Advisor accepts the package) around VERIFY, then
continue, re-dispatch, reroute, or return.

Known duplicates left in place by decision: the Completion opener and the
Durable State opener restate LAWS bullets 1 and 3.

## Smart

Unchanged: identity, core laws, action patterns with laws, stop conditions,
decisions and durable state, completion, anti-patterns, return envelope.

Rendered from fragments: the RENT HANDS bullets are replaced by two Smart
lines (Fast and Fast-Read are the only hands it may rent; never load a skill
the dispatch did not name) followed by ROUTE, CONTRACT, VERIFY as their own
sections. Smart carries table rows it never routes (EVOLVING, GATE); they
grant nothing, since its own line names its rentable hands.

## Judge

Unchanged: identity, core laws, evaluation boundary, action patterns, stop,
completion, anti-patterns, return envelope, opus pin.

Rendered from fragments: the RENT HANDS paragraph is replaced by two Judge
lines (Fast-Read is the only hand it may dispatch; gate commands run in its
own shell) followed by ROUTE, CONTRACT, VERIFY inside Evidence, then the
three evidence bullets. The structural no-write invariant is enforced by its
tool list and stated once in Advisor's gate section.

## Fast and Fast-Read

Unchanged in every respect except one: LAWS is inserted before Core Laws.
Their bodies were not otherwise re-rendered; the 2026-09-11 departures for
both hands stand. Known duplicate left in place: "Never retry on your own; a
resumed dispatch with a new basis is a new task" restates LAWS bullet 2 in
each body.

## Evidence

The eval harness was removed 2026-09-15. Behavior was checked instead by
blank-context probes: a subagent reads only the skill body and CLAUDE.md and
answers scenarios with what it would do, citing the deciding line.

- Routing probe, 13 scenarios, three runs: eight identical across all runs,
  two converged after edits (diagnosis routing, instruction-file definition),
  two vary benignly, one asks the user by design ("ship it").
- Pressure probe, 15 adversarial scenarios, three runs: two hard bends in
  run one (gate-floor waiver, cheaper Judge), zero after the waiver rule;
  the standing-grant wobble (blanket approval, overnight CI loop) persisted
  until the standing-grant clause.
- Targeted probe, 5 grant and compaction scenarios: five held, including a
  grant with a fix that edited CI config (held) and a compaction whose
  summary never named advisor-mode (CLAUDE.md line fired).
- Decay: every run re-read the same three regions most, the authority law,
  the gate ladder with its floor line, and the BOUNDED boundaries. No new
  region appeared as edits landed.

Residuals accepted without a rule, because every run behaved correctly
without one: the small-work threshold; concurrency on one file; the remedy
for a capped return breached; the remedy for a landed scope overreach; the
selector among the three blocked resolvers; a standing grant's limits being
lost to compaction (the safe failure is to hold the push and ask).

## Non-Decisions

The design intentionally does **not** introduce:

- a size threshold for the small-work exception
- tier-specific additions inside any fragment
- a per-hand dispatch table
- a shared reference loaded on demand in place of resident text
- a Researcher role
- mandatory session ledgers or memory files
- mandatory Judge after delegation
- automatic Lead escalation for difficult work
- Lead mode-transition ceremony
- continuation for Fast / Fast-Read / Smart / Judge
- rules for behavior the probes showed correct without them

## Debt

- mechanical-work.md and local-work.md describe schemas the bodies no
  longer render from; conformance-check.py reports NONCONFORMING on HEAD.
- Residual LAWS duplicates in Lead, Fast, and Fast-Read (listed above).
- CHANGELOG and plugin version are updated by the release skill before
  merge; advisor-mode and the executor bodies are SHIPPED surfaces.
