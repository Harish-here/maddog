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
work ALWAYS goes to Fast, reads to Fast-Read, bounded work to Smart; the sole
exception is work so small that dispatching costs more than doing it. The
exception carries no size threshold by decision (see Non-Decisions).

## Shared constitution

Text that every dispatcher or every executor needs is written once and
carried byte-identically. Four fragments, canonical in
docs/executor-family/constitution.md:

| Fragment | Content | Carriers |
|---|---|---|
| LAWS | completion is a state; never retry blindly; durable state off by default; authority (what needs it, exact action or standing grant, no inference, reversibility test with the discarded-work exception) | all six |
| ROUTE | route by shape; fast-tier ALWAYS with the sole exception; never do a hand's work; the shape table; hand preference order; no more authority than held | Advisor, Lead |
| CONTRACT | OUTCOME, BOUNDARY, DONE-WHEN; add only what is useful; cite by path; capped returns with cited claims | Advisor, Lead, Smart, Judge |
| VERIFY | a return is evidence, not proof; check against DONE-WHEN; verify load-bearing claims at cited evidence, where a spot-check or re-run gate is verification and redoing the work is not; keep observed, produced, concluded apart | Advisor, Lead, Smart, Judge |

Decisions that fix the mechanism:

- Fragments name no role as their subject; second person addresses whichever
  role carries them. Headings around a fragment belong to the carrying file.
- No tier-specific additions inside a fragment. What varies by role is
  stated in the role's own body in one line each: which hands it may rent,
  what its direct work is, what acceptance means for it.
- ROUTE is carried only by roles that own no execution, Advisor and Lead.
  Smart does its own work and rents two hands under its own rule; Judge
  rents one hand and never routes; the fast tier dispatches nothing and
  carries LAWS only.
- LAWS holds only what every role can act on. "Show an edit and write after
  approval" and "an irreversible action runs as its own dispatch" are the
  Advisor's vantage (it can show, wait, and dispatch); each executee already
  states the hand-side form in its own law ("the dispatch authorizes that
  exact action", "never behind a wait"), so those two sentences live in the
  Advisor body.
- Every executor body ranks the Standing Laws explicitly: they bound every
  hand and never license what a core law forbids; among core laws the
  earlier wins.
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
- A change confined to a user-named workspace is reversible unless it
  discards work that exists nowhere else (a reset, a clean, a force-push).

## Advisor

advisor-mode is always-resident once invoked and is held under 500 words on
the strictest count (headings, table rows, and arrow glyphs included). It
carries the four fragments plus Advisor-only text; the body is its own
record of what that text is.

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
the user's waiver; a hand's own call returns to it as CONTINUE; compaction
reload;
the acceptance boundary; instruction files defined; the reversibility test;
standing grants; BOUNDED diagnosis qualified by a known evidence surface.

CLAUDE.md carries one Advisor line so the compaction reload survives
compaction: the skill body cannot preserve a rule that compaction removes.

## Lead

Unchanged: identity, core laws in precedence order, package laws in impact
order, the four work patterns with their laws, batching prohibition, gates,
continuation and retry, ambiguity and escalation, durable state, unattended
work, completion, anti-patterns, return envelope.

Rendered from fragments: Orchestration keeps Lead's lines above ROUTE:
classify each slice never the whole package; a merely hard slice is not
Lead's; direct work is reasoning plus the reads its judgment must hold
first-hand (verification, carried investigation), with fact-gathering to
Fast-Read and every change, whatever its size, to a hand. Below ROUTE: an
evolving slice inside the package stays Lead's, one that is its own package
is a boundary stop. Batching: a hard-to-reverse action always runs as its
own dispatch. Dispatch Contract
is CONTRACT plus Lead's efficient-md line and "each slice independently
executable." Returns is Lead's acceptance line (a slice is accepted only to
decide the next move; Advisor accepts the package) around VERIFY, then
continue, re-dispatch, reroute, or return.

Sentences that restated LAWS (the Completion opener, the Durable State
opener) are removed; Lead-specific continuation and partial-return rules stay.

## Smart

Unchanged: identity, core laws, action patterns with laws, stop conditions,
decisions and durable state, completion, anti-patterns, return envelope.

Rendered from fragments: the RENT HANDS bullets are replaced by Smart's own
rent rule (Fast for a closed mechanical slice, Fast-Read for a fact-finding
read, when cheaper than doing it inside the task; evidence it must judge it
reads itself; never rent to avoid work or past Boundary stop; never load an
unnamed skill) followed by CONTRACT and VERIFY. Smart does not carry ROUTE:
the coherence review showed "ALWAYS goes to Fast" and "never do a hand's
work yourself" telling the doer to rent out its own job. Added from the
same review: inside its boundary Smart dispatches its own attempts, so an
adapted retry on a recorded basis is not blind; RESULT carries what already
changed on disk when blocked, and a conclusion for DIAGNOSE and REVIEW;
Completion states what done means. The Execution intro and the Completion
opener that restated other text are removed.

## Judge

Unchanged: identity, core laws, evaluation boundary, action patterns, stop,
completion, anti-patterns, return envelope, opus pin.

Rendered from fragments: the RENT HANDS paragraph is replaced by two Judge
lines (Fast-Read is the only hand it may dispatch; gate commands run in its
own shell) followed by CONTRACT and VERIFY inside Evidence, then the three
evidence bullets. Judge carries no ROUTE: it never routes. From the
coherence review: a gate that would change the checkout or a shared service
is a finding, never run; FINDINGS may be "none" on STOP; NOTES names the
pattern applied when it differs from the hint. The Completion opener and the
retry sentence that restated LAWS are removed. The structural no-write invariant is enforced by its
tool list and stated once in Advisor's gate section.

## Fast and Fast-Read

Unchanged except: LAWS is inserted before Core Laws, the Completion
sentence that restated LAWS bullet 2 is removed, and the Standing Laws are
ranked. Fast, from the coherence review: One-way doors lists a reset or
clean that discards uncommitted work, and accepts authorization by a stated
rule with a workspace and limits (TRANSFORM's glob shapes); RESULT carries
the copy and reversible steps already taken when blocked; a failed step is
run once and reported. The 2026-09-11 departures for both hands stand.

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
- Coherence review, one blank-context reviewer per executor, six checks
  each (contradiction, role leak, inert or misleading, seam gap, return-field
  matrix, trigger realism): four of five INCOHERENT before the fixes above.
  The load-bearing findings were all the same shape: fragment sentences
  written from the Advisor's vantage (show, wait, own invocation, ALWAYS
  dispatch, never reproduce) landing in a role that does the work or runs
  the gate. Fixed by narrowing LAWS and ROUTE to what every carrier can act
  on and moving the rest to the Advisor body, plus one seam line per role.
  Also surfaced and fixed: the unranked Standing Laws, STATUS blocked being
  unreachable under the partial rule, and RESULT "empty when blocked" hiding
  changes already on disk.

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
- a size threshold for "targeted reads", the same elastic zone as the
  small-work exception

## Debt

- mechanical-work.md and local-work.md describe schemas the bodies no
  longer render from; conformance-check.py reports NONCONFORMING on HEAD.
- CHANGELOG and plugin version are updated by the release skill before
  merge; advisor-mode and the executor bodies are SHIPPED surfaces.
