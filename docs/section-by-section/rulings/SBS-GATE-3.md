VERDICT-ID: SBS-GATE-3

## ROUND-2 FOLD AUDIT

- **F16 — folded exactly.** The clause is gone from both premium slots: `packet:266` reads `NEVER — never write to the target path. Every change lands in the draft.` and `packet:386` reads `- Never write to the target path.` A repo-wide grep of the block for `existing path` returns exactly one hit, `packet:367`, inside the MOVE-write sentence. Assemble step 1 still carries both halves of F5's repair — `never at any existing path` scoped to the MOVE write (`packet:367`) and the derived-name rule (`packet:368`). The F16 deadlock is dead: nothing now forbids the ledger write at `packet:338-339`, `packet:350`, `packet:369-370`. Protection intact, but single-sited — the MOVE-destination rule now lives at exactly one place, with no premium-slot backstop. That is the shape of repair (a), which SBS-GATE-2 named as valid, not a defect in these bytes.
- **F17 — folded exactly, reaches all three cases.** Arrange step 5 (`packet:362`) gates on "every closure above has its ledger row"; the description's closure (`packet:350`) and the HOLD closures at Arrange step 3 (`packet:360`) are both *above* it in file order, and the last body section's closure is above it too. Assemble step 2 (`packet:371`) repeats the gate with "HOLDs included" as a backstop. No contradiction with Assemble step 1: step 1 writes the draft and no ledger row, so a late-firing gate corrupts nothing. Wording wrinkle filed as F20.
- **F18 — folded exactly.** `packet:350`: "its closure writes a ledger row under the reserved id `DESC`", stated at the closure itself — the point of action. No collision: the id namespaces in the file are `S1..Sn` / `S3a` (`packet:299`) and `O1..On` (`packet:294`); `DESC` collides with neither, and the file was never single-namespace, so nothing reads wrong from a non-`S` id. The specimen is unchanged and shows only row *shapes*; "one row per section" already admits non-section rows, since the GAP marker at `packet:287` explicitly defines "a ledger row with no section". DESC coexists.
- **The free cut — folded exactly.** OUT now ends at `packet:264-265` "…at paths named before the walk starts." and still states what OUT is (a draft and a verdict ledger, at named paths). The deleted instruction survives operative at Assemble step 4, `packet:381-382`.
- **No fifth shipped-byte change.** Every line citation in SBS-GATE-2 maps onto the current file with an offset that shifts only at the four fold sites, by exactly the expected amount: +34 (fence move) → +32 after the two Contract deletions (GATE-2's 246→278, 254→286, 269→301, 306→338, 313→345) → +33 after the DESC line (327→360, 334→367, 335→368) → +34 after the Assemble clause (341→375, 347→381, 352→386, 359→393). −2 then +1+1 nets zero, and the file measures 154 lines in both rounds. The rewrap lost no words: the NEVER line went 2→1 lines and the OUT line 3→2, exactly the width the deleted text occupied. Description re-measured at 517 characters — byte-unchanged.

## P1 VERDICT

**APPLY** — the two blocking findings of SBS-GATE-2 are repaired at their named sites, the repairs reinforce rather than undercut each other (F17's gates are what make F18's DESC row non-skippable), and no regression, over-fold, or fifth edit survives the arithmetic and fragment checks.

## FINDINGS

- **F20 — cosmetic — Dimension 3/5 — packet:371.** The Assemble-side gate is worded as a precondition on entering the section ("before this section starts") but sits *inside* it, at step 2. An agent reading literally has already executed step 1 by the time it meets a rule that claims to precede the section. Failure: the agent writes the draft, reaches step 2, finds a resolved-HOLD row missing, and discovers a "precondition" it could no longer have satisfied in order. Harmless in practice — step 1 writes nothing the missing row corrupts, and the remedy (write the row) is still available. Does not block APPLY. Not a regression; the clause is new but the misfit is in wording, not effect.
- **F21 — cosmetic — Dimension 3 — packet:377 vs packet:287.** The specimen's GAP row carries id `S7` and title `Escalation`, while the marker table defines GAP as "a ledger row with no section". Failure: a user copies the shape, gives a GAP an `S` id for a section that does not exist, and the hand-off's GAP list points at a phantom section. Pre-existing and mirrored verbatim from `spec.md:183` against `spec.md:57`; both prior gates examined this specimen (SBS-GATE-1 F11, SBS-GATE-2's column check) and neither filed it. Recorded because the check ran — **not rework grounds and not a round-2 regression**; caller's note.
- **F22 — unverified assumption — Dimension 0 — packet (whole P1 block).** No pre-round-2 copy of P1 survives in the scratchpad (the directory holds only the packet and the two rulings), so a mechanical old-vs-new diff was again impossible. "No fifth change" rests on three independent checks — the offset arithmetic above, a fragment-by-fragment match of every line SBS-GATE-2 quoted, and a full spec §§2-9 re-walk. A line-neutral, in-place word change inside a line no prior ruling quoted would escape all three. Stated at that strength, as SBS-GATE-2 stated its own.

## FREE TOKEN CUTS

none. The one candidate — Assemble step 2's gate at `packet:371`, whose coverage is fully contained in Arrange step 5's at `packet:362` — is not free: it is the backstop that catches a silently skipped Arrange step 5, and SBS-GATE-2 prescribed both sites by name. Cutting it partially unfolds F17.

## SPEC-LEVEL

- New, non-blocking, touching no §12 decision: `spec.md:183`'s ledger specimen contradicts `spec.md:57`'s GAP rule (the F21 pair). P1 mirrors the spec faithfully, so P1 needs no change; the binding artifact carries the incoherence forward to its next reader.
- `DESC` (`packet:350`) is an addition beyond spec text — §6.3 states no closure and §7 says "one row per section". It is permitted: §12 holds no decision on ledger ids or the description's row, and it is the repair SBS-GATE-2 named for F18. Recorded so the spec's silence is not mistaken for a prohibition.
- The `spec.md:56` note stands from SBS-GATE-2 and is not re-filed.

## CHECKED-CLEAN

- **Dimension 0 (hygiene)** — re-run: bytes changed. 154 lines between the four-backtick fences at packet:240/395; frontmatter opens and closes at block lines 1 and 14; no nested fences, no residue, no truncation; longest non-table line 82, in family with the file's existing 79-81.
- **Dimension 1 (spec fidelity)** — re-run: the fold audit required it. All §§2-9 elements present; the §6.2 exemplar is byte-identical to `spec.md:118-122` (`diff` empty); the ledger specimen equals `spec.md:181-183` plus the F11 separator; all six §8 prohibitions at packet:386-394; §9's seven-element order at packet:259/289/304/345/352/364/384.
- **Dimension 2, name rules (D-NAME-1..4)** — inherited from SBS-GATE-1; `name` unchanged, `skills/section-by-section/` still absent.
- **Dimension 2, description slots and budgets** — inherited from SBS-GATE-2, with byte-identity confirmed rather than assumed: re-measured 517 characters, matching its count exactly.
- **Dimension 2, partition (D-PART-1/2/3)** — inherited from SBS-GATE-2; the description is byte-unchanged, so the S1 discriminator and the efficient-md partition stand as ruled.
- **Dimension 3 (normative coherence)** — re-run: both premium slots changed. Enumerated every write instruction in the file (packet:264, 300-302, 338-339, 350, 360-361, 366-368, 369-372) against every prohibition. No law cancels another. No path writes the target; the MOVE destination is covered at packet:367; draft and ledger paths are the user's to name. F20 and F21 are the residue.
- **Dimension 4(a) blank-context** — re-run: an agent holding only this file runs Open 1-5, the five tests, the proposal shape, closure with its row, Description last with DESC, Arrange 1-5, Assemble 1-4 and the Prohibitions with no unreachable reference and no stall. The F16 deadlock that was the sole stall at SBS-GATE-2 is gone.
- **Dimension 4(b)** — NOT EXECUTED; declaration inherited from SBS-GATE-1, unaffected.
- **Dimension 4(c) trigger shapes** — inherited from SBS-GATE-1/2; S2 byte-unchanged.
- **Dimension 5 (obligation weakness)** — re-run: round 2 added two obligations. Both are gated rather than free-standing — Arrange step 5 and Assemble step 2 each condition an action on the rows existing, and together they make F18's DESC row non-skippable (it is a closure "above" both). Skipping either is silent, but the blast radius stays lost work on a crash, exactly as SBS-GATE-2 scoped it, and this is the converting structure SBS-GATE-2 itself named.
- **Dimension 6 (doc coherence)** — inherited from SBS-GATE-1; P2/P3 out of scope and not re-ruled. F7 and F12 remain escalated.
- **Dimension 7 (decoupling)** — re-run: a sweep of the block for `author-agent|review-agent|executor-|advisor-mode|.claude|allowed-tools|permissionMode|mcp__` returns nothing; `efficient-md` appears once, at packet:359, guarded with its fallback. No runtime identifier, settings key, or API. CLAUDE.md §Invariants holds.
- **Dimension 8** — WARM substitute re-run: 154 lines (14 frontmatter, 140 body) against spec §9's "~150". Unchanged from SBS-GATE-2; no `references/` fork owed.
- **Dimension 9 (routing edges)** — inherited from SBS-GATE-2; the description is byte-unchanged, so its repo-wide grep result stands. NOT EXECUTED by its own rule.

## NOT EXECUTED

- **P2 and P3** — out of scope by dispatch; APPLY at SBS-GATE-1, byte-unchanged, not re-ruled and not re-verified.
- **Dimension 4(b)** — not applicable: a skill has no agent envelope to matrix.
- **Dimension 9** — NOT EXECUTED by checklist L236's own rule, inherited.
- **A mechanical round-1 vs round-2 diff of P1** — impossible; no pre-round-2 copy exists in the scratchpad. Substituted by the offset arithmetic, fragment matching, and spec re-walk described above. Filed as F22.

## DELEGATION LOG

none — the target is 154 lines and every check was mine to run.

Relevant paths: `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/759469df-44b7-4c84-b7b6-ec8ace8db919/scratchpad/section-by-section-packet.md`; `/Users/harishamutha/maddog-skills/docs/section-by-section/spec.md`.
