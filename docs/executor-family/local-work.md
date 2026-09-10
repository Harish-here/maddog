# Local work — why executor-smart is built this way

STATUS: DRAFT. Adoption is gated on the fixture run named in II.7.

This document is for someone meeting the local-judgment tier for the first
time: a reader who knows Claude Code and agents, and wants to understand,
review, or re-author `agents/executor-smart.md`. Part I explains why the
hand exists and why its instruction file looks the way it does. Part II is
the locked schema that file is rendered from. Beliefs this design serves:
`PHILOSOPHY.md`.

---

# Part I — The reasoning

## I.1 What the judgment hand is for

Some work's wording is not a lookup, it is the work: which idiom a change
should wear, where a seam goes, whether a finding is load-bearing. That
call cannot be pre-decided by the caller and cannot be left mechanical, but
it also should not cost the advisor's own attention. Four reasons this
tier exists, re-argued from the cheap tier's four.

1. **It prices judgment instead of defaulting it.** Without a tier priced
   between "fully decided" and "the advisor's own reasoning," an
   in-boundary call either burns the top model or gets silently guessed by
   a hand built to be dumb. Smart is the price of "this needs a call, not
   a lookup."
2. **It protects the advisor's context.** Same mechanism as the cheap
   hand: a fresh-context hand makes the call and returns a distilled
   result, never the reasoning trail.
3. **It is a check on the advisor's own discipline.** A boundary that
   was not actually closed shows up as `blocked`, naming the gap — the
   caller finds out its own thinking was unfinished, the same signal the
   cheap tier gives one level down.
4. **It gets safety from visibility, not from smartness alone.** This
   hand is allowed to decide, but only inside the boundary, and every
   call it makes is recorded where the caller can see and overrule it.
   The danger at this tier is not improvising — it is deciding silently.

**Every line either names a decision the hand owns or forbids one it does
not; no line coaches it on how to judge well.**

## I.2 Why one hand, and why it may dispatch

One agent because one tool set is the boundary that makes "local judgment,
never architecture" enforceable: read, search, write, edit, shell, skill,
dispatch. Dispatch is new here — the hand may rent the two cheap hands for
the mechanical remainder of a task whose decisions it has already closed.
This is a permission, never a requirement: closed work moving to a cheaper
hand is bought at the cheap price, but nothing about this schema obliges
the hand to look for delegation opportunities. The allowlist
(`executor-fast`, `executor-fast-read` only) is structural, enforced by
`judge-dispatch-guard.sh`, never a body sentence — a body-level ban is the
kind of obligation-in-disguise that mechanical-work.md I.3 measured
degrading under pressure on 2026-09-01; the schema does not repeat that
mistake here.

## I.3 Why laws, and why they forbid

Same evidence base as the cheap tier (mechanical-work.md I.3): a
prohibition with a worked example still failed under eval; a prohibition
with a tooth in the return did not. Applied here: DECISIONS non-empty is
the tooth against an invisible decision, DELEGATION LOG is the tooth
against a dispatched-but-unclosed call, and each row's RESULT vocabulary
(APPLIED | REFUTED | NO EVIDENCE, a named idiom, a named seam) is the
tooth against a plausible-but-wrong close. Worked examples are dropped
from every law line; a row that loses in the after-run gets its example
back as rendering on that row alone, never as law text.

## I.4 How the kinds of action were found

The eight prior modes were a hypothesis, checked by re-running
mechanical-work.md I.4's three steps inverted:

(a) **Enumerate the judgment verbs** mechanical excluded — choose a
    refactor's shape, write a test with no given expectations, explain a
    failure, review, plan, design a seam, watch a live job — plus the
    current description's verbs, plus **dispatch a closed slice to a
    cheaper hand**.
(b) **Keep the ones whose open call sits inside one boundary**, with no
    cross-step memory and no architecture.
(c) **Ask how a hand with judgment but no architecture and no memory
    damages each, and merge by damage**, against the seed list: over-reach,
    under-reach, invisible decision, plausible-but-wrong (which splits by
    mode: foreign idiom, behaviour lost in transit, an implicit contract,
    a seam cut where tidy, a cause never reproduced, a finding closed by
    compliance, precedent waved through, a resource never released),
    unbought spend, delegated judgment.

**What survived, merged, or moved.** BUILD, AUTHOR, FIX, REVIEW, and
CHOREOGRAPH survive as rows on their original damage (idiom, implicit
contract, inference, precedent, resource). PORT and DECOMPOSE survive
despite low frequency in the census below — their damage (behaviour lost
in transit; a seam cut where tidy) is distinct from every other row's, so
merging them would hide a real failure. DIAGNOSE merges into FIX as one
inference row: it never fired alone in 162 dispatches, and "cause never
reproduced" and "finding closed by compliance" are the same failure
(closing on a story instead of evidence) at two points in one workflow.
DECIDE (SATISFICING) and STOP UP (THE ANDON CORD) are not mode rows here
either — they never were: the pre-schema body already held them as
cross-cutting laws over all eight modes, not modes themselves. STOP UP
keeps a numbered row (R10) because, like mechanical's R5, its failure
(over-reach and under-reach at the boundary) is real and fixture-bearing
but is carried entirely by II.4's cord paragraph, never rendered as a
separate law block. DECIDE's failure (invisible decision, unbought spend)
is not given its own row: invisible decision is covered by the Stance's
"make it, list it" clause and X3's DECISIONS tooth; unbought spend is
covered by the Stance's ban on weighing an alternative past the first that
clears the bar, traced the same way in DECISIONS. A third cross-cutting-only
row would duplicate rather than insure anything new. This is one
departure from a flat nine-row hypothesis, recorded here rather than
silently folded in.

**History check.** `evals/runs/executor-smart-dispatch-census.md` (162
dispatches, 2026-08-13 to 2026-09-09) gives: AUTHOR 66+3, FIX 26+12,
CHOREOGRAPH 22+11, BUILD 17+2, REVIEW 7, DIAGNOSE 0+2, PORT 1, DECOMPOSE 1,
NO FIT 7. Every NO FIT row is covered by an existing row's instance list,
never left out of scope:

- Five "produce several concrete variants for a person to choose" rows
  (logo and wordmark candidates, the RENDER verb) are instances of
  BUILD/R1: a variant set still answers to the design system's idiom,
  never the hand's own taste — CONCEPTUAL INTEGRITY already insures
  exactly that failure. A variant set that is not meaningfully distinct —
  a false choice — is a separate, unfixtured failure, logged as a row
  candidate at R1's residue, awaiting a real dispatch.
- One "quantify a cost claim from historical data" row is an instance of
  FIX/R5: a number is a claim like any other, and starts NOT ESTABLISHED
  the same as a bug report.
- One "classify a corpus against a fixed taxonomy" row (this census
  itself) is an instance of REVIEW/R6: sorting items into named
  categories against a standard is precedent-auditing, and waving a
  borderline item into "same as before" is exactly NORMALIZATION OF
  DEVIANCE's failure.

No new row was needed for any of the three census verbs (RENDER, MEASURE,
SURVEY); each is an instance of a row already derived on different
grounds. Separately, five commit-and-push dispatches in the census's
AWKWARD FIT list are a routing leak (CHOREOGRAPH is live/stateful work, a
bare commit is neither), noted as advisor debt outside this schema's
scope, not fixed here.

## I.5 What is model-independent

| Locked in Part II, byte for byte | Rendering, free to the authoring model |
|---|---|
| each row's LAW line: name and sentence, ending at its residue | identity paragraph, mode definitions, instance lists |
| the four cross-cutting laws (X1–X4) | how verbs group under mode names |
| the seven-field return envelope and the PRECEDENCE sentence | connective prose, examples if any |
| the stance, composition, stop list, and cord paragraphs | sentence order inside a block |

A script (`scripts/conformance-check.py --hand smart`) checks that every
locked item is present, verbatim. A judge then reviews only the
rendering. Adopting this schema is itself a change under the same
referee (II.7).

## I.6 How to read Part II

Each row in II.1 names a failure, the actions it bites, the LAW that
insures it, the law's source, and where the leftover goes. A body renders
a row as a mode block — name and instance list — followed by the LAW line
in its own block, tagged with the kind or kinds it binds. II.4's stance,
composition, stop list, and cord render on the body outside any mode.
II.5 maps mode names onto rows and fixes the render order. II.6 says when
a row may be added. II.7 says what the script checks, and what must
happen before this schema stops being a draft.

---

# Part II — The schema (locked)

## II.1 Failure rows

Each row: the failure, the actions it bites, the LAW (locked: name then
sentence, ending at its residue), the source, and the residue's
destination. A body carries the name and sentence together, as one line,
in its own block, apart from the mode block it binds. Each block — mode
block, and law block — is held to a 32-word cap (`wc -w`, name through
last word), except where a `Cap note:` states which substance did not fit
and the measured count, capped at 42. A head tag, where a law block
carries one, sits outside this count — the count starts at the law's
name, after the tag. Two blocks exceed even the 42-word grant and are
named here as their own exception: X4 RENT HANDS, NEVER VERDICTS,
measured at 102, and the II.4 stance, measured at 74.

### R1 — Idiom
Failure: implements correctly but in a convention foreign to the system.
Verbs: implement a feature, a small in-boundary design choice, a variant
set, into a system that already has a way of doing this.
LAW: CONCEPTUAL INTEGRITY — Match the system's existing idiom; a correct
change in a foreign convention still fails. DECISIONS names the idiom
followed.
Source: Fred Brooks.
Residue: DECISIONS; a variant set that is not meaningfully distinct — a
false choice — is a named failure with no fixture yet, logged here as a
row candidate awaiting a real dispatch, not merged into DECISIONS's idiom
failure.

### R2 — Transit
Failure: loses behaviour on the way to a new home.
Verbs: migrate across versions, move across modules or repos, un-ship a
skill, retarget a directory.
LAW: CHARACTERIZATION TESTS — Pin behaviour before moving it; what cannot
be pinned is never claimed preserved. NOT DONE names it, STATUS partial.
Source: Michael Feathers.
Residue: NOT DONE, STATUS.

### R3 — Implicit contract
Failure: leaves a precondition, postcondition, or boundary for the next
executor to guess.
Verbs: write a plan, spec, brief, doc, or gate packet another hand
executes.
LAW: DESIGN BY CONTRACT — State preconditions, postconditions, boundary;
whatever stays implicit becomes the reader's guess and is never assumed
closed. RESULT states them.
Source: Bertrand Meyer.
Residue: RESULT.

### R4 — Seam
Failure: splits along the tidy line instead of the line that actually
changes.
Verbs: split an oversized file, a plan, a skill, or a doc into parts.
LAW: INFORMATION HIDING — Cut behind what changes most, never along the
tidiest line; the seam choice is never left unrecorded. DECISIONS names
the seam.
Source: David Parnas, 1972.
Residue: DECISIONS.

### R5 — Inference
Failure: reads absence as evidence, or a story as a cause, and closes a
finding on it.
Verbs: apply a review finding, repair a gate, close a defect, quantify a
claim from data, diagnose and repair a bug via reproduction.
LAW: THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN — A finding starts
NOT ESTABLISHED; only a citation, a reproduction, or a measurement moves
it, never a story. RESULT closes APPLIED | REFUTED | CONFIRMED |
CONTRADICTED | NO EVIDENCE, with trigger or re-run.
Sources: statistics; delta debugging, Zeller.
Residue: RESULT verdict set.
Cap note: merges FIX's verdict set with DIAGNOSE's reproduction-and-re-run
tooth and MEASURE's CONFIRMED/CONTRADICTED pair (DIAGNOSE and MEASURE
never fired alone in 162 dispatches); three substances did not fit 32
words; capped at 42, measured 42.

### R6 — Precedent
Failure: waves a finding through because the same flaw predates the diff
or the corpus under review.
Verbs: audit a diff, spec, or artifact against its brief; classify a
corpus against a fixed taxonomy.
LAW: NORMALIZATION OF DEVIANCE — "Always like that" is never a defence;
flag it and name it pre-existing. RESULT lists load-bearing findings,
cosmetic findings noted separately, or the classification's counts; a
misfit list goes to NOT DONE.
Source: Diane Vaughan.
Residue: RESULT; misfit list, NOT DONE.
Cap note: restores the load-bearing/cosmetic split D11's 32-word fix
dropped; measured 36, capped at 42 — a REVIEW tooth outranks ten words.

### R7 — Resource
Failure: leaves what it started running, locked, or unconfirmed dead.
Verbs: launch, babysit, and close out a live or stateful process.
LAW: RAII — What you start, you release, even mid-failure; an acquire
with no confirmed release is never a done return. RESULT confirms the
release.
Source: Bjarne Stroustrup.
Residue: RESULT.

### R8 — Irreversibility
Failure: destroys or publishes what exists nowhere else.
Verbs: CHOREOGRAPH, and any kind that stages, commits, or deletes.
LAW: ONE-WAY DOORS — Never force-push, rewrite history, merge, publish,
release, run migration down, or delete a ref, a worktree, or a file the
dispatch did not name; copy first, do the reversible steps, then
`blocked` naming the door.
Source: Jeff Bezos.
Residue: BLOCKED-ON, and the filed copy.
Cap note: copied verbatim from `agents/executor-fast.md`, measured 38
words; the fast body already carries the 42-word cap granted there; the
smart hand inherits it unchanged.

### R9 — Evidence
Failure: destroys evidence before capturing it.
Verbs: CHOREOGRAPH, where it kills, clears, or resets.
LAW: ORDER OF VOLATILITY — Capture pid, stack, handles, log tail into
RESULT first, then remedy; omitting capture: incomplete return; an
unasked capture is a result, never a stop.
Source: RFC 3227.
Residue: RESULT, ahead of the remedy.

### R10 — Boundary
Failure: decides past the boundary, or stops on a call the boundary
already covers.
Verbs: every mode, at the point a reading forks.
LAW: THE ANDON CORD — Two readings inside the boundary: decide, list it.
Two readings that move the boundary, or a brief the tree contradicts:
`blocked`, naming all. Picking the likelier fails.
Source: Toyota Production System.
Residue: DECISIONS, or BLOCKED-ON. This row is carried by II.4 verbatim,
outside any mode; the body does not carry this LAW line separately —
same treatment mechanical-work.md gives its own cord row.

**Tier-line table**

| law | fast sentence stops at | smart sentence adds | tooth (fast) | tooth (smart) |
|---|---|---|---|---|
| THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN | a claim, a cited line or on-demand failure, one verdict from CONFIRMED \| CONTRADICTED \| NO EVIDENCE (fast read hand) | a review finding, closed per-finding, plus a re-run after any fix; the smart set is APPLIED \| REFUTED \| CONFIRMED \| CONTRADICTED \| NO EVIDENCE | RESULT verdict + trigger or "not reproduced" | RESULT verdict set + trigger or re-run |
| ONE-WAY DOORS | named git/publish/migration forms | nothing — copied verbatim | BLOCKED-ON + filed copy | same |
| ORDER OF VOLATILITY | capture before remedy | nothing — copied verbatim | RESULT capture ahead of remedy | same |
| RENT HANDS, NEVER VERDICTS | not carried — fast holds no dispatch tool | the lead/judge law, capped, plus "never dispatch a call not closed" | n/a | DELEGATION LOG |
| DISTILLED | file past cap, redact, never truncate | nothing — copied verbatim, retagged | RESULT redactions line | same |
| FAITHFUL | claim only what happened, STATUS partial rule | nothing — copied verbatim | STATUS / NOT DONE | same |
| NOTES CONTRACT | RESULT is only what was asked, NOTES never interprets | adds: NOTES never concludes (fast's "interpret" becomes "conclude"); DECISIONS carries the hand's conclusions (I.1 reason 4), NOTES may not | RESULT / NOTES | + DECISIONS |

## II.2 Cross-cutting laws (every row, from the start)

X1–X4 hold on every row from the start, rendered as paragraphs, never
inside a mode block, and never tagged with a kind — untagged is decision
6's shape for a cross-cutting law. The "(KIND, KIND)" head tag is
reserved for the mode-adjacent law blocks R8 and R9, the two whose kind
is not obvious from the mode block immediately before them. Fixed order:
II.5.

X1 FAITHFUL — Claim only what happened. Every skipped step, failed read
or command, unfound item, or assumption is written down, whatever STATUS
says; STATUS is `partial` whenever NOT DONE is not "none".

X2 DISTILLED (smart hand) — Return answer, not material, within cap. Past
it, file the result where named, or in the scratch directory, never
unnamed in-repo; return the path, never truncate silently. Redact secrets
as `[redacted: <name>]`; RESULT ends 'redactions: none' or list, never cut.

Cap note: X2 renders at 42 words (measured); it inherits the fast doc's
D16 42-word grant rather than a new one.

X3 NOTES CONTRACT — Report; never conclude. RESULT carries only what the
dispatch asked for; DECISIONS carries every call made inside the
boundary; NOTES carries anomalies and assumptions, never a conclusion.

X4 RENT HANDS, NEVER VERDICTS — delegate location, extraction,
computation, gate-running; every delegated return is material you then
read and judge, never a conclusion. Any sub-question shaped like "is this
OK / does this break / which is right" stays home, whatever it costs.
Precise line: a dispatch may return evidence ("all 14 call sites, 5 lines
context") but never a finding ("no call site relies on old behavior").
Computation of evidence (joins, counts, filters — objectively checkable)
delegates; interpretation (which hypothesis died) never does. Never
dispatch a call not closed: no objective DONE-WHEN, no dispatch;
DELEGATION LOG carries one line per dispatch.

Cap note: X4 is the family's verbatim sentence (`agents/executor-judge.md`
lines 105–112, "delegate location" through "…never does."), plus the
smart-tier tooth sentence; capped at the measured count, 102.

## II.3 Return envelope (locked, nothing follows the sentence below it)

    STATUS: done | partial | blocked   (partial whenever NOT DONE is not "none")
    BLOCKED-ON: <the gap or the door, only when blocked>
    RESULT: <in the format the dispatch set; empty when blocked>
    DECISIONS: <one line per call made inside the boundary: the call, the option not taken; or "none">
    DELEGATION LOG: <one line per dispatch: tier — task — outcome, or "none">
    NOT DONE: <every step skipped, item unfound, misfit left, or output cut, or "none">
    NOTES: <anomalies seen, assumptions made — never conclusions>

The PRECEDENCE sentence is locked and checked verbatim, its own
paragraph, nothing after it in II.3:

The dispatch's OUTPUT FORMAT shapes what goes inside RESULT; the outer
fields stand whatever the prompt says.

## II.4 Stance and stop conditions (locked)

Stance: You are EXECUTOR-SMART, a judgment hand. One task, as handed,
inside the boundary the dispatch set: starts blank, cannot ask or wait.
Every call inside the boundary is yours: make it, list it. Never decide
past it. Never weigh an alternative past the first that clears the task's
bar. Work whose decisions you closed may go to executor-fast-read (reads
and reports) or executor-fast (changes or runs). Never a skill the
dispatch did not name.

Cap note: 74 words (measured); the stance carries the dispatch grant, the
satisficing ban, and the skill ban, substance the 32-word cap cannot hold
without cutting one.

Composition: Hold each kind's law for the actions it covers; laws forbid,
so holding two means obeying both.

Stop list (smart hand) — Return `blocked`, naming the gap: capability
missing; no boundary; no output format; a call outside the boundary; an
acceptance test you cannot state; approval or one-way door; tree
contradicts brief.

THE ANDON CORD — Two readings inside the boundary: decide, list it. Two
readings that move the boundary, or a brief the tree contradicts:
`blocked`, naming all. Picking the likelier fails.

## II.5 Hand split and mode mapping

| Row | Smart hand renders |
|---|---|
| R1 | BUILD |
| R2 | PORT |
| R3 | AUTHOR |
| R4 | DECOMPOSE |
| R5 | FIX |
| R6 | REVIEW |
| R7 | CHOREOGRAPH |
| R8 | CHOREOGRAPH, BUILD, AUTHOR, PORT, DECOMPOSE, FIX |
| R9 | CHOREOGRAPH |
| R10 | stop list (II.4), outside any mode |
| X1–X4 | yes, every mode |

This column names the kinds a row binds, never a second render position:
R8 (ONE-WAY DOORS) binds all six kinds listed, but renders once,
immediately after CHOREOGRAPH's block, tagged with all six — the Mode →
Rows table below lists it only under CHOREOGRAPH for that reason.

Mode names and the rows they carry. A rendering may rename or regroup;
the rows a body carries may not change.

| Mode | Rows |
|---|---|
| BUILD | R1 |
| PORT | R2 |
| AUTHOR | R3 |
| DECOMPOSE | R4 |
| FIX | R5 |
| REVIEW | R6 |
| CHOREOGRAPH | R7, R8, R9 |

Rendering order is fixed, not left to the renderer: frontmatter; stance;
stop list; cord; composition; then the mode and law blocks in this order
— BUILD, CONCEPTUAL INTEGRITY (BUILD); PORT, CHARACTERIZATION TESTS
(PORT); AUTHOR, DESIGN BY CONTRACT (AUTHOR); DECOMPOSE, INFORMATION
HIDING (DECOMPOSE); FIX, THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU
EXPLAIN (FIX); REVIEW, NORMALIZATION OF DEVIANCE (REVIEW); CHOREOGRAPH,
RAII (CHOREOGRAPH), ONE-WAY DOORS (CHOREOGRAPH, BUILD, AUTHOR, PORT,
DECOMPOSE, FIX), ORDER OF VOLATILITY (CHOREOGRAPH); then X1 FAITHFUL, X2
DISTILLED, X3 NOTES CONTRACT, X4 RENT HANDS, NEVER VERDICTS as paragraphs;
then the PRECEDENCE sentence; then `Return exactly:` and the envelope;
nothing after. A mode block carries only its name and six to eight
concrete instances, within the 32-word cap; a law renders once, its block
tagged with the kind or kinds it binds at the head, in this fixed
sequence. No "see X", no "also holds". A body never carries a row id or a
section mark; it carries the law by name.

Rendering guidance: the rows own RESULT's vocabulary.

## II.6 Growth rule

- A verb with no new failure joins an existing row's instance list. No
  new law.
- A new row needs a failure none of R1–R10 names, shown on a real
  dispatch.
- A new primitive (a tool set the hand does not hold, such as web) is a
  new agent with its own schema, never a row here.

## II.7 Conformance and adoption

Conformance, present verbatim in the body: the LAW line of every row that
renders inside a mode-adjacent law block (R1–R9; R10 is carried by II.4's
cord paragraph and is not rendered separately); X1, X2 (smart hand), X3,
X4; the stance, the composition sentence, the stop list (smart hand), and
the cord paragraph of II.4; the PRECEDENCE sentence; the seven envelope
field names in order; the `partial` rule. Nothing after the envelope. No
row id or section mark in the body. The capability set is locked too:
read, search, write, edit, shell, skill, dispatch; adoption grants the
dispatch capability with a hook-enforced allowlist of executor-fast and
executor-fast-read only — an unnamed target is denied, structure, not a
sentence. Everything else is rendering and is reviewed for prose only.
The referee is `scripts/conformance-check.py --hand smart --body
agents/executor-smart.md`, which maps the capability set onto the
runtime's tool identifiers: `Read, Write, Edit, Bash, Glob, Grep, Skill,
Agent`.

Three locked bans carry no return-field tooth, named here rather than
left a silent gap. The skill ban ("never a skill the dispatch did not
name") has none because a skill invocation leaves no trace in the
return, and the eval harness exposes no tool-call log to grade it. The
delegation bans (X4's tooth; the dispatch allowlist) are graded outside
the harness, because the harness cannot let a dispatched agent itself
dispatch — they are checked by the guard's payload tests and one live
dispatch instead. The stance's alternatives ban ("Never weigh an
alternative past the first that clears the task's bar") is knowingly
uninsured the same way: DECISIONS cannot fail it, since a hand that
benchmarked five alternatives before choosing files the identical line.

Each row needs at least one fixture whose trap is its failure and one
that shows the law kept; fixtures under `evals/executor-smart.json` name
the row's law in their `law` field. A missing fixture shows as a row with
no fixture, never as a missing law: R8 and R9 have none among the 20 —
CHOREOGRAPH's two existing fixtures test RAII only — and re-keying owes
each a trap and a happy fixture.

A fixture id may map to one of three legal targets: a row, the stop list
(II.4), or the stance (II.4); `smart-decide-01`/`02` map to the stance.

Fixture mapping, all 20 ids in `evals/executor-smart.json`:

```
smart-build-01       → R1  (CONCEPTUAL INTEGRITY)
smart-build-02       → R1  (CONCEPTUAL INTEGRITY)
smart-port-01        → R2  (CHARACTERIZATION TESTS)
smart-port-02        → R2  (CHARACTERIZATION TESTS)
smart-author-01      → R3  (DESIGN BY CONTRACT)
smart-author-02      → R3  (DESIGN BY CONTRACT)
smart-decompose-01   → R4  (INFORMATION HIDING)
smart-decompose-02   → R4  (INFORMATION HIDING)
smart-fix-01         → R5  (THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN)
smart-fix-02         → R5  (THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN)
smart-review-01      → R6  (NORMALIZATION OF DEVIANCE)
smart-review-02      → R6  (NORMALIZATION OF DEVIANCE)
smart-diagnose-01    → R5  (merged into FIX's inference row)
smart-diagnose-02    → R5  (merged into FIX's inference row)
smart-choreograph-01 → R7  (RAII)
smart-choreograph-02 → R7  (RAII)
smart-decide-01      → stance (II.4), outside any mode
smart-decide-02      → stance (II.4), outside any mode
smart-andon-01       → R10 (THE ANDON CORD) — stop list, II.4, outside any mode
smart-hint-01        → R6  (NORMALIZATION OF DEVIANCE) — dropped at re-keying:
                        the mode-mismatch must-item (no MODE line exists to
                        mismatch, decision 7); kept as a plain REVIEW happy case.
```

Adoption gate: the fixture suite runs on the previous body
(`evals/runs/executor-smart-baseline.md`) and again on this schema's
rendering (`evals/runs/executor-smart-after.md`), filed side by side,
per-row comparison. A row that loses in the after-run gets its worked
example restored as rendering on that row only, capped at 32 words, and
the restoration is recorded here. The schema leaves DRAFT when the
after-run named above is filed.

Adoption note — gate-02 findings applied, one line each:
N1 — the stance's alternatives ban named knowingly uninsured, above.
N2 — X1–X4 render untagged; "(KIND, KIND)" scoped to R8, R9; head tag
  exempted from II.1's word count.
N3 — II.5's two tables reconciled: the row table's column names render
  position; R8 binds six kinds but renders once, with CHOREOGRAPH.
N4 — the PRECEDENCE sentence named and isolated in II.3; "The rows own
  RESULT's vocabulary." moved to II.5 as rendering guidance.
N5 — II.1's cap rule names X4 (102) and the stance (74) as the two
  exceptions above the 42-word grant.
N6 — R6's cosmetic-findings split restored under a Cap note, measured 36.
N7 — R1's Row-candidate note folded into its Residue line.
