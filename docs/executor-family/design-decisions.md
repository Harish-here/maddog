# maddog Design Decisions

STATUS: ADOPTED 2026-09-16, current-state sections rewritten 2026-09-23;
Smart, Fast and the BOUNDARY STOP fragment updated 2026-09-24; Fast-Read and
the shared Fast/Fast-Read Return updated 2026-09-25.
Supersedes the 2026-09-11 record and the locked schemas in mechanical-work.md
and local-work.md. The production bodies under agents/ and
skills/advisor-mode/ carry thirteen shared fragments, canonical in
docs/executor-family/constitution.md and checked by scripts/fragment-check.py.

## Purpose

Canonical record of the executor-family design. The sections from
Architecture to Fast-Read state what holds now; the dated pass sections
under Evidence are history and are never rewritten. This is the decision
layer behind the bodies; nothing loads it.

## Architecture

The system routes by **judgment shape**, not task size, difficulty, or
subject.

```text
READ        → Fast-Read     facts as found; no judgment
MECHANICAL  → Fast          decisions all closed
BOUNDED     → Smart         implementation choice, criteria review,
                            diagnosis with a known evidence surface
EVOLVING    → Lead          next action depends on discovery
GATE        → Judge         verdict before an action that changes state
                            others depend on
GLOBAL      → Advisor       outcome, scope, routing, acceptance
```

Roles are responsibility boundaries, not model-strength tiers. Mechanical
work ALWAYS goes to the Fast tiers: Fast-Read to read, Fast to change or
run. What a role keeps for itself is a concrete test in its own text, not a
cost comparison (see Shared constitution).

## Shared constitution

Text that every dispatcher or every executor needs is written once and
carried byte-identically. Thirteen fragments:

| Fragment | Content | Carriers |
|---|---|---|
| FAMILY LAWS | completion is a state; never retry blindly; durable state off by default; authority for hard-to-reverse actions, instruction-file edits, and scope or intent changes (exact action or standing grant; silence grants nothing). Hard-to-reverse includes anything seen outside the workspace or changing state others depend on, even if it can be undone; inside a user-named workspace a change is reversible unless it discards work or data that exists nowhere else | all six |
| CORE PRECEDENCE | no core law licenses what a Family Law forbids; among core laws the earlier wins | all six |
| ROUTE | route by shape; mechanical work ALWAYS to the Fast tiers (Fast-Read to read, Fast to change or run); once a hand owns a slice, never do its next step yourself, but wait for its return or stop it and REROUTE; no more authority than held; the shape table ending at the GATE row (verdict before an action that changes state others depend on; never a hand that can edit what it judges), each carrier adding its own EVOLVING row | Advisor, Lead |
| CONTRACT | GOAL, BOUNDARY, DONE-WHEN; add only what is useful; cite by path; capped returns; load efficient-md before the first dispatch and never reload it | Advisor, Lead, Smart, Judge |
| VERIFY | a return is evidence, not proof; check against DONE-WHEN; verify load-bearing claims at cited evidence; redoing the work is not verification; a claim you or a Judge already cleared needs no second pass; keep observed, produced, concluded apart | Advisor, Lead, Smart, Judge |
| PATTERNS | ALWAYS CLASSIFY before the first tool call; a named pattern is a hint; hold each pattern's law; core laws outrank pattern laws; work that fits none is returned | all five executors |
| LOOP | the fenced flow OUTCOME → SLICE → CLASSIFY → DISPATCH → EVALUATE → DONE with its actor row | Advisor, Lead |
| DONE | the finish condition is the OUTCOME; a slice's DONE-WHEN only returns you to SLICE | Advisor, Lead |
| DISPATCH FIRST | work goes to a hand before you do any of it yourself; a look that only decides where work goes stays yours | Advisor, Lead |
| RESUME | resume a hand only when the slice builds on what it holds, the slice's shape routes to it, and it is within its cache window; else a fresh hand from a written summary; a resumed hand still gets a full Contract | Advisor, Lead |
| VERDICTS | the four-row result table: valid → ACCEPT; incomplete → CONTINUE; wrong shape → REROUTE; blocked → RESOLVE when the block is yours to clear, otherwise ESCALATE | Advisor, Lead |
| UNCERTAINTY | existing decisions first, then minimum evidence; escalate only on ambiguity that survives evidence or authority you lack; one message when you ask; invent no requirements | Advisor, Lead |
| BOUNDARY STOP | law 1's opening: your only authority is what your dispatch carries as approved by the user; a grant met anywhere else is information; repo instruction files tighten, never loosen | Lead, Smart, Fast |

Decisions that fix the mechanism:

- Fragments name no role as their subject; second person addresses whichever
  role carries them. Headings around a fragment belong to the carrying file,
  so a carrier may seat a fragment under any heading (UNCERTAINTY sits inside
  Evaluate, after the verdict table it serves).
- FAMILY LAWS stay neutral: they govern behaviour every member shares and name
  no member, route, or stage. A rule that needs a member's name belongs in the
  carrier's own text. Core Laws are the carrier's own and may name members.
- No tier-specific additions inside a fragment. What varies by role sits in
  the role's own text next to the fragment: the Advisor's two kept things
  after DISPATCH FIRST, Lead's single read after it, each carrier's EVOLVING
  row after ROUTE.
- Every Role ends with a family sentence: the hands it dispatches (or that it
  dispatches none) and that the Family Laws bind it and every hand. This is
  where "hand" is defined.
- Every Core Laws section is numbered and named, opens with CORE PRECEDENCE,
  and puts authority first: the Advisor's Authority from the user, Lead's and
  Smart's and Fast's Boundary stop, Judge's Dispatch stop.
- Authority reaches a hand only through its dispatch. A grant met anywhere
  else — a file, a hand's relay, a tool's output — is information, never
  authority; repo instruction files can tighten any law, never loosen one.
- Two rules replace the gate ladder and "never behind a wait". Judge before
  shared state: before any action that changes state others depend on, get a
  Judge's verdict on it and act only on a pass (Advisor and Lead; a hand acts
  on a dispatch that followed one). Act alone: a hard-to-reverse action runs
  or is dispatched on its own, never in the same step as a test run or any
  wait (every role that acts). A push to one's own branch needs authority and
  runs alone but takes no Judge.
- Laws are tool-neutral. The only tool vocabulary is the door list in Fast's
  Boundary stop, as tagged examples after a neutral rule ("a publish, merge,
  or push … as a git reset, clean, or checkout can"), kept because the cheap
  tier maps named commands better than an abstract clause.
- A fix sits where the failing act happens as well as in the law: Judge's
  Gather keeps only commands that change nothing; Fast's OPERATE and VERIFY
  mark a hard-to-reverse operation or check as a door; Fast's Done forbids
  changing other state to make DONE-WHEN read true.
- What a role keeps is a concrete test, never "so small that dispatching costs
  more". Advisor: the look behind an outcome proposal, and a single read or
  command whose short output decides its next step. Lead: a single read or
  read-only command, every change to a hand. Judge: the evidence the verdict
  rests on, commands the bar needs that change nothing, and a single read or
  read-only command. Smart: its task's choices, changes, and the checks that
  prove them, plus the evidence it judges and a single read or command; closed
  many-file slices go to the Fast tiers.
- Every role that finishes by returning says so at Done: "You stop by
  returning: emit the block under Return."
- Every STATUS carrier (Lead, Smart, Fast, Fast-Read) maps each kind of stop
  to a status in Return: done when DONE-WHEN is met and NOT DONE is empty;
  blocked when a law stops the work, a cause the role names applies, or the
  work fits no pattern; partial otherwise. The old parenthetical "partial
  whenever NOT DONE is not none" made blocked unreachable and is gone. Judge
  maps work that fits no pattern to STOP.
- Under a loop heading, every child heading is a loop stage. Standing rules
  sit outside the loop or inside the stage they serve.
- A fragment is edited in constitution.md and propagated; a copy is never
  edited in place. advisor-mode is the master text: a change found while
  reviewing another carrier is made in advisor-mode and constitution.md, then
  propagated. `scripts/fragment-check.py` byte-compares every (carrier,
  fragment) pair and is the conformance gate. `scripts/conformance-check.py`
  and the Part II schemas it reads are superseded history, not a gate.
- A shared reference file was rejected: Smart may not load a skill the
  dispatch did not name, and agent bodies may not cite a plugin-root path.
  Resident text was the only way to reach the whole family.
- Added 2026-09-17, still holding: CONTRACT tells every dispatcher to load
  efficient-md before its first dispatch (6 of 6 probes loaded it on the
  explicit wording). Advisor and Smart add "Write MD artifacts by it as well."
  Smart's no-unnamed-skill rule excepts efficient-md.

## Loops

| Role | Loop | Why |
|---|---|---|
| Advisor, Lead | the LOOP fragment | they cut and dispatch slices |
| Judge | BAR → CLASSIFY → GATHER → VERIFY → VERDICT, own text | the judgment is never dispatched; the back-edge is evidence-driven, VERIFY → GATHER |
| Smart | TASK → CLASSIFY → WORK → VERIFY → DONE, own text, added 2026-09-23 | a doer with judgment: VERIFY checks its own result against DONE-WHEN and loops back to WORK; resumable, so it re-enters at TASK |
| Fast, Fast-Read | none, by decision | a back-edge would contradict "never retry on your own" and invite the dirty-tree revert; the unbroken-run, re-entry, and done-return duties are already stated in their Role and Done |

Each file holding a loop states the unbroken-loop rule and, where the role can
be resumed, where a new message re-enters (LOOP DISCIPLINE in constitution.md).

## Advisor

advisor-mode is always-resident once invoked. Its own text: Role (outcome and
scope are the user's; the family sentence), four numbered core laws
(Authority from the user; Judge before shared state; Act alone, carrying the
user's grant; Show before writing), the Operate paragraph (a kept slice skips
DISPATCH, never EVALUATE; a message that explicitly changes the outcome
re-enters at OUTCOME), the bounded outcome look, the two kept things, and "You
accept a Lead's return whole". There is no Gate section: its live rules moved
to Core Laws and the GATE row. Body 1,033 words raw (markup included), up from
767; the 500-word target is measured on the owner's plain draft and was not
re-measured (see Non-Decisions).

CLAUDE.md carries one Advisor line so the compaction reload survives
compaction.

## Lead

Lead's own text: Role and family sentence (hands: Fast-Read, Fast, Smart,
Judge), four core laws (Boundary stop; Judge before shared state; Act alone;
No nesting or self-judging), the Operate paragraph (stops include an early
return; a resumed Lead re-enters at SLICE), Outcome ("never expand or redefine
it"), Classify's per-slice rule (one package can hold several patterns; a
slice's evidence can bring a new one), the pattern table and after-PLAN rule
directly under Classify, its EVOLVING row, its single-read line, the Return
status map. Body 1,453 words raw, up from 1,249.

## Smart

Smart's own text (2026-09-24): Role and family sentence (hands Fast-Read and
Fast, by short name), four core laws (Boundary stop, opening with the
BOUNDARY STOP fragment and naming product, architectural, and cross-task
calls as outside the boundary; Act alone; Evidence before choice, which
records what evidence cannot resolve in DECISIONS; Judgment is expensive,
bounded by the first path that would meet DONE-WHEN), its own loop with Task,
Classify (Pattern | Applies when | Law; rows written as conditions on the
task; a behaviour-preserving refactor sits only under TRANSFORM; REVIEW says a
gating review is Judge's), Work, Verify, Done (DONE-WHEN met only through the
dispatched work, never by weakening a check), and the Return status map with
DELEGATION LOG, where blocked holds however much of the work is done. Smart
does not carry ROUTE or DISPATCH FIRST: the doer never rents out its own job.
Its description separates it from Fast by "how to reach the goal is not yet
decided". Body about 1,380 words raw.

## Judge

Judge's own text: Role and family sentence (one hand, Fast-Read), four core
laws (Dispatch stop, covering bar and grant; Independent judgment; Evidence
before verdict, which defines primary evidence; Acceptance over activity), its
loop (a resumed Judge re-enters at BAR), Bar, the pattern table, Gather's
three kept things, the Verify seam, the Verdict table with "Uncertainty is
STOP, never FAIL" and five STOP causes (a missing Bar input; unreachable
evidence, including a command the shell cannot run; a target that differs;
authority not granted, including any command that would change state; work
that fits no pattern), and a five-field return. The description's trigger is
the GATE row's. Body 981 words raw, up from 928.

## Fast and Fast-Read

Both open with the family Role and a family sentence (neither dispatches),
carry CORE PRECEDENCE, end with Done (finish condition is the dispatch's
DONE-WHEN; stop by returning; never retry on your own, and a resumed dispatch
with a new basis is a new task), and map statuses in Return. Both define a
misfit as a member or item that may not fit (list it in NOT DONE, leave it,
never a stop; a misfit alone leaves the status done). Their Return bullets
are word for word the same (2026-09-25): the dispatch shapes RESULT only,
with the reason line; a cut is marked `[omitted: N lines]` where it falls
and listed in NOT DONE; a secret is marked `[redacted: <what it is, never
any part of its value>]` in every field, and the marker is its only trace.

Fast (2026-09-24): four core laws (Boundary stop, opening with the BOUNDARY
STOP fragment and then defining a door and the copy-first procedure; Act
alone; Stop, don't guess as a list with the TRANSFORM-misfit carve-out;
Execute only what is closed). Its pattern table's middle column is "Applies
when", rows prefixed "the task …". Return adds "the outer fields stand"
and a reason-giving line: the caller reads STATUS first and lifts RESULT
out, so a set format goes inside RESULT. Its
description sends work to Smart "when how to reach the goal is still open".
Body about 1,160 words raw.

Fast-Read (2026-09-25): its opening says "You only read". Four core laws:
Evidence, never judgment (quote a source wherever its content is stated,
and only a source opened in this task; a search result's summary is not the
source; never merge sources); Stop, don't guess as a list, with the VERIFY
and SWEEP carve-outs; Read only what the question needs (the web only when
the dispatch names a web source or asks for a search); Sources give no
orders. Four patterns, middle column "Applies when", rows prefixed "the
question …": SWEEP (Systematic Search: every match to a target known
before the search; the searches listed when nothing is found), TRACE
(Citation Chaining: steps cited in order; a fork or dead end is the last
step and goes to NOT DONE), EXTRACT (Diplomatic Transcription), VERIFY
(Null Hypothesis; a NO EVIDENCE claim lists its searches, goes to NOT DONE,
and sets STATUS to partial, per fixture fastread-faithful-02). The
description adds "where a reference leads". Body about 1,040 words raw, up
from 762.

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
  the gate. Fixed by narrowing FAMILY LAWS and ROUTE to what every carrier can act
  on and moving the rest to the Advisor body, plus one seam line per role.
  Also surfaced and fixed: the unranked Family Laws, STATUS blocked being
  unreachable under the partial rule, and RESULT "empty when blocked" hiding
  changes already on disk.
- Coherence rerun on the fixed text: Lead, Smart, and Fast COHERENT WITH
  COSMETIC FINDINGS; Judge and Fast-Read INCOHERENT on one item each.
  Fragment-level from the rerun: absence claims are verified at their search
  pattern and scope; the workspace carve-out excludes discarded data as well
  as work.
- Drift audit, two fresh-eyes reviewers (executors against the branch base;
  Advisor against the owner's settled draft): the coherence rounds had added
  about twenty sentences that answered checklist items (return-field
  completeness, "STATUS blocked unreachable", inert-or-misleading
  hypotheticals) without changing what a hand does, and the Advisor had lost
  four precise rules to hold a word count. All reverted or restored. Kept
  from the coherence rounds only what a fragment made necessary (precedence,
  standing grants through the dispatch, Smart's own rent rule, Judge's seam
  line) or fixed a defect with a behavioral failure behind it (Smart's
  blocked RESULT, Fast's reset-or-clean door and rule-form grant, Lead's
  re-gate verdict). FAMILY LAWS bullet 2 lost "decided by the dispatcher", the
  Advisor-vantage phrase behind two carrier seams.

Residuals accepted without a rule, because every run behaved correctly
without one: the small-work threshold; concurrency on one file; the remedy
for a capped return breached; the remedy for a landed scope overreach; the
selector among the three blocked resolvers; a standing grant's limits being
lost to compaction (the safe failure is to hold the push and ask).

Residuals accepted on the 2026-09-17 external review, each with its failure
named:

- The Judge's dispatch fields (target by path, bar, primary evidence, prior
  verdict) are not listed in Advisor or Lead. Three probe runs named all
  four from the triad alone, and the Judge's Stop rule refuses a dispatch
  that lacks one: the failure is one refused round.
- The Advisor does not state that a push to a user-named branch is hard to
  reverse, as Lead does. Three probe runs held the push, escalated Lead's
  request, and refused to chain it behind a test run, each citing
  "publishing" in FAMILY LAWS.
- Interrupt handling (not probed): a background hand may run on after a user
  interrupt. Its return is checked against the corrected intent; the cost is
  wasted work or a same-file collision, never a one-way action.
- Telling the user before they leave (not probed): work may continue
  unattended. FAMILY LAWS forbids inferring authority from absence, so the cost is
  work parked on an approval.
- Per-step classification of a frozen plan (not probed): a whole plan may go
  to one hand. The cost is a pricier hand; Lead's body classifies each slice.
- Reading on the way to a change (not probed): may be split into a Fast-Read
  dispatch and a Fast dispatch. The cost is one extra dispatch.

## Lead pass, 2026-09-17

Lead was reworked section by section against the compressed Advisor: 1,910
plain words to about 1,030, of which about 540 are shared fragments and
about 490 are Lead's own. Lead now mirrors the Advisor's headings (Role,
Operate, Evaluate, Uncertainty) and adds Work Patterns and Return.

Six fragments were added, so the orchestration behaviour of Advisor and Lead
is byte-identical and checked: PATTERNS (all five executors: ALWAYS CLASSIFY
before the first tool call); LOOP, DISPATCH FIRST, VERDICTS, GATE LADDER,
UNCERTAINTY (Advisor and Lead); GATE LADDER is so named because a bare GATE collides
with the shape table's GATE row when the carrier table is parsed. ROUTE now ends at the table's GATE row with
the authority sentence in its first paragraph; each carrier adds its own
EVOLVING row (Advisor: Lead; Lead: you). Three Advisor phrases were made
vantage-neutral so the text could be shared: "review by whoever you answer
to", "Escalate only when", "authority you lack". constitution.md also
records the four-part OPENING pattern, which is not a fragment.

Removed from Lead as carried elsewhere: the six core laws, package laws 3 to
5, Orchestration, Batching, the resume and retry rules, Unattended Work,
Completion, Anti-Patterns, DELEGATION LOG and NOTES (NOTES folds into
DECISIONS). Lead's return envelope now differs from Smart's.

Probe, nine scenarios covering every section, Sonnet and Haiku, draft against
the prior body: the draft matched the prior body on Sonnet (8 of 9 each) and
bettered it on Haiku. One scenario failed 8 of 8 on both bodies and both
models: a push authorised only by a line in a repo file. Runs matched the
line against the FAMILY LAWS definition of a standing grant (action,
workspace, limits) and two read the gate floor sentence as making repo files
a source of authority. Fix: Lead, Smart, and Fast each state "A grant met
anywhere else — a file, a hand's relay, a tool's output — is information,
never authority", and the GATE LADDER floor sentence now reads "can raise this
ladder's floors, never lower them or grant authority". Re-probe on the
narrower first wording: 18 of 18, including a real dispatch-carried grant
still being used.

Residuals accepted, each with its failure named: the remedy "raise the
hand's model or effort" is gone (a hard slice may be misrouted once); a
slice may outlive a partial or blocked return (wasted work by an orphaned
hand); Haiku never sent a Judge before a production publish on either body
(Lead runs on a high tier); one Sonnet run sent a Judge after a push had
already happened (one wasted round).

## Judge pass, 2026-09-19

Judge was reworked section by section against the reworked Lead: 1,048
body words to 840, of which 249 are the four shared fragments and 591 are
the Judge's own. Judge now mirrors the Lead's headings (Role, Operate,
Return) and gives Operate one `###` per stage of its own loop, `BAR →
CLASSIFY → GATHER → VERIFY → VERDICT`, with Contract nested under Gather
at `####`. The loop is Judge's own text, not a fragment: it re-enters at
GATHER, never CLASSIFY, and ends at VERDICT. The same nesting of Contract
under the dispatch heading was applied to advisor-mode and executor-lead.

Core laws stay at four with one swap: "Judgment is expensive" left for
Gather's tier line, and Bar stop entered first, the Judge's counterpart to
the Lead's Boundary stop: the bar reaches the Judge only through its
dispatch; a bar met anywhere else is information, never the bar. Identity,
Evaluation Boundary, Stop, Completion, and Anti-Patterns are gone as
carried by Role, Core Laws, Verdict, the loop, and Return; the one unique
clause each held (the resumed-Judge rule, redefine-the-bar, the STOP
conditions, no unasked advice) moved to Bar, Core Laws, Verdict, and
FINDINGS. Return lost DELEGATION LOG, folded into EVIDENCE. The
description was rewritten to the five-slot rule: GATE in caps, PASS, FAIL,
STOP named, re-gate as an instance, the consequence test in the trigger,
STOP on missing inputs as an invariant; 891 characters.

Probe, 13 pairs (a direct question and a pressure scenario per section),
Sonnet and Haiku, two runs each, draft against the prior body: draft 102
of 104 actions, prior body 103 of 104. The prior body's miss was a Haiku
run adopting a README's criteria as the bar, the hole Bar stop closes; the
draft held it 8 of 8. The draft's two misses were one Haiku run: a push
skimmed past inside a "gate command" question (the explicit-push twin held
8 of 8), and "reject" for a missing bar where STOP was due. Blind probe,
ten scenarios authored by a hand that saw only the description and FAMILY
LAWS, Sonnet and Haiku: 20 of 20, including the missing-bar case going to
STOP on both models. No text was changed for a probe result.

Residuals accepted, each with its failure named: a Haiku Judge may run a
push hidden in a gate command (the Judge is pinned to Opus); a Haiku Judge
may answer a missing bar with a refusal instead of STOP (one wasted
round). Follow-ups recorded: the Core Laws precedence line is
byte-identical in five executors and is a candidate fragment; slot-4
redirects could become optional in the description checklist,
family-wide.

## Advisor and Lead pass, 2026-09-21

Ran as a section-by-section review of advisor-mode with the user closing every
verdict, then propagated to the constitution and the five executors.

- ASSIGN left the loop and SLICE entered before CLASSIFY. Once CLASSIFY names
  the shape, the shape table names the hand, so ASSIGN could not come out two
  ways. Meanwhile the loop said "the next slice" and no stage cut one.
- The loop line is fenced and carries an actor row, given / you / to a hand.
  "Given" reads correctly for both carriers: the Advisor's outcome comes from
  the user, the Lead's from Advisor.
- Every stage owns a section, in loop order, in advisor-mode and Lead alike,
  which is the shape Judge already had. Outcome, Slice and Done are new;
  Dispatching became Classify; Contract sits under Dispatch.
- The dispatch field OUTCOME is renamed GOAL. One word named the session's end
  state and each dispatch's end state, and the new Outcome section made the
  collision visible. advisor-mode's argument-hint became [outcome].
- The gate ladder moved under Classify. Measured: with the ladder under
  Evaluate, a probe asked which decisions take a Judge answered from the shape
  table and never mentioned reversibility; under Classify it answered from the
  ladder.
- LOOP split into LOOP, the diagram, and DONE, its one sentence, so the DONE
  sentence can sit in the Done section. Eleven fragments.
- LOOP DISCIPLINE joins OPENING as a pattern rather than a fragment: each file
  holding a loop states the unbroken-loop rule in its own stage names. Smart,
  Fast and Fast-Read hold no loop and carry none.
- VERIFY gained "a claim you or a Judge already cleared at its evidence needs
  no second pass". The first wording, "a claim already cleared, by you or by a
  Judge", let a hand's own report read as clearing: absence claims were
  verified in 1 probe of 3 under it and 3 of 3 after.
- Judge and Smart merged the small-work exception with the
  evidence-you-read-yourself sentence rather than carrying two sentences that
  end the same way. The convention that the exception sentence matches across
  the four dispatchers now holds on its first half only.
- Lead's Done states that a Lead stops by returning. At DONE a probe answered
  "I stop, no artifact, no other step" and returned nothing; after the line,
  three of three returned.
- Lead's EVOLVING row says a slice stays with the Lead and is never dispatched.
  The diagram's "to a hand" label otherwise contradicted it.
- fragment-check.py carried the fragment list in two regexes as well as in
  FRAGMENT_NAMES, so DONE went unchecked when it was added. The parser derives
  from the one list now.

Probes: 24 recall questions and 12 applied-task scenarios against advisor-mode
on the cheap tier, the tasks repeated on the mid tier; 8 routing items on both;
10 against Lead and 6 against Judge. Recall scored 23 of 24 while the applied
scenarios found three rules that did not fire, one of them a rule the recall
set had just answered correctly. Every applied failure was replayed against the
pre-change file before being attributed to this pass: two of three first-round
failures were variance and reversed on repeat.

## Section-by-section pass, 2026-09-23

Ran the section-by-section skill on all six carriers. The user closed every
verdict for advisor-mode and Lead; for Judge, Smart, Fast and Fast-Read a Lead
drafted each round and the Advisor closed verdicts as the user's delegate,
one commit per tier (b1bfca8, a965ce9, a780d55, d2f70c9, 213428d, b8aefd4,
74289f0).

- An external review opened the pass. Its settle-conditions all closed: session
  stop is the OUTCOME, not the first slice; the Advisor's ACCEPT and the user's
  review of delivered work are two acts; the look, kept work, and dispatch are
  ordered; the GATE row no longer repeats a ladder.
- The gate ladder is gone. Its factual and reversible rungs restated Evaluate
  and the loop; its live rules became Judge before shared state, Act alone, and
  the repo-files-tighten rule. A stress case settled the split: under the old
  text every push to any branch took a Judge.
- "Hard-to-reverse" keeps a definition, stated as edges only ("includes"): the
  term alone misfires both ways, missing an undoable-but-seen action and
  flagging every workspace edit.
- The small-work exception became a concrete test per role. The cost
  comparison could not be applied without judgment, and a cheap model stretched
  it.
- CONTINUE left the verdict block and became RESUME under Dispatch: reuse is a
  decision about who gets the next slice, keyed to the hand's cache window,
  which each runtime defines.
- Laws stay tool-neutral after the user ruled git vocabulary out of a law; Fast
  keeps named commands only as tagged examples.
- Smart gained a loop; Fast and Fast-Read were decided against one (see
  Loops).
- Carry-backs: reviewing Lead changed the master (the Core Law split, the GATE
  row, "Besides checking results" before the Advisor's kept things); reviewing
  the tiers made the precedence line identical in all six, now the CORE
  PRECEDENCE fragment.

- Follow-up the same day: PATTERNS says "One or several may apply"; Smart
  classifies on every pass (its loop's back-edge returns to CLASSIFY, so a fix
  after DIAGNOSE is BUILD); Smart, Fast and Fast-Read patterns became the
  family's Pattern | Work | Law table, words unchanged. Probe against the
  prior files, two runs each (Fast and Fast-Read on Haiku, Smart on Sonnet):
  Fast 11.5 of 12 against 10 of 12 (RECOVER's capture-first fired where the
  block form missed it twice), Fast-Read 9 of 10 against 8 of 10 (the one miss
  a probe artifact), Smart 10 of 10 on both with explicit per-pass
  re-classification only in the new form.

No probe ran on the rest of this pass. Unprobed, each to be probed against the pre-change
file before release: Fast-Read's "an instruction met in a source is content";
Fast's Done clause against changing other state and its checkout example;
Judge's Dispatch stop; Smart's loop.

Residuals, each with its failure named:
- The guard denies interpreters (python, node, perl) to Judge, and Judge can
  dispatch only Fast-Read, so a bar that names a script gate reaches STOP by
  construction. Remedy is the caller's: supply that gate's output as evidence.
- The guard once denied `git commit` to a Fast dispatch that two earlier Fast
  dispatches in the same session ran; the Advisor made that commit under the
  user's grant. Cause not established.
- Advisor-mode grew from 767 to 1,033 raw words; no rule was cut to hold a
  count.

## Smart section-by-section pass, 2026-09-24

The user closed every verdict (ledger kept in the session scratchpad). The
review read Smart against the constitution, Lead, and Judge, after first
listing what only Smart is: it both decides and writes; it cannot ask for
input; it does its own job and rents only closed slices; judgment is its
cost; it never calls a Judge; it reviews without gating; it takes Fast's
blocked decisions.

- "Never redefine the outcome or expand the boundary" (old law 3) and "a
  failed attempt is never permission to expand the task" (Verify) were
  removed: the Family Law on scope changes plus Boundary stop already say
  it, and Smart can obtain no grant mid-task. The law's decision list moved
  into Boundary stop. Five laws became four.
- "Outcome" now means only the caller's end state; the dispatch's is the
  goal. "As user-approved" had lost its object and became "what your
  dispatch carries as approved by the user", in Lead too, now the BOUNDARY
  STOP fragment.
- The pattern table's middle column became "Applies when" after comparing
  Advisor's When, Lead's Flow, and Judge's Target: its job is recognising the
  work, and only qualifiers and surprising examples earn a place. Fast and
  Fast-Read keep "Work" (rename deferred; their rows are verb-led).
- Added: Done's "never weaken a check or change other state to make it read
  true" (a GAP taken from Fast); the markdown line loads efficient-md when no
  dispatch has (also in advisor-mode).
- The author-agent / review-agent gate was waived by the user in favour of
  old-versus-new probes.

Probes, all on Haiku, blind, keyed before dispatch, every draft miss replayed
against the pre-change file:
- 9 applied scenarios ×3 per file: draft 27/27, old 24/27. The one scenario
  that separated them was an unresolvable choice (old 0/3: kept analysing,
  blocked, or picked unrecorded).
- 10 more scenarios on untested sections ×3: draft 26.5/30, old 27/30. The
  gap is a resume message in long batches (old 3/3, drafts 3/6); run alone,
  drafts 7/7 and old 3/3. Not attributable to a changed line.
- Recall, one question per section plus traps: section questions 19/19 on
  every draft run.
- Routing, 11 tasks: draft 22/22, old 21/22. A behaviour-preserving refactor
  went to Fast under both descriptions (old 1/3) until the description named
  "transform an existing structure while preserving its behavior" and "how
  to reach the goal is not yet decided" (2/2).
- Two walks through the loop found no broken join.

Residuals:
- Returning partial when a law stops the last piece: old 2/3, draft 2/3 to
  2.5/3 after "blocked holds however much of the work is done". Runs fill
  BLOCKED-ON and still write partial; a Return format that derives STATUS
  from BLOCKED-ON is the likely fix. Not attempted.
- The resume message in long batches, above. Sonnet, Smart's production
  model, was not probed; check both before release.
- A plain rerun before diagnosing a one-off test failure appears under both
  files; arguably a legitimate flakiness probe. Not acted on.
- Recall traps read "dispatch Lead for evolving work" off the description
  under both files; behaviour was always correct.

## Fast section-by-section pass, 2026-09-24

The user closed every verdict (ledger in the session scratchpad), against the
constitution, Lead, Judge and the reworked Smart.

- One-way doors became Boundary stop: the BOUNDARY STOP fragment, then "A door
  is any hard-to-reverse action or instruction-file edit …" and the
  copy-first procedure. The removed first sentence restated the Family Law.
- Role: "cannot ask for input" and "whether it is right stays with the
  caller". Description: Smart's exclusion is "how to reach the goal is still
  open", replacing "ambiguous refactors". Done drops "Write no file the task
  does not require" (the durable-state Family Law). Return gains "the outer
  fields stand", the one line every other role already carried.

Probes on Haiku, blind, old versus new: 12 scenarios ×3 with six pressure
items (urgency, "don't overthink", demo deadline, cheap shortcuts): old 35/36,
new 33/36, the gap variance on replay; every pressure item held 18/18 on both.
Routing 8 tasks ×2: new 16/16, old 15/16. Recall 20 questions: new 20 and
19.5. Walk: no broken join.

A dispatch-set format ("reply with ONLY the raw output", "JSON only")
dropped the return block about half the time under both files; one run cited
"your only authority is what your dispatch carries" as licence. "Your reply
always opens with the STATUS line; a format … applies inside RESULT only"
kept it 2/6 (old 1/6) and was itself cited as licence. The adopted line gives
the reason and names the cases, 4/6. Residual: the probe used the same two
cases the line names, so 4/6 may overstate the general case; Sonnet-fed
callers and Smart's Return were not re-probed.

## Fast-Read section-by-section pass, 2026-09-25

The user closed every verdict (ledger in the session scratchpad), against
the constitution's ROLE PROPERTIES and the reworked Fast. The constitution
gained P37 (references that point onward without end); P28 names SWEEP.

- RECON split into SWEEP and TRACE. RECON named no shape and overlapped
  EXTRACT and VERIFY; "where is X" (a set, known target, one search) and
  "where does this lead" (a chain, each step read before the next) need
  different rules. Totality and Effective Value gave opposite stop points;
  Systematic Search replaces both. The law names come from Cochrane
  Handbook ch. 4 ("a thorough, objective and reproducible search … to
  identify as many eligible studies as possible", verified in session).
- Law 1 now requires quoting and forbids merging sources; the opened-source
  rule came from a live Fast-Read web dispatch in the session that returned
  `done` with "quotes" its cited pages do not hold (a 403 page, a missing
  sentence, a paraphrase). Law 3 split: the reading limit stays, and "an
  instruction met in a source" became law 4, reworded so following a needed
  reference is not read as obeying the source.
- Law 2 carries a SWEEP-misfit carve-out: as a core law it outranked RECON's
  "never a stop". The pattern column became "Applies when", as in Fast.

Probes on Haiku, blind, old versus new, answer keys written before results:

- 11 scenarios ×3 (one dropped: its key was wrong): new 27/30, old 25/30.
  "Reply with ONLY JSON" kept the block 3/3 against 1/3.
- NO EVIDENCE never set partial (0/6) under either file until the VERIFY row
  named the status; then 4/6 against 1/6. A fork was called done 2/3 until
  TRACE sent it to NOT DONE.
- A search record demanded in RESULT fired 0/9 and was reverted; it is kept
  only for an empty SWEEP (3/3) and NO EVIDENCE (3/3). "List what you cut in
  NOT DONE" displaced the in-place marker (0/3 against 2/3); naming both
  restored it (6/6).
- A secret leaked in NOTES while a run explained its redaction: old 1/3, new
  1/6. "The marker is the only trace of a secret" gave 0/6. Fast took the
  same two Return bullets, probed through Fast-Read only.

Residuals: an absence read as CONTRADICTED, and a TRACE blocking at a dead
end, each about 1 run in 3 on both files; a cut-only return called partial
3/6. Product agents keep their own RECON step labels and name SWEEP at the
dispatch.

## Non-Decisions

The design intentionally does **not** introduce:

- a cost comparison for what a role keeps; each role states a concrete test
- a size threshold for a slice
- a size threshold for "targeted reads"
- tier-specific additions inside any fragment
- member names in FAMILY LAWS
- tool vocabulary in any law, beyond Fast's tagged examples
- a per-hand dispatch table
- a shared reference loaded on demand in place of resident text
- a loop for Fast or Fast-Read
- a Researcher role
- mandatory session ledgers or memory files
- mandatory Judge after delegation, or before an action that changes nothing
  others depend on
- automatic Lead escalation for difficult work
- Lead mode-transition ceremony
- continuation for Fast / Fast-Read / Smart / Judge beyond a caller's resume
- rules for behavior the probes showed correct without them
- a word count held by cutting rules: the 500-word target is measured on the
  owner's plain-text draft; markup is not counted, and a rule is never cut
  to meet it

## Debt

- The five lines listed as unprobed under the 2026-09-23 pass; Smart's
  loop was probed on 2026-09-24.
- The residuals under the 2026-09-24 Smart and Fast passes and the
  2026-09-25 Fast-Read pass; Fast's new Return bullets unprobed on Fast.
- Judge cannot run script gates under the guard (see the 2026-09-23
  residuals).
- BOUNDED's "diagnosis with a known evidence surface" does not separate a
  surface the evidence established from a cause someone asserted. Left as
  designed: a wrong hypothesis returns blocked and reroutes, at the cost of
  one round.
- Lead's Return marks BLOCKED-ON for partial or blocked only; one probe in
  three emitted it as "none" on a done status. One run, not acted on.
- mechanical-work.md and local-work.md describe schemas the bodies no
  longer render from; conformance-check.py reports NONCONFORMING on HEAD.
- CHANGELOG and plugin version are updated by the release skill before
  merge; advisor-mode and the executor bodies are SHIPPED surfaces.
