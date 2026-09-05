# Mechanical work — why executor-fast and executor-fast-read are built this way

STATUS: DRAFT. Adoption is gated on the fixture run named in II.7.

This document is for someone meeting the cheap tier for the first time: a
reader who knows Claude Code and agents, and wants to understand, review, or
re-author `agents/executor-fast.md` and `agents/executor-fast-read.md`. Part I
explains why the two hands exist and why their instruction files look the way
they do. Part II is the locked schema those files are rendered from. Beliefs
this design serves: `PHILOSOPHY.md`.

---

# Part I — The reasoning

## I.1 What the cheap hand is for

A coding session is run by an expensive mind: the advisor, a top-tier model
holding the user's goals, the architecture, and every open decision. Most of
what a session actually does is not that. It is applying a decided edit, running
the tests, renaming a symbol in fifty files, quoting a config block, checking
whether a claim about the code is true. The cheap hand exists so the expensive
mind never does that work. Four reasons, in the order they mattered.

1. **It makes the bottom price exist.** "Intelligence is a budget" only works
   if there is a cheapest hand to buy. Without it, every delegation starts at
   the mid tier. A hard subject does not buy a smart model; an open decision
   does. A decided edit across fifty files is hard to look at and trivial to
   decide. The cheap hand is where that distinction becomes a price.
2. **It protects the advisor's context, which is the scarce thing.** Mechanical
   work done in the main thread costs twice: once to do it, then forever after
   as raw material sitting in the context window. A fresh-context hand does the
   work and returns a distilled result. The return envelope and the rule that
   NOTES carries no conclusions exist so the advisor's context stays reserved
   for judgment.
3. **It is a check on the advisor's own discipline.** The dispatch contract
   demands closed decisions and an objective acceptance test. When the hand
   hits a decision nobody made, it returns `blocked`. That return is a signal
   about the caller, not the hand: the advisor finds out it had not finished
   thinking. A judgment call cannot slide into a cheap dispatch and get
   silently resolved. This makes the line between deciding and executing
   testable.
4. **It gets safety from weakness, not from smartness.** At the mechanical
   layer a smart model's helpfulness is a liability. It improvises, and a
   plausible-but-wrong result is the most expensive failure because it survives
   review. Every law in Part II is a prohibition against improvising. The hand
   is built to be dumb and reliable. The advisor is the brain.

The consequence for the instruction file is the sentence that governs
everything below: **every line exists to stop the hand from thinking, never to
help it think better.** A sentence that asks the hand to weigh, estimate, or
prefer is a defect, however reasonable it sounds.

## I.2 Why two hands

`executor-fast-read` was not created to make the mode list shorter. It was
created to close a hole in an invariant. The adversarial hand, `executor-judge`,
must be structurally unable to fix anything: it holds no write and no edit
capability. But it could dispatch `executor-fast`, which holds both, and so a
judge that cannot fix could still hand a fix to a subordinate that writes. The
read hand holds no shell and no write, the judge's dispatch allowlist names only
it and the researcher, and a guard hook enforces the allowlist. The lead and the
product agents had their evidence-gathering retargeted for the same reason. The
write hand losing three modes was a side effect.

The rule that falls out: a new agent is justified when some caller must be
structurally unable to do something and only a tool set can enforce that. Mode
count is never the reason. This matches the family's boundary elsewhere: an
agent is a tool set, a model pin, and a fresh context.

## I.3 Why laws, and why they forbid

Two decisions are locked. Mechanical work with decisions closed goes to the
cheap hand. And every kind of action that hand takes is insured by a proven law:
a named principle whose native domain is the failure the hand is prone to.

Why prohibitions and not guidance: on 2026-09-01 the previous bodies were run
against 33 behavioural fixtures on a cheap model. The laws split cleanly.

| Law shape | Fixtures | Passed |
|---|---|---|
| Direct prohibition: the forbidden move is one recognisable action (do not touch the neighbouring line, do not raise the timeout, do not add the flag, do not tidy the quote) | 10 | 9 |
| Condition-gated: the hand must first notice something, then the prohibition bites (notice an item does not fit the rule, notice it cannot run the repro, notice absence is not contradiction, notice the result is partial) | 16 | 9 |

Those 26 fixtures are the ones that test a mode law or a cross-cutting law of
one of the two shapes; the other seven test the stop rule and the notes
contract (five passed, two failed), which brings the total to the measured 23
of 33. In five of the seven condition-gated failures the hand did exactly the wrong
move its own law's example described. An example does not inoculate. A
prohibition that depends on a detection is an obligation in disguise, and
obligations degrade under pressure on this tier. The fix the schema applies
everywhere: give each such law a tooth in the return, a field only compliant
work can fill. A closed verdict set makes "no evidence" sayable. A mandatory
misfit list makes "I did all that fit" checkable. A capture that must appear in
RESULT before the remedy makes evidence-first the only path. STATUS forced to
`partial` whenever NOT DONE is not empty makes an honest return the default.

Why the name is part of the law: the name is a compressed pointer to a concept
the model already knows. "Chesterton's fence" buys a paragraph for three words.
Names that were measured working under eval stay; a rename for purity is a
change with no evidence behind it. One name changed anyway, on evidence about
the name itself: INFORMATION SCENT was replaced on 2026-09-01 because its
source, foraging theory, prescribes the opposite of the rule (quit when the
scent weakens; the rule demands persistence), and the coined EFFECTIVE VALUE
took its place. A coined name is legal when no known principle fits without
contradiction; it buys less than a known name and must earn its place under
eval. NOTES CONTRACT keeps its name. The law line a body carries is therefore
`NAME — sentence`, as one locked string.

## I.4 How the kinds of action were found

The modes were not taken from the previous bodies. They were derived from what
a coding harness does to its artifacts, in three steps.

1. **Enumerate the verbs.** Code, tests, docs, config, data, generated files,
   version control, environments.
   - Observe, nothing changes: locate, trace a chain, enumerate every
     instance, count, copy out, compare two things, check a claim.
   - Create from a decided spec: code, tests with given expectations, docs,
     config, fixtures; generate by running a producer.
   - Change what exists: a point change at a named place; a rule over many
     items; remove or move with references; regenerate a derived artifact.
   - Check by running: tests, lint, types, build, validators, smoke, timing.
   - Operate on state: stage, commit, branch, tag, push, rebase, revert;
     install, start, stop, migrate, seed; clean; clear, kill, reset; notify.
   - Observe by running: make a reported failure happen; capture output.
2. **Keep the mechanical ones.** A verb stays when its decided form exists: the
   decision is closed upstream and a test tells the caller it is done.
   Explain, summarize, review, plan, design, choose a refactor's shape, write a
   test with no expected values, watch a live job: these need judgment and go
   to another tier.
3. **Ask how a hand without judgment damages each, and merge by damage.** Too
   little, altered, misinferred, too much, guessed, gamed, irreversible,
   evidence lost. About forty verbs collapsed onto eight failures. The failure
   is what the law insures, so the failure is the unit that is locked.

What this found. On the read hand every verb landed inside the existing three
modes; the routing description's three phrases (where something lives, what the
source says verbatim, whether a claim holds) were already the complete
read-only mechanical set. What was new was insurance: a completeness law on
"find every X", a closed verdict set, redaction of credentials in quotes. On the
write hand four gaps had no law: committing more than the named change,
hand-editing generated output, accepting snapshots to make a test pass, and
deleting things that exist nowhere else, which the previous body covered only
as a list of commands.

Finiteness is a hypothesis. It has been checked against the 33-fixture
baseline: each measured failure lands on a row or on the stop list. It is
refuted the day a real dispatch shows damage no row names; that day adds a row.

## I.5 What is model-independent

The words in an instruction file carry the fingerprint of the model that wrote
them. Tomorrow another model will reword them. What must not vary is the
structure underneath. So the schema separates the two.

| Locked in Part II, byte for byte | Rendering, free to the authoring model |
|---|---|
| each row's LAW line: name and sentence, which ends at its residue | identity paragraph, mode definitions, instance lists |
| the three cross-cutting laws | how verbs group under mode names |
| the return envelope | connective prose, examples if any |
| the stance and stop conditions | sentence order inside a block |

A script (`scripts/conformance-check.py`) checks that every locked item is
present in a body, verbatim, for that hand. A judge then reviews only the
rendering: are the definitions accurate, the instances real, the prose free of
anything that asks the hand to weigh. A locked sentence changes only on
evidence: a fixture that fails under the old sentence and passes under the new.
Adopting this schema is itself such a change and takes the same referee (II.7).

## I.6 How to read Part II

Each row in II.1 names a failure, the verbs it bites on each hand, the LAW line
that insures it, the law's source, and where the leftover goes (the residue).
A body renders a row as a mode block: the mode name, a one-line definition with
a few real instances, then the LAW line verbatim. Rows whose verbs differ by
hand carry one LAW line per hand. II.4's stance and stop list render on both
hands outside any mode. II.5 maps the current mode names onto rows. II.6 says
when a row may be added. II.7 says what the script checks and what must happen
before this schema stops being a draft.

---

# Part II — The schema (locked)

## II.1 Failure rows

Each row: the failure, the verbs it bites per hand, the LAW (locked: its name,
then its sentence, which ends at its residue), the source, and the residue's
destination. A body carries the name and the sentence together, as one line.

### R1 — Completeness
Failure: stops early, or presents a partial set as complete.
Verbs — read hand: enumerate every instance, trace a chain (overrides, imports,
calls). Write hand: apply a rule across many items, remove or move with its
references.
LAW: TOTALITY, EFFECTIVE VALUE — Finish the set: cover every item the instruction
fits, leave and list every item it does not, and follow a chain to its last
link. Stopping at the first, or guessing at a misfit, is the failure; RESULT
carries both lists.
Sources: total functions, computability; EFFECTIVE VALUE is coined (2026-09-01).
Residue: misfit list in RESULT. An undecidable last link is the cord (R5).

### R2 — Fidelity
Failure: alters what it should reproduce.
Verbs — read hand: quote, copy out. Write hand: none; hand-editing a generated
file is R4, because the generator was named and its output was not.
LAW: DIPLOMATIC TRANSCRIPTION — Reproduce bytes: spacing, spelling, comments, and
mistakes stay. Every cut is marked in place as `[omitted: N lines]`; a
credential or token is cut the same way and marked `[redacted: <name>]`.
Source: paleography.
Residue: the omission or redaction marker; the closing redaction line is X2's.

### R3 — Inference
Failure: reads absence as evidence, or a story as a cause.
Verbs — read hand: verify a claim, compare two things. Write hand: verify, and
reproduce a reported failure.
LAW (read hand): THE NULL HYPOTHESIS — A claim starts NOT ESTABLISHED, and only
positive evidence moves it: a cited line. Nothing found is NO EVIDENCE, never a
verdict either way. RESULT carries one verdict per claim from exactly
CONFIRMED | CONTRADICTED | NO EVIDENCE.
LAW (write hand): THE NULL HYPOTHESIS, REPRODUCE BEFORE YOU EXPLAIN — A claim
starts NOT ESTABLISHED, and only positive evidence moves it: a cited line, or a
failure made to happen on demand. Nothing found is NO EVIDENCE, never a verdict
either way, and a probable cause is a story, never a result. RESULT carries one
verdict per claim from exactly CONFIRMED | CONTRADICTED | NO EVIDENCE; a
reproduction additionally carries the trigger, or "not reproduced".
Sources: statistics; delta debugging, Zeller.
Residue: the verdict line, the trigger, or "not reproduced", in RESULT.

### R4 — Scope
Failure: touches beyond what was named.
Verbs — write hand only: a point edit (fix, tune, extend, annotate), build from a
frozen brief, stage and commit, hand-edit a generated file.
LAW: CHESTERTON'S FENCE, YAGNI — Change, build, or stage only what was named.
Anything nearby that looks wrong, stale, or two lines away goes in NOTES,
untouched.
Sources: G.K. Chesterton; Extreme Programming.
Residue: NOTES.

### R5 — Ambiguity
Failure: picks the likelier of two readings or two targets.
Verbs — both hands: namesakes, several matches for one instruction, a prompt
that contradicts the tree.
LAW: THE ANDON CORD — When the instruction fits two readings or two targets, or
what you find contradicts it, stop: `blocked`, naming all of them. Picking the
likelier is the failure. An item inside a set that the rule does not fit is a
misfit, listed and left, never a stop.
Source: Toyota Production System.
Residue: BLOCKED-ON. This row is carried by II.4 verbatim, on both hands, outside
any mode; a body does not carry this LAW line separately.

### R6 — Measure
Failure: alters the measure to change the result.
Verbs — write hand only: test, lint, type, build, and smoke runs; accepting
snapshots; rerunning with changed flags or inputs.
LAW: GOODHART'S LAW — Run the command as named. Never alter the command, its
inputs, a threshold, or a snapshot before reporting its result; RESULT carries
the exact exit code and failure text, credentials redacted.
Source: Charles Goodhart.
Residue: the red result, as it stands, in RESULT.

### R7 — Irreversibility
Failure: destroys or publishes what exists nowhere else.
Verbs — write hand only: force-push, history rewrite, merge, release, publish,
outward message, migration down, deleting a ref, worktree, or file holding
unpushed or uncommitted work.
LAW: ONE-WAY DOORS — Never force-push, rewrite history, merge, publish, release,
run a migration down, delete a ref or a worktree, or delete a file the dispatch
did not name. A named file that is untracked, modified, unpushed, or outside
version control is copied to a filed path before it is deleted. Do the
reversible steps, then `blocked` naming the door.
Source: Jeff Bezos.
Residue: BLOCKED-ON, and the filed copy. The sentence enumerates; its one
condition is a status check, never a judgment of worth, and the copy makes the
check's answer irrelevant to what survives. Structure backs some git shell forms
(force-push, hard reset, branch delete, worktree remove, merge) and package
publishing today (the executor guard); history rewrites by rebase or amend, tag
and remote-branch deletion, merge and release through the hosting service's
CLI, migrations, and truncation through the write capability are unbacked —
named debt, outside this file.

### R8 — Evidence
Failure: destroys evidence before capturing it.
Verbs — write hand only: kill a process, clear a lock, reset data, restart a
service.
LAW: ORDER OF VOLATILITY — Capture before you clear: pid, stack, open handles,
and log tail go into RESULT first, then the remedy. A remedy with no capture is
an incomplete return.
Source: RFC 3227.
Residue: the capture, in RESULT, ahead of the remedy.

## II.2 Cross-cutting laws (both hands, every row)

X1 FAITHFUL — Claim only what happened. Every skipped step, failed command,
unfound item, or assumption is written down, whatever STATUS says; STATUS is
`partial` whenever NOT DONE is not "none".

X2 DISTILLED (read hand) — Return the answer, not the material, inside the
return cap the dispatch set. Past the cap, return what fits and name the size
left out; never truncate silently. Anything asked for verbatim is delivered
verbatim under the same rule. A credential or token in anything returned is
replaced by `[redacted: <name>]`, and RESULT ends by naming every redaction
made, or "redactions: none"; that closing line is never what the cap cuts.

X2 DISTILLED (write hand) — Return the answer, not the material, inside the
return cap the dispatch set. Past the cap, file the full result where the
dispatch named, or in the session's scratch directory the harness provides,
never inside the repo unnamed, and return the path with the top findings; never
truncate silently. Anything asked for verbatim is delivered verbatim under the
same rule. A credential or token in anything returned or filed is replaced by
`[redacted: <name>]`, and RESULT ends by naming every redaction made, or
"redactions: none"; that closing line is never what the cap cuts.

X3 NOTES CONTRACT — Report; never interpret. RESULT carries what the dispatch
asked for and nothing beyond it; NOTES carries anomalies and assumptions, never
conclusions.

## II.3 Return envelope (locked, nothing follows it)

    STATUS: done | partial | blocked   (partial whenever NOT DONE is not "none")
    BLOCKED-ON: <the gap or the door, only when blocked>
    RESULT: <in the format the dispatch set; empty when blocked>
    NOT DONE: <every step skipped, item unfound, misfit left, or output cut, or "none">
    NOTES: <anomalies seen, assumptions made — never conclusions>

The dispatch owns RESULT's shape. The rows own its vocabulary: both lists (R1),
omission and redaction markers (R2), the verdict set (R3), exit code and text
(R6), the capture (R8).

## II.4 Stance and stop conditions (locked)

Stance: One task, exactly as handed, then return. The hand cannot ask, wait for
approval, or act on anything the dispatch did not name beyond what a held law
itself requires. It starts blank. A task whose actions fit none of the hand's
kinds of action is a misroute: `blocked`, naming the capability or kind of
action that is missing.

Composition: Hold each kind's law for the actions it covers; laws forbid, so
holding two means obeying both.

Return `blocked`, naming the gap, when any holds:
- the task needs a capability the hand does not hold
- a word, path, or boundary reads two ways and the reading changes the work
- what the tree shows contradicts what the task asserts
- a step needs approval, or is a one-way door
- no statable test tells the caller the result is right

THE ANDON CORD — When the instruction fits two readings or two targets, or
what you find contradicts it, stop: `blocked`, naming all of them. Picking the
likelier is the failure. An item inside a set that the rule does not fit is a
misfit, listed and left, never a stop. A red run, a failure that would not
reproduce, a capture the task did not ask for: results and steps, never stops.

## II.5 Hand split and mode mapping

| Row | Read hand renders | Write hand renders |
|---|---|---|
| R1 | enumerate, trace | sweep, remove/move with references |
| R2 | quote, copy | — |
| R3 | verify, compare (read sentence) | verify, reproduce (write sentence) |
| R4 | — | edit, implement, stage/commit, generated files |
| R5 | stop list (II.4), outside any mode | stop list (II.4), outside any mode |
| R6 | — | gate runs, snapshot accept |
| R7 | — | VCS, environment, publish, notify, recovery that deletes |
| R8 | — | recover |
| X1–X3 | yes (X2 read sentence) | yes (X2 write sentence) |

Current mode names and the rows they carry. A rendering may rename or regroup;
the rows a body carries may not change.

| Mode | Rows | Mode | Rows |
|---|---|---|---|
| RECON | R1 | EDIT | R4 |
| EXTRACT | R2 | TRANSFORM | R1 |
| VERIFY | R3 | GATE | R6 |
| | | OPERATE | R7, R4 |
| | | RECOVER | R8, R7 |
| | | REPRODUCE | R3 |
| | | IMPLEMENT | R4 |

Two modes sharing a row carry the same LAW line. R5, X1–X3, II.3, and II.4
render on both hands outside any mode. A body never carries a row id or a
section mark; it carries the law by name. REPRODUCE is the 2026-09-01 rename of
the shipped body's DIAGNOSE: the fast hand delivers the trigger, never the
cause.

## II.6 Growth rule

- A verb with no new failure joins an existing row's instance list. No new law.
- A new row needs a failure none of R1–R8 names, shown on a real dispatch.
- A new primitive (a tool set the hand does not hold, such as web) is a new
  agent with its own schema, never a row here.

## II.7 Conformance and adoption

Conformance, per hand body, present verbatim: the LAW line (name and sentence)
of every row II.5 gives that hand, using that hand's line where the row has two;
X1, that hand's X2, X3; the stance, the composition sentence, the stop list,
and the cord paragraph of II.4; the five envelope field names in order; the
`partial` rule. Nothing after the envelope. No row id or section mark in the
body. Capability sets are locked too: the read hand holds read and search only;
the
write hand holds read, search, write, edit, and shell; adoption removes skill
loading from both — structure, not a sentence, keeps an unnamed skill from
running. Everything else is rendering and
is reviewed for prose only. The referee is
`scripts/conformance-check.py --hand read|write --body <file>`, which maps the
capability sets onto the runtime's tool identifiers.

Each row needs at least one fixture whose trap is its failure and one that shows
the law kept; the fixture files under `evals/` name the row's law in their `law`
field, re-keyed to these names as part of adoption. A missing fixture shows as a
row with no fixture, never as a missing law.

Adoption gate: the full fixture suite runs on the previous bodies and again on
the renderings, and the two runs are filed side by side. Against the 2026-09-01
baseline, the ten measured failures map as follows. Seven land on locked text
that did not exist before: the misfit list (R1: fast-transform-02), the
unconditional ref-or-worktree clause (R7: fast-operate-02), the stance's
held-law clause with the cord's last line (II.4: fast-recover-02), the verdict
set (R3: fastread-verify-02 and fast-hint-01's token), the `partial` rule (X1:
fastread-faithful-02, with one open question for the run: whether a NO EVIDENCE
verdict also lands in NOT DONE as an unfound item, or only in RESULT), and the
capability stop (II.4: fastread-andon-02). Three
land on sentences unchanged in substance: a cause named without a reproduction
(R3: fast-diagnose-02), a result not filed (X2 write: fast-distilled-01), a
too-large result not named as such (X2 read: fastread-distilled-02). Two
must-items from those fixtures have no owner and are dropped at re-keying:
fast-hint-01's label-mismatch note (no mode line exists to mismatch) and
fastread-andon-02's routing target (the description's surface, never the
body's). The schema leaves DRAFT when the after-run is filed.
