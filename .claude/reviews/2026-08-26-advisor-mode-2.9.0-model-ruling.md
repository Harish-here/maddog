# advisor-mode 2.9.0 model gate — judge ruling (filed verbatim, 2026-08-26)

I'll start by reading the target model and the incumbent skill.
----
MODE: DESIGN-REVIEW. Target and contract are present. Reading primary evidence.
----
MODE: DESIGN-REVIEW (premortem). Target and contract both present; ruling below.

**VERDICT: REWORK**
D1: APPLY-WITH-CUTS · D2: REWORK · D3: APPLY · D4: REWORK · D5: APPLY-WITH-CUTS · D6: REWORK · D7: APPLY-WITH-CUTS

(model = `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/519de2d7-f923-4beb-87eb-9ca807b4a97d/scratchpad/advisor-2.9.0-model.md`; SKILL = `/Users/harishamutha/maddog-skills/skills/advisor-mode/SKILL.md`)

**FINDINGS**

F1 BLOCK — D6. Silent bind removes the statement that `references/ledger.md:76-79` makes the routing gate's key: "the routing gate keys on the statement NAMING every routed class's hand ... a prohibition at the consumer". Six months on, an advisor with a clean bind never makes the statement, reads ledger.md at the flip, and finds routing was prohibited all session — or ignores the reference and the prohibition dies. Also `ledger.md:66-68` ("always NAMES each routed class's hand"). Clears with: a ruling on which artifact the routing gate keys on when nothing is said, plus the ledger.md amendment in the same packet.

F2 BLOCK — D6. Eval fixture `evals/advisor-mode.json:24-32` (`kept-exempt-from-bind`, core, pins 2.8.0 MAJOR F3) requires the binding record to name a hand per routed class and state kept exempt. "a clean bind is silent" (model.md:82) reads as a prohibition on emitting it, so the fixture fails by design — and the model's fixture-debt clause (model.md:96) names memory fixtures instead, of which **none exist** (`grep -i memory evals/advisor-mode.json` → empty). Clears with: a ruling on whether silence is "not proactively stated" or "not stated when asked", and a corrected debt list.

F3 MAJOR — D4. Item 4 says "keep only: read absent.md before any unattended dispatch", which discards the rest of `SKILL.md:281` — including the definition of unattended ("work authorized on their way out, a dispatch already running when the user says they are leaving, and sessions starting with no user at all"). Combined with the ledger-narrative move (model.md:54), the WARM body no longer names any departure shape except a fresh launch; the mid-flight and no-user-at-all shapes survive only in `absent.md:84-91`, read after the condition is recognised. This is checklist class 9 (`.claude/skills/review-agent/references/checklist.md:238`) and reopens the divergence that cost three rounds in 2.8.0 (memory `advisor-mode-review-2-8-0-thread.md:15`). Clears with: a ruling on what minimum departure-trigger text stays resident.

F4 MAJOR — D4. Item 5 (efficient-md unconditional at session open) silently reverses a shipped 2.8.0 remedy: `CHANGELOG.md:15` — "efficient-md's BIND invocation now cites the installed-skill list already in session context as its discovery evidence (F4)" — and `SKILL.md:197-200`. Failure shape is known and recorded: plugin cache lag left a shipped skill unregistered (memory `advisor-mode-review-2-8-0-thread.md:25`); the unconditional form gives no fallback (checklist dimension 7 / class 10), and the family peer `.claude/skills/author-agent/SKILL.md:68` stays conditional. Clears with: a ruling that the 2.8.0 F4 remedy is overruled and why, or restoration of the evidence check.

F5 MAJOR — D2. The dependency test splits on the commonest case in this repo: hand A implements, a review returns findings, B is "apply the findings". Test (a) and (b) both hold, so one advisor resumes; another reads "never resume after a rejected ... return" (model.md:31) as covering a findings-bearing return and dispatches fresh. Second splitter: same judge, new artifact, same package, overlapping files — resume by the test, fresh gate by "three rounds per artifact" (model.md:35). Clears with: a ruling defining "rejected" and whether artifact identity or package identity bounds judge reuse.

F6 MAJOR — D2. Ceilings are named for "fast 2, smart 4" only (model.md:33) — no ceiling for the iterated hand, which is the burst-dispatched, most expensive, most resumable one, nor for web-perception. The tier words also contradict the skill's own rule that it names no hands (`SKILL.md:84`; `ledger.md:69` "the skill deliberately names none"), and are unassignable under a shared-hand DEGRADED bind (`SKILL.md:75-78`). Clears with: a ruling setting ceilings per **class**, iterated included.

F7 MAJOR — D1. Deleting the CLOSE obligation with nothing structural in its place (correct per memory `agent-laws-forbid-not-require.md:17`) also removes the only trigger for qualifying class (c), "shipped state with open debts" (model.md:14) — the exact shape of every thread note this project runs on, e.g. `advisor-mode-review-2-8-0-thread.md:19-28`. Six months on: no thread notes, debts re-derived from git or lost. Clears with: a ruling accepting zero-memory sessions as steady state, or naming the structure (hook / artifact ordering) that carries class (c).

F8 MINOR — D1/D4. `ledger.md:32-34` states CLOSE "is discharged by the surfacing batch and the memory write"; under D1's absent path there is no memory write, and the packet lists no ledger.md edit for it. Clears with: including that line in the packet's scope.

F9 MINOR — D4. Removal item 1 quotes through "There is no report-and-continue path" but the sentence continues ":a write you make yourself is a broken rule" (`SKILL.md:172-173`) — the prohibition teeth of Own Hands. An author following the quote literally may delete both. Clears with: a ruling on the exact residue.

F10 MINOR — D4. Item 3 drops the named field `DELEGATION LOG`, a family-wide guaranteed return slot (`agents/executor-judge.md:133`, `agents/executor-lead.md:179`), for "check where the return says it delegated" — a check that finds nothing when the return is clean, so skipping it becomes silent.

F11 MINOR — D5. Own Context keeps "reading the cited line is not ingestion" (a permission) and drops "A claim cleared by rereading the sentence is not cleared" (`SKILL.md:43`) — the only prohibition-shaped line in that section, and the one carrying the cheap-agent-evidence doctrine.

F12 MINOR — D7. "no parentheticals; no nested clauses" collides with D5's keep-whole of the Bind table, whose adversarial cell is one nested parenthetical rule (`SKILL.md:66`). Clears with: a ruling on whether D7 governs table cells.

F13 MINOR — D2. `.claude/skills/release/SKILL.md:14,129-130` re-gates per head commit with no round bound; a fourth head under the three-round cap has no advisor-bought verdict. Survivable via "the user decides", but the precedence is unstated.

**CUTS** (free to drop, verbatim from the model): `"Fixture debt"` section as written — "Any advisor-mode eval fixture asserting a memory write at CLOSE fails by design under D1 and must be updated in the same packet." No such fixture exists; it is replaced by F2's real debt. Also `"or the equivalent unit"` (model.md:33) — no reachable signal in this harness; the default ceiling always governs.

**NOT EXECUTED**
- Dim 0 file hygiene, Dim 2 routing partition, Dim 4 return-field matrix: the target is a decision model, not a shipped agent/skill file — no frontmatter, no description, no return contract.
- Dim 8 token-weight: partially executed only via D5's word target; the resident text does not exist yet.

**DELEGATION LOG**
executor-fast — five-part verbatim grep sweep (round bounds, DELEGATION LOG, efficient-md, memory-at-CLOSE, advisor-mode fixtures) — still running at ruling time; superseded, I ran each grep myself and every citation above is from my own read or command output.

**NOTES**
Assumptions: (1) "a clean bind is silent" reads as a prohibition on emitting, not merely on volunteering — F2 flips to MINOR under the other reading; (2) D7's "answer-first does not apply" is scoped to the skill body, not to advisor messages, so no conflict with the user's global CLAUDE.md; (3) I treated the model as binding for the packet, and did not weigh alternatives to any locked decision.
----
The sweep returned. It corroborates every citation I made independently and does not disturb the verdict. One addition and one scope note.

**VERDICT UNCHANGED: REWORK** (D1 APPLY-WITH-CUTS · D2 REWORK · D3 APPLY · D4 REWORK · D5 APPLY-WITH-CUTS · D6 REWORK · D7 APPLY-WITH-CUTS)

**Added finding**

F14 MINOR — D1/D4. `skills/advisor-mode/SKILL.md:186` (inside the Ledger section) states flatly "While the user is present, decisions go to the surfacing batch and to memory at CLOSE." D1 makes the memory write approval-gated and D4 rewrites the Ledger section, but the model names this sentence in neither list — model.md:54 touches only the Ledger's opening narrative, model.md:72 only CLOSE. Shipped as written, the body carries an unconditional memory claim next to the new approval-gated rule, which is the cancelled-obligation shape memory `agent-laws-must-not-contradict` warns about. Clears with: a ruling adding SKILL.md:186 to the packet's edit scope.

**Corroboration, no new findings**

- Round bounds: `workflows/sdd-task-loop.js:41` ("one fix round + scoped re-review"), `agents/product-ux.md:101` ("One fix round maximum"), `skills/product-engineering/SKILL.md:146` ("Budget 2 fix rounds") are all tighter than D2's three and are preserved by `SKILL.md:226`. F13 stands as the only round-bound finding, and stays MINOR.
- `DELEGATION LOG` is a declared return field in eight agent definitions, not two — F10's evidence base is wider than I cited, severity unchanged.
- efficient-md references match F4's set exactly; `README.md:105` and `skills/plain-english/SKILL.md:8` add no conditional/unconditional claim either way.

**DELEGATION LOG (final)**
executor-fast — five-part verbatim grep sweep (round bounds, DELEGATION LOG, efficient-md, memory-at-CLOSE, advisor-mode fixtures) — returned raw file:line quotes only, no verdicts; every line it returned that I rely on I had already read or reproduced myself.

**NOTES**
The sweep excluded `.claude/reviews/` and `.claude/worktrees/`. `.claude/reviews/2026-08-26-advisor-mode-design-review.md` is named by `evals/advisor-mode.json:4` as the filed rulings behind the three core fixtures; I did not read it, so F2's account of what those fixtures pin rests on the fixture file itself, not on the ruling it cites. That is a limit on F2's provenance, not on its evidence — the fixture text is primary and I read it directly.