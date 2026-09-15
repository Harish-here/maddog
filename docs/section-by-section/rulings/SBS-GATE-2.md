VERDICT-ID: SBS-GATE-2

**P1 VERDICT: REWORK** — one load-bearing regression the rework itself introduced: the F5 widening, applied to both premium slots, forbids writing to "any other existing file's path" with no carve-out for the pass's own ledger, which the file's own line 337 requires be written after every closure and resumed from after context loss.

## FOLD AUDIT

Pre-rework bytes were unavailable for a mechanical diff (`p1-extracted.md` and `p1-new.md` are both byte-identical to the packet block — `diff` empty — so neither preserves the round-0 text). The audit below rests on the prior ruling's verbatim quotes plus a full re-walk of every spec §§2-9 element against the current file.

- **F2 — folded exactly.** packet:246 carries both user-sentences, byte-matching spec.md:48.
- **F3 — folded exactly.** packet:317 gives the description a user closure; packet:353 extends Prohibition 2 with ", the description included". No over-reach. (Consequence filed as F18.)
- **F4 — folded exactly.** packet:325 guards the citation in the house form — `.claude/skills/author-agent/SKILL.md:72` reads "Where the efficient-md skill is installed"; packet:326 adds the self-contained fallback "otherwise a few hundred lines", consistent with `references/warm.md:1-9`'s ~500-line WARM ceiling. Description S3 is now self-contained. The self-contradiction with Prohibition 4 is gone.
- **F5 — OVER-FOLDED.** Both repairs taken where either sufficed, and the widening swept in the skill's own outputs. See F16.
- **F6 — folded exactly.** packet:228 "optional", packet:262 "where any exist", packet:300 "Evidence reads `—`".
- **F8 — folded exactly.** packet:254 and packet:327 now state one law and put the user in the sentence.
- **F9 — folded exactly.** Numbered step restored (packet:306) with artifact-first ordering (packet:307). No second closure path: Arrange step 3 points back ("as in the walk"), Description last points back ("exactly as a section's are"), Prohibition 2 covers all three. Residual coverage gap filed as F17.
- **F10 — folded exactly.** packet:359-360 gates on all of Open closing; agrees with packet:259. No over-reach.
- **F11 — folded exactly.** packet:341 separator, six columns against six headers.
- **F15 — folded exactly.** packet:269 "where the runtime has none, ask the user for one".
- **Free cuts:** anchor rationale — **taken** (packet:263-264 carries none); "so the user sees the whole file" — **taken** (packet:265-267); RESHAPE rationale — **taken** (packet:283 keeps the precedence, drops the why); anchor-ordering rationale — **taken** (packet:313-317).
- **No fifth cut.** Every spec element survives: §2 scope items, §3's eight verdicts and two markers, §4's five inputs, §5's five tests with RESHAPE precedence, §6.1-6.5 step-for-step, §7's outputs, all six §8 prohibitions, §9's frontmatter keys and seven-element body order (packet:225/257/272/313/319/331/350). Every sentence the prior ruling quoted from the old file is present or accounted for by a named fold.

## FINDINGS

**F16 — load-bearing — REGRESSION — Dimension 3 — packet:233-234 and packet:352 (against packet:269-270, 306-307, 336-337)**
The widened law reads "never write to the target path, or to any other existing file's path" at both premium slots. The ledger is written "after every closure so the pass survives context loss and resumes mid-file" (packet:337) — after the first row, the ledger path is an existing file's path, and on a resume it existed before the pass began. Open step 5 explicitly invites "a durable path when the pass should outlive the session" (packet:269-270), which on a second round on the same target is a pre-existing file. Failure: the agent closes S1, writes row 1, reaches S2's closure, reads the bottom premium slot, and finds its own ledger forbidden — it either stops writing rows (the artifact-first gate at packet:307 then blocks the next proposal and the walk deadlocks) or scatters one file per row. Ground-truth class 1: a law cancelled by another law in the same file, prohibition winning. Two valid repairs, caller's choice, I choose neither: (a) delete the widening clause from both slots and rest on F5's other repair — Assemble step 1 already scopes "never at any existing path" to the MOVE write (packet:334) and gives the MOVE draft a derived name (packet:335); (b) keep the widening and carve out the draft and ledger paths named at Open step 5. Repair (a) is a pure deletion.

**F17 — load-bearing — Dimension 5 — packet:306-307 vs packet:313-317, 327-328**
F9's artifact-first gate converts the ledger-row obligation only where a next proposal follows. Three closures have no following proposal: the last body section, the description's closure (packet:317), and every HOLD closed at Arrange step 3 (packet:327) — Arrange step 4 records MOVE and GAP rows but not the resolved HOLD verdicts. Failure: a pass with two HOLDs loses context between Arrange and Assemble; the rows for the final section and both held verdicts were never written, and the resume the file promises at packet:337 restarts them. Assemble step 2 catches completeness before hand-off, so the blast radius is lost work on a crash, not a wrong output. Converting structure available: gate Arrange step 5's closure, and the Assemble step, on the preceding rows existing — the same artifact-first shape already used in the walk.

**F18 — load-bearing — fold consequence of F3 — Dimension 3/5 — packet:313-317 vs packet:336-338**
F3's fold gave the description a closable verdict and replacement text, but the ledger is "one row per section" and the description carries no `S` id — Open step 4 assigns `S1..Sn` to the target's body sections only (packet:265-267). Failure: the user closes REWORD on the frontmatter description with replacement text; the draft carries the new description; the ledger — stated at spec.md:187 as "the accepted-findings record for the later authoring pass" and handed off at packet:347-348 as the evidence set — has no row for the single highest-consequence line in the file, so the downstream review sees a changed description with no accepted finding behind it. Two valid repairs, caller's choice, I choose neither: give the description a ledger row with a reserved id, or name its verdict in the closing report at Assemble step 3.

**F19 — cosmetic — Dimension 0 (packet prose, not the shipped file) — packet:147-149 vs packet:150-156**
The rationale now holds both positions at once: line 147-149 grades 517 characters "a note rather than a failure" per D-DESC-7b, while line 150-153 justifies dropping the eight verdict names because spelling them out "pushed every draft to 534-622, over the ≤500 target". Under the grading the packet now states, 534 was never a failure either. Not shipped text and not a rework ground; flagged so the record does not carry a self-cancelling justification forward as precedent. The trade itself stays cleared per SBS-GATE-1 F14.

## FREE TOKEN CUTS

The shipped file is at its floor — 140 body lines after four cuts already taken. One clean cut found:

- **packet:231-232**, delete verbatim (the wrap falls mid-sentence):

      They and the target are the evidence set for an
  `independent review this skill does not run.`

  It duplicates the operative instruction at packet:347-348 ("Hand off: the draft, the ledger and the target are the evidence set for an independent review. Name them; do not run it."). Deleting leaves the OUT line complete at "…at paths named before the walk starts." The file already spends its one sanctioned premium-slot repetition on the NEVER-write law; this is a second law stated twice.

## STILL BLOCKING

none. F7 remains true and unfixed — `skills/efficient-md/SKILL.md:9-10` still says "do that directly, no skill", which P1 falsifies the moment it ships — but the defect lives in efficient-md's bytes, not P1's. P1's new S3 is self-contained and does not depend on efficient-md's text, so P1 clears on its own. One note for the caller, not a P1 ground: the rework removed P1's only by-name mention of efficient-md from the description, so the stale claim in efficient-md is now the only surviving cross-reference between the two, and it points the wrong way.

## SPEC-LEVEL

One non-blocking note, new since SBS-GATE-1 and touching no §12 decision. P1 now deliberately diverges from `spec.md:56` ("HOLD … must be resolved before the Arrange step") in favour of "resolved with the user at Arrange, before the draft is assembled" (packet:254). The divergence is correct — `spec.md:159` makes "Resolve every HOLD" step 3 *of* Arrange, so §3 and §6.4 contradict each other — but the spec text stays wrong and will mislead the next reader of the binding artifact. P1 needs no change for it.

## CHECKED-CLEAN

- **Dimension 0 (file hygiene)** — re-checked: the rework changed bytes. Fences at packet:206/361 unambiguous; 154 lines extracted; frontmatter opens and closes at block lines 1 and 14; no residue, truncation, or duplicated block; the ledger specimen at packet:340-343 is indented 7 spaces, correct for a code block inside a numbered item.
- **Dimension 1 (spec fidelity)** — re-checked: the fold audit required a full re-walk. Every §§2-9 element present and uncontradicted; the §6.2 exemplar byte-matches spec.md:118-123. One deliberate divergence, filed under SPEC-LEVEL.
- **Dimension 2, name rules (D-NAME-1..4)** — inherited from SBS-GATE-1; `name` unchanged and `skills/section-by-section/` still does not exist.
- **Dimension 2, description slots** — re-checked: the description was rewritten. S1/S2/S3/S4 in order; measured **517 characters** (510 + 7 joining spaces), the packet's count confirmed — D-DESC-7a clear, D-DESC-7b a NOTE. D-DESC-1/2/4/5/6/8/9 clean. D-DESC-3 clears at its weakest admissible grade: "that is a separate formatting pass" names a disposition in kind, not a neighbour, which §3's own carve-out permits ("only a redirect naming neither a neighbour nor a disposition is a defect") — it is not a bare prohibition.
- **Dimension 2, partition (D-PART-1/2/3)** — re-run as instructed, void inheritance. I enumerated 11 `agents/*.md`, 5 `skills/*/SKILL.md` and 3 `.claude/skills/*/SKILL.md` myself and read every description. The S1 discriminator survived intact — "with the user, who closes each … ONE existing … producing a draft and a verdict ledger" — so the positive partition against `efficient-md`, `executor-smart`, `executor-judge`, `review-agent` and `author-agent` holds on P1's side without leaning on any negative clause. No keyword monopoly: "review", "section", "ledger", "verdict", "draft", "instruction file" all appear in sibling descriptions. No uncovered shape opened by the rewrite — the residency-shaping shape remains covered by efficient-md's own S1.
- **Dimension 3 (normative coherence)** — re-checked: four premium-slot laws were rewritten. F16 and F18 are the findings; no other contradicting pair.
- **Dimension 4(a) blank-context** — re-run as instructed. An agent holding only this file runs Open 1-5, the Walk's five tests, the proposal shape, closure with the row, the HOLD/SPLIT/reopen rules, Description last, Arrange 1-5, Assemble 1-4, and the Prohibitions, end to end, with no reference it cannot reach — the sole external citation is guarded with a fallback. The only stall on the path is F16.
- **Dimension 4(b)** — NOT EXECUTED; the accepted contract declaration stands, unaffected by the rework.
- **Dimension 4(c) trigger shapes** — inherited from SBS-GATE-1; S2's "grown, drifted, or misbehaved" is byte-unchanged.
- **Dimension 5 (obligation weakness)** — re-checked: F9's fold is the whole subject. F17 is the finding.
- **Dimension 6 (doc coherence)** — inherited from SBS-GATE-1 for the P2/P3 anchors, which I did not re-rule. F7 and F12 remain the two stale by-name references, both escalated.
- **Dimension 7 (decoupling)** — re-checked: the F4 fold is its subject. The guard matches the house form at `.claude/skills/author-agent/SKILL.md:72`; the fallback bounds the arrangement on the single-skill install path; no runtime tool identifier, settings key, or API in the body — a sweep of the extracted block for `author-agent|review-agent|executor-|advisor-mode|.claude` returns nothing, and `efficient-md` appears once, guarded.
- **Dimension 8** — excused in its checklist sense per the accepted declaration; the WARM substitute re-run: **154 lines** (14 frontmatter, 140 body) against spec §9's "~150". Within tolerance at 2.7% over an approximate ceiling, and no `references/` fork is owed — spec.md:206-207 triggers that fork on the warm ceiling (~500), not on 150.
- **Dimension 9 (routing edges)** — re-checked because the description changed: `grep -rn 'section-by-section'` across the repo, excluding `docs/section-by-section/`, returns nothing. NOT EXECUTED stands by its own rule.

## NOT EXECUTED

- **Dimension 9** — NOT EXECUTED by checklist L236's own rule: no router in the live tree names this hand or its class. Verified by repo-wide grep, not assumed.
- **Dimension 4(b)** — not applicable: a skill has no agent envelope and no MODE/STATUS return contract to matrix. Inherited declaration, accepted at SBS-GATE-1.
- **P2 and P3** — out of scope by dispatch; ruled APPLY at SBS-GATE-1 and byte-unchanged. Not re-ruled, not re-verified.
- **A mechanical old-vs-new diff of P1** — impossible: both leftover copies in the scratchpad are post-rework and byte-identical to the packet block. The "nothing quietly rewritten" conclusion rests on the spec re-walk and the prior ruling's quotes instead, and is stated at that strength.

Relevant paths: `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/759469df-44b7-4c84-b7b6-ec8ace8db919/scratchpad/section-by-section-packet.md`; `/Users/harishamutha/maddog-skills/docs/section-by-section/spec.md`; `/Users/harishamutha/maddog-skills/skills/efficient-md/SKILL.md`; `/Users/harishamutha/maddog-skills/.claude/skills/author-agent/SKILL.md`.
