# section-by-section 3.4 — state

Updated 2026-09-27. Branch `claude/section-by-section-3-4`, worktree
`~/maddog-skills-sbs`, from main `dc08424`. Plan: `plan-2026-09-27.md`
(decisions D1–D6, slices 1–5). Replay set: `replay/` (73 items, 11 patterns).

## Done

- Slice 1 — plan committed (`d87fdd8`).
- Slice 2 — replay set committed (`b122aec`). Gaps: patterns 7, 10, 11 hold
  one user catch each. Two catches fit no pattern (see `replay/README.md`).

## Next: slice 3, the review run

Runs in the main conversation; the user closes every section. Post the Start
message below as the skill's setup message, then wait for the user to:
confirm or correct the intent anchor, close the map, name the scope (whole
file, or only the sections the plan changes), and answer the one question.
Draft and ledger go in the new session's scratchpad.

After Assembly: a hand applies the draft to `skills/section-by-section/SKILL.md`
on this branch, then slices 4–5 (replay test, spec, release). The user merges.

## Open for slice 4

The replay set does not fit `tests/harness/` (still unmerged, on
`claude/advisor-mode-framework-v2jhtw`): that harness scores an exact
expected hand; a replay item needs a judged match between the model's check
output and the recorded catch. Choose: add a case type there, or a small
runner here.

## Start message (drafted, not yet posted)

**Intent anchor (proposed).** This file makes an agent walk one instruction
file section by section with the user. For each section the agent proposes
verdicts and tested replacement text. Only what the user closes goes into a
draft and a ledger; the target is never edited. Per O11, give your own
one-line view first; yours wins where they differ.

**Section map** — target `skills/section-by-section/SKILL.md` (268 lines):

- DESC — frontmatter description (L3–10)
- S1 — Opening; "exactly one verdict" (L15–17)
- S2 — Closure law (L19–21)
- S3 — Progressive disclosure law (L23–24)
- S4 — Tested-text law and `Tested:` block (L26–36)
- S5 — Inputs and outputs (L38–43)
- S6 — Start: read whole, one setup message, wait (L45–50)
- S7 — Start: intent anchor (L52–54)
- S8 — Start: section map and review scope (L55–61)
- S9 — Start: draft and ledger paths (L62–63)
- S10 — Start: the one question, O-ids (L64–66)
- S11 — Start: when asking is required (L68–71)
- S12 — Markers: UNREVIEWED, GAP, HOLD (L73–81)
- S13 — Section loop and diagram (L83–93)
- S14 — Diagnose: Elsewhere, first match, Also line (L95–102)
- S15 — Redundancy (L104–109)
- S16 — Responsibility (L111–119)
- S17 — Coherence (L121–127)
- S18 — Correctness (L129–134)
- S19 — Clarity + KEEP fallback (L136–145)
- S20 — Discuss: template, coherence pair (L147–163)
- S21 — Settle: five kinds of reply (L165–177)
- S22 — Write: text, shorter-line rule, MERGE/MOVE (L179–189)
- S23 — Record: ledger (L191–212)
- S24 — Assembly opening (L214–225)
- S25 — Assembly 1: HOLD (L227–230)
- S26 — Assembly 2: GAP (L231–232)
- S27 — Assembly 3: cross-section axes (L234–239)
- S28 — Assembly 4: terminology (L240)
- S29 — Assembly 5: MOVE, MERGE, SPLIT (L242–247)
- S30 — Assembly 6: verify outline, description (L248–254)
- S31 — Assembly 7: compose (L255–259)
- S32 — Hand-off (L261–264)
- S33 — Prohibitions (L266–268)

**Observations** (examples in `replay/`):

- O1 — terms and pointers don't resolve (9 items)
- O2 — redundancy missed, incl. a definition the word already carries (11)
- O3 — proposed text not really tested; compression hurt readability (14)
- O4 — form doesn't fit content (14)
- O5 — several verdicts apply, skill gives one (3)
- O6 — a sentence admits two readings (4)
- O7 — judgment rule where a concrete test exists (1)
- O8 — a section omits what its own question needs (11)
- O9 — a sentence in the wrong section (4)
- O10 — mid-run rulings lost (1)
- O11 — anchor drawn from the file before asking the user (1)
- O12–O17 — plan decisions D1–D6

**The one question.** In your own words, what should this file make an agent
do? Any observations beyond O1–O17? Any files the target relies on that the
redundancy and term checks should read (D5)?
