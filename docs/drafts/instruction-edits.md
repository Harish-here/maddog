# Instruction-file edits for docs/plans/executor-fast-read.md

Draft only — nothing here has been applied. Each item names the target file,
quotes the current text verbatim (grep-verified at exactly one hit — see the
executor return's SNIPPET AUDIT table), and gives the proposed replacement
verbatim. Two items go beyond the plan's literal task text; each is marked
FINDING (self-review, not authorized by a specific plan line) and left for
the owner's call — everything else is a direct transcription of a CLOSED
decision.

---

## agents/executor-fast.md

### Edit 1 — frontmatter description (T2)

BEFORE:
```
description: >
  Runs fully-specified MECHANICAL tasks on a cheap, fast model: bulk
  find/replace, applying a known edit across many files, running tests or
  linters, grep/glob search, extracting/reformatting data, scaffolding
  boilerplate, committing, pushing, opening a PR, restarting a service,
  clearing a stale lock, reproducing a reported bug. Use when every decision
  is already closed and acceptance is objective. Do NOT use
  for ambiguous refactors, design choices, or any plausible-but-wrong-output
  task — those go to executor-smart. If the project defines its OWN executor
  agent, prefer it at the same tier. Do NOT plan or make architectural calls
  — those stay with your caller. Do NOT use for web research — it holds no
  web tools; that goes to researcher.
```

AFTER (gate-03 F1: the write-or-not test alone is not decisive — this file's
own list includes running tests/linters, which change nothing on disk — so
the test is now TWO-PRONGED: disk/running-system change, OR requiring a
command at all. Also rewritten to be slot-for-slot SYMMETRIC with
`executor-fast-read`'s description — same five slots, same order, same
phrasing wherever the content is the same; the two-pronged test is the one
axis that differs, stated positively on both sides):
```
description: >
  Runs fully-specified MECHANICAL tasks on a cheap, fast model: a decided
  edit, one rule across many files, test and build runs, git and service
  operations, state recovery, bug reproduction, code from a frozen brief.
  Use when the task changes something on disk or in a running system, or
  requires running a command, and every decision is already closed with
  acceptance objective. Do NOT use for read-only work that changes nothing
  and runs no command — that goes to executor-fast-read. Do NOT use for
  ambiguous refactors, design choices, or any plausible-but-wrong-output
  task — those go to executor-smart. Do NOT use for web
  research — it holds no web tools; that goes to researcher.
```

Drops the RECON/EXTRACT examples ("grep/glob search, extracting/reformatting
data") since those modes leave this file (decision 4); the two-pronged test
replaces the flawed single-prong "changes something on disk" test (decision
11, revised by gate-03 F1); adds the redirect to `executor-fast-read` for
read-only, no-command work (decision 21); drops "If the project defines its
OWN executor agent, prefer it at the same tier" — owner ruling: this clause
is an assumption imported from a different repository that this one does not
hold, and must not be restored as a helpful-looking hint.

Also drops "Do NOT plan or make architectural calls — those stay with your
caller" outright — owner ruling: the slot was doubly redundant, never
load-bearing for hand selection. The "Use when" slot already requires every
decision to be closed, and an architectural call is by definition an open
one; the `executor-smart` redirect already excludes "design choices" and,
unlike this clause, names where the work goes instead. A clause that repeats
an exclusion and names no destination earns no place in a description meant
to be as slim as possible — a clause earns its place only if it changes
which hand gets picked and says something no other slot already says. This
is the DESCRIPTION copy only: the equivalent rule in the agent BODY ("Scope,
architecture, and cross-task decisions are not yours — they stay with your
caller") stays untouched — the body is read by the agent, the description by
the caller, and the body's copy repeats nothing else there. Removing this
clause drops a whole slot rather than shrinking one, so the slot count falls
from six to five on both sides.

Partition check: `executor-fast-read`'s mirrored test is the exact logical
negation — "changes nothing on disk or in a running system AND requires no
command execution." A ∨ B here, ¬A ∧ ¬B there: every task shape lands on
exactly one side, none on both, none on neither.

Also replaces slot 2 (the example list right after "on a cheap, fast
model:") — owner ruling: one example per mode. The old ten-item list
("bulk find/replace, applying a known edit across many files, running
tests or linters, scaffolding boilerplate, committing, pushing, opening a
PR, restarting a service, clearing a stale lock, reproducing a reported
bug") named ten things for seven modes, with "bulk find/replace" and
"applying a known edit across many files" naming the same thing twice, and
"committing, pushing, opening a PR" naming three names for one activity —
while RECOVER and IMPLEMENT had no example at all. The new seven-item
list maps one-to-one onto the seven remaining modes, in CLASSIFY FIRST
order:

| Mode | Example |
|---|---|
| EDIT | a decided edit |
| TRANSFORM | one rule across many files |
| GATE | test and build runs |
| OPERATE | git and service operations |
| RECOVER | state recovery |
| DIAGNOSE | bug reproduction |
| IMPLEMENT | code from a frozen brief |

`executor-fast-read`'s slot 2 gets the same treatment, mapping one-to-one
onto its three modes:

| Mode | Example |
|---|---|
| RECON | where something lives |
| EXTRACT | what the source says verbatim |
| VERIFY | whether a claim holds |

**The two lists' grammar differs on purpose — owner-ruled, do not
harmonize.** `executor-fast`'s list names things done (a decided edit, one
rule across many files, test and build runs...) because that hand changes
something. `executor-fast-read`'s list names questions answered (where,
what, whether...) because that hand changes nothing — it can only ever
produce an answer, never an effect, so the grammar itself carries the
read-only axis instead of a phrase having to state it. A later editor
tidying the read list into parallel gerunds ("locating where something
lives, extracting what the source says verbatim, verifying whether a
claim holds") would erase the one deliberate textual signal of the
read/write axis and must not do so.

### Edit 2 — CLASSIFY FIRST mode count (T2, decision 4)

BEFORE (one grep hit): `CLASSIFY FIRST. Every task you are handed is one of the ten MODES below. Name the`

AFTER: `CLASSIFY FIRST. Every task you are handed is one of the seven MODES below. Name the`

### Edit 3 — remove RECON, EXTRACT, VERIFY mode blocks (T2, decision 2/4)

BEFORE (currently between the CLASSIFY FIRST paragraph and the EDIT mode block):
```
RECON — locate, map, inventory, or answer "how does X work" from a codebase or corpus.
  INFORMATION SCENT (Pirolli & Card). Follow the strongest lead until the trail stops
  producing new facts; the first hit is a waypoint, not the destination.
  E.g. asked where a retry limit is set, you find the default, then the caller that
  overrides it, then the env var that overrides that. Reporting only the default is a
  wrong answer, not a partial one.

EXTRACT — reproduce source material: code, config, prose, output, log lines.
  DIPLOMATIC TRANSCRIPTION (paleography). Reproduce exactly what is there — spacing,
  spelling, comments, oddities — and mark any omission rather than smoothing it away.
  E.g. a config line arrives mis-indented with a stale trailing comment; you quote it
  mis-indented and with the comment. Tidying it produces a line that does not exist.

VERIFY — decide whether a claim, assumption, or document matches reality.
  THE NULL HYPOTHESIS (statistics). Every claim starts at NOT ESTABLISHED, and only
  positive evidence moves it; failing to find a contradiction moves nothing.
  E.g. asked to verify "the timeout is 30s", the line setting it to 30s confirms it.
  Grepping and finding nothing that says otherwise is NO EVIDENCE, never CONFIRMED.

EDIT — apply a change whose content is already decided: supplied text, a named fix, a
```

AFTER (block removed entirely — CLASSIFY FIRST paragraph's blank line runs straight into EDIT):
```
EDIT — apply a change whose content is already decided: supplied text, a named fix, a
```

This whole block (opening `RECON —` line through the blank line before `EDIT —`) is
grep-verified unique as a contiguous span (it contains `RECON — locate, map, inventory,
or answer "how does X work"`, confirmed one hit, as its distinguishing first line).

---

## agents/executor-smart.md

### Edit — remove "prefer a project's own executor" clause (owner ruling)

Owner ruling: "If the project defines its OWN executor agent, prefer it at the
same tier" is an assumption imported from a different repository — this one
does not hold it — and must be removed, not softened, so a later reader does
not restore it as a helpful-looking hint.

BEFORE (grep-verified one hit as a contiguous span):
```
  cost, or after executor-fast returns blocked. If the project defines its
  OWN executor agent, prefer it at the same tier. Do NOT use for mechanical,
```

AFTER:
```
  cost, or after executor-fast returns blocked. Do NOT use for mechanical,
```

This snippet ends exactly where it started relative to the following
"objective work (bulk edits, test runs, search, extraction, a reliable bug
repro)..." text, which the next edit below still targets unchanged — the two
edits apply independently and in either order.

### Edit — "Do NOT use" clause (T3 group B, round 2 NF5, round 3 F4)

The plan's T3 instruction is "changes the named hand to executor-fast-read... unless
the authoring pass finds the surrounding sentence now reads oddly." It does: the
clause names four example tasks (bulk edits, test runs, search, extraction, a bug
repro) under ONE redirect to `executor-fast`; only two of those four (search,
extraction) are RECON/EXTRACT-shaped and belong on `executor-fast-read` — the other
two (bulk edits, test runs, bug repro) are EDIT/GATE/DIAGNOSE-shaped and stay on
`executor-fast`. A blind rename would misroute test runs and bug repros to a hand that
holds no shell. Split instead:

BEFORE (two lines, wrap-anchored per round 3 F4 — each independently one grep hit):
```
  objective work (bulk edits, test runs, search, extraction, a reliable bug
  repro) — executor-fast, cheaper. Do NOT make cross-task or architectural
```

AFTER:
```
  objective work (bulk edits, test runs, a reliable bug repro) —
  executor-fast, cheaper — or read-only search/extraction —
  executor-fast-read, cheaper still. Do NOT make cross-task or architectural
```

---

## agents/executor-lead.md

### Edit — remove "prefer a repo-local executor" clause (owner ruling)

Same assumption as the `executor-fast`/`executor-smart` clause above, in the
body rather than the description: "Prefer a repo-local executor at the same
tier over a generic one" was imported from a different repository that this
one does not hold. Read the surrounding CHEAPEST COVERING TIER paragraph
before cutting — the sentence sits between "however important it is." and
"Web research goes to researcher", and removing it must leave that paragraph
reading straight through.

BEFORE (grep-verified one hit as a contiguous span):
```
however important it is. Prefer a repo-local executor at the same tier over
a generic one. Web research goes to researcher — executors stay web-free.
```

AFTER:
```
however important it is. Web research goes to researcher — executors stay web-free.
```

The paragraph still reads coherently: "a task whose decisions you already
closed is fast-tier however important it is. Web research goes to
researcher — executors stay web-free. Verbatim material into artifacts is
script work..." — no dangling reference, no orphaned clause.

---

## agents/executor-judge.md

Round 1 finding 3: exactly five bare `executor-fast` hits, all inside three spots
(lines 14, 15, 31, 33, 106). T8 renames all five to `executor-fast-read`.

### Edit 1 — frontmatter description (lines 14-15)

BEFORE: `  executor-fast. Never dispatch this agent to fix anything or author`

AFTER: `  executor-fast-read. Never dispatch this agent to fix anything or author`

BEFORE: `  anything: it holds no Write or Edit and can dispatch only executor-fast or`

AFTER: `  anything: it holds no Write or Edit and can dispatch only executor-fast-read or`

### Edit 2 — DISPATCH note (lines 30-35)

BEFORE:
```
- You hold no Write or Edit tool, and `scripts/judge-dispatch-guard.sh` blocks you from
  dispatching any subagent but `executor-fast` or `researcher` — including a dispatch
  that names none, which would default to a general-purpose agent holding every tool.
  Do not fix anything yourself, and do not dispatch a fix: rent `executor-fast` only for
  evidence (a sweep, an extraction, a gate-run), never a repair. A defect you find
  routes back to the party that owns the fix, as a finding — never as a delegated edit.
```

AFTER (renames the two bare hits at lines 31 and 33; the FINDING below also touches
this block — see after the plain rename):
```
- You hold no Write or Edit tool, and `scripts/judge-dispatch-guard.sh` blocks you from
  dispatching any subagent but `executor-fast-read` or `researcher` — including a
  dispatch that names none, which would default to a general-purpose agent holding
  every tool. Do not fix anything yourself, and do not dispatch a fix: rent
  `executor-fast-read` only for evidence (a sweep, an extraction), never a repair — run
  any gate yourself via your own shell, since the rentable hand holds no shell. A
  defect you find routes back to the party that owns the fix, as a finding — never as a
  delegated edit.
```

**FINDING (self-review, not a T8 line — flagged, not authorized).** The original text
lists "a gate-run" among the things you may rent `executor-fast` for. After decision 8
the only rentable hands are `executor-fast-read` (no shell) and `researcher` (web-only,
no shell either) — neither can run anything. Left as a bare rename, this sentence
would tell the judge to rent a hand for a job that hand structurally cannot do. The
AFTER text above drops "a gate-run" from the rentable list and routes it to the
judge's own Bash tool instead (DELEGATION point 4, DIRECT VERIFICATION, already grants
this). Flagging because it sits one line outside the five grep-verified hits T8 names,
so it would not be caught by a literal "rename executor-fast" pass.

### Edit 3 — DELEGATION point 2 (line 106) + shrink (decision 9)

BEFORE:
```
2. DISPATCH TARGETS — executor-fast and researcher ONLY. Never executor-smart, never
   executor-lead. Never dispatch an edit of any kind — a judge that causes a fix has
   stopped being a judge; report the finding instead.
```

AFTER (renamed and shrunk — the "never executor-smart/lead" and "never dispatch an
edit" clauses are now enforced structurally by the guard, per decision 9, so the
instruction-side statement of them is reduced, not repeated at length):
```
2. DISPATCH TARGETS — executor-fast-read and researcher ONLY, structurally enforced
   by `judge-dispatch-guard.sh`. Report a needed fix as a finding, never dispatch one.
```

**FINDING (self-review, not a T8 line — flagged, not authorized).** DELEGATION point 3
has the same "gate-run" defect as Edit 2 above (it does not contain the literal string
`executor-fast`, so it falls outside T8's five named hits, but it names the same
now-void rental):

BEFORE:
```
3. EVIDENCE NEEDS discovered mid-review are normal: rent fast for sweeps, extraction,
   and gate-runs — a rented gate-run must return the raw output (the red and its
   failure text, or the passing run's tail); its PASS/FAIL word alone is a
   characterisation you may not rule on; rent researcher when a claim hinges on
   external documentation (its return is doc quotes — material, not a conclusion). Claims genuinely unverifiable
   (no reachable evidence, not merely inconvenient to check) are ruled "unverified
   assumption" in FINDINGS — that is itself a verdict, not a blocker. Evidence that
   should exist but does not (the file a report cites is absent, the test it claims
   passing does not run) is blocked only when it carries the review's sole load-bearing claim; otherwise record it as an unverified-assumption finding and continue.
```

AFTER:
```
3. EVIDENCE NEEDS discovered mid-review are normal: rent executor-fast-read for
   sweeps and extraction; run any gate yourself via your own shell (DIRECT
   VERIFICATION, point 4 below) and report its raw output (the red and its failure
   text, or the passing run's tail) — a PASS/FAIL word alone is a characterisation you
   may not rule on; rent researcher when a claim hinges on external documentation
   (its return is doc quotes — material, not a conclusion). Claims genuinely unverifiable
   (no reachable evidence, not merely inconvenient to check) are ruled "unverified
   assumption" in FINDINGS — that is itself a verdict, not a blocker. Evidence that
   should exist but does not (the file a report cites is absent, the test it claims
   passing does not run) is blocked only when it carries the review's sole load-bearing claim; otherwise record it as an unverified-assumption finding and continue.
```

Point 1 ("RENT HANDS, NEVER VERDICTS") and point 4 ("DIRECT VERIFICATION") are
untouched per T8's explicit instruction.

**Debt, not fixed here (gate-03 F5).** DELEGATION point 4 itself reads "you may run
gates or greps yourself via Bash to test a..." — a shipped body naming a tool
identifier (`Bash`), which is the same adapter-set violation `CLAUDE.md` forbids and
that both edits above just avoided introducing. It predates this plan and T8
explicitly leaves point 4 untouched, so it is recorded here as pre-existing debt for
a future pass, not corrected as part of this change.

With Edits 2-3 and both findings folded in,
DELEGATION shrinks from its 25-line baseline (96-120) — satisfying T8's DONE-WHEN —
while keeping the section's intent (rent for evidence, judge yourself, never delegate
a fix) exactly as before.

---

## agents/product-pm.md, product-ux.md, product-be.md, product-ui.md (T3 group B)

Each is a single-word rename, no surrounding change — all four are RECON-shaped
(pure enumeration, no shell needed), so a plain rename is safe here (unlike
executor-judge.md's gate-run clauses above).

| File | BEFORE | AFTER |
|---|---|---|
| `agents/product-pm.md` (line 40) | `APP RECON: delegated to executor-fast, with hard output caps in every` | `APP RECON: delegated to executor-fast-read, with hard output caps in every` |
| `agents/product-ux.md` (line 22) | `JOURNEY RECON: delegated to executor-fast, same output-cap discipline as` | `JOURNEY RECON: delegated to executor-fast-read, same output-cap discipline as` |
| `agents/product-be.md` (line 26) | `enumerations to executor-fast — storage engines and schemas, the` | `enumerations to executor-fast-read — storage engines and schemas, the` |
| `agents/product-ui.md` (line 25) | `enumerations to executor-fast — framework, styling system, component` | `enumerations to executor-fast-read — framework, styling system, component` |

`agents/product-qa.md:90` ("Dispatch to executor-fast, by name, exactly these: gate
runs...") is the named exemption (decision 13) — GATE-shaped, needs a shell, stays on
`executor-fast`. Not edited.

---

## README.md (T3 group C)

### Edit 0 — lead/judge rental line (line 81-83, gate-03 F4)

The dispatch retarget (judge's guard now allows only `executor-fast-read` and
`researcher`, per the `agents/executor-judge.md` edits above) makes the current
sentence false for the judge: it can no longer rent the full fast-tier hand, only
the read-only one.

BEFORE (grep-verified one hit as a contiguous span, opening line quoted):
```
smart do the work; lead holds memory across a package; lead and judge can
rent fast-tier hands, lead smart-tier too; judge rules on the others'
output and can never edit. The guard scripts enforce the last part.
```

AFTER:
```
smart do the work; lead holds memory across a package; lead can rent
fast-tier hands, smart-tier too; judge can rent only the read-only
fast-tier hand; judge rules on the others' output and can never edit. The
guard scripts enforce the last part.
```

### Edit 1 — Executor family list (line 80, round 3 F5)

BEFORE: `**Executor family** (`executor-fast`, `executor-smart`, `executor-lead`,`

AFTER: `**Executor family** (`executor-fast`, `executor-fast-read`, `executor-smart`, `executor-lead`,`

(The word "executor-fast" itself is not retargeted here — this adds the fifth family
member, it does not move a dispatch.)

### Edit 2 — executor-fast bullet (lines 86-88, round 2 NF5)

BEFORE:
```
- **executor-fast** — runs fully-specified mechanical tasks on a cheap, fast
  model: bulk edits, test/lint runs, search, extraction, boilerplate,
  committing, pushing, opening a PR.
```

AFTER (moves "search, extraction" into a new bullet, per T3):
```
- **executor-fast** — runs fully-specified mechanical tasks on a cheap, fast
  model: bulk edits, test/lint runs, boilerplate, committing, pushing,
  opening a PR.
- **executor-fast-read** — runs read-only mechanical tasks on the same
  cheap, fast tier, holding no shell and no edit: search, extraction,
  verifying a claim against reality.
```

### Edit 3 — Architecture, in brief (lines 159-165, round 3 F5)

BEFORE:
```
Route every task on its *shape*, never the subject's sophistication: a task
with every decision already closed and objective acceptance goes to
`executor-fast`; one task carrying local judgment inside a fixed boundary
goes to `executor-smart`; a package needing judgment with memory across
several steps goes to `executor-lead`; a verdict on another intelligence's
output goes to `executor-judge`. `product-engineering` is a second,
orthogonal axis — a discipline pipeline, not a judgment tier.
```

AFTER:
```
Route every task on its *shape*, never the subject's sophistication: a task
with every decision already closed and objective acceptance goes to
`executor-fast`; the read-only slice of that shape — locating, reproducing,
or verifying, with no shell and nothing to write — goes to
`executor-fast-read`; one task carrying local judgment inside a fixed
boundary goes to `executor-smart`; a package needing judgment with memory
across several steps goes to `executor-lead`; a verdict on another
intelligence's output goes to `executor-judge`. `product-engineering` is a
second, orthogonal axis — a discipline pipeline, not a judgment tier.
```

---

## skills/advisor-mode/SKILL.md (T9)

### Edit — define the read/write hands in the Bind structural-contract table

The mechanical-split edit below introduces "the read hand" and "the write
hand" in Routing, but the skill defines neither term anywhere, and its Bind
section still assumes one hand per class. Define both terms here, in Bind,
since Bind's table physically precedes Routing in the file — first use.
Both are named as roles, never as agent names, preserving the table's own
stated invariant ("This table names no agents, the binding record supplies
the hands").

BEFORE (grep-verified one hit):
```
| mechanical / local / iterated | Needs the task's tools. Where no guard covers an irreversible step, it stays foreground and advisor-supervised. |
```

AFTER (splits the one row into two: mechanical now binds two hands, each
with its own structural contract; local and iterated are unaffected and
stay bundled with mechanical's write hand, since all three need only "the
task's tools"):
```
| mechanical — read hand | No shell, no edit capability: cannot change anything or run anything. |
| mechanical — write hand / local / iterated | Needs the task's tools. Where no guard covers an irreversible step, it stays foreground and advisor-supervised. |
```

### Edit — "the binding record names the hand" accommodates two hands

Mechanical now binds two hands, so the sentence declaring what the binding
record names, singular, no longer covers every class.

BEFORE (grep-verified one hit as a contiguous span):
```
Per class, the binding record names the hand. It also names invariants
satisfied. It also names any degradation. An unqualified class is DEGRADED or UNBOUND.
Never substitute a class silently.
```

AFTER:
```
Per class, the binding record names the hand — mechanical names two, one
per structural contract above. It also names invariants satisfied. It also
names any degradation. An unqualified class is DEGRADED or UNBOUND. Never
substitute a class silently.
```

With both edits above applied, "the read hand" and "the write hand" are
defined terms (roles, not agent names) by the time Routing's new sentence
below uses them — the routing split reads coherently to a reader who has
not seen any of the edits that motivated it.

### Edit — mechanical class split test

Anchor: the `## Routing` table's `kept` row is the table's last row; the new sentence
is inserted immediately after the table, before `### Tie-breaks` (decision 10 calls
for "one sentence near the mechanical row... or a footnote" — a footnote right after
the table reads better than breaking a table cell, and keeps the table itself
agent-name-free per its own stated invariant).

BEFORE (last table row, then the section break):
```
| kept | Architectural, user-facing judgment. Never for sale. E.g. whether to build the feature at all: delegating it hands away the duty. |

### Tie-breaks
```

AFTER (gate-03 F1: the single-prong test — "changes anything on disk or in a
running system" — is not decisive on its own; a test/lint run changes nothing on
disk and still needs the write hand's shell. Two-pronged, matching the
description-level fix above):
```
| kept | Architectural, user-facing judgment. Never for sale. E.g. whether to build the feature at all: delegating it hands away the duty. |

Within mechanical, split by one test: does the task change anything on disk
or in a running system, or require running a command? No to both → the
read hand. Yes to either → the write hand.

### Tie-breaks
```

No agent name appears in the new sentence, preserving the table's stated invariant
("This table names no agents, the binding record supplies the hands").

---

## Gate-03 disposition notes (not file edits)

**F6, out of scope for any named task.** `agents/researcher.md:11` reads
"executor-fast for web research — this agent exists so the shared executors ...
[hold no web tools]" and names only `executor-fast`; it does not mention
`executor-fast-read`. No T-task in this plan touches `researcher.md`, so no edit is
proposed here — flagged for the owner as a stale reference the plan's task list
missed, to be picked up in a future revision or a dedicated task.

**F7, cosmetic — refused, reason recorded.** The mode blocks in
`executor-fast-read.body.md` (RECON/EXTRACT/VERIFY) omit the literal
`NAME — takes: ... Output: ... LAW: NAMED PRINCIPLE (attribution) — statement. E.g.
...` shape `references/agent-template.md` declares. They were copied verbatim from
`agents/executor-fast.md`, whose own ten mode blocks use the same shorter shape
(name — one-line scope, then LAW paragraph, then E.g.) and have never carried
explicit "takes:"/"Output:" labels. Reshaping only the new file's three blocks
would make it the one file in the executor family with the template's literal
labels while every sibling (fast, smart, lead, judge) keeps the older shape —
trading one cosmetic gap for a family-wide inconsistency, and doing so unilaterally
in a task scoped to two draft files, not a family-wide format pass. Left as
inherited, with this note as the record of why; the template-vs-shipped-shape gap
is family-wide pre-existing debt, not something this task introduced or is
positioned to fix alone.
