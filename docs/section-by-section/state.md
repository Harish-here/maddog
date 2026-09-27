# section-by-section 3.4 — state

Updated 2026-09-27. Branch `claude/section-by-section-3-4`, worktree
`~/maddog-skills-sbs`, from main `dc08424`. Plan: `plan-2026-09-27.md`
(decisions D1–D6, slices 1–5). Replay set: `replay/` (73 items, 11 patterns).

## Done

- Slice 1 — plan committed (`d87fdd8`).
- Slice 2 — replay set committed (`b122aec`). Gaps: patterns 7, 10, 11 hold
  one user catch each. Two catches fit no pattern (see `replay/README.md`).
- Slice 3 done 2026-09-27: the section-by-section review of SKILL.md ran with
  the user closing every section, a judge gate (PASS WITH FIXES, all fixes
  closed), and the result applied in this commit. The draft and ledger were
  session-scratch only and were not kept (user's decision). Rulings made
  during the run, for the spec update in slice 5: R1 several verdicts per
  section; R2 hunt for drops; R3/R4 ten-check table, one row per check,
  pointers and names separate; R5 correctness only on a diagnosis, deletions
  only on proposed text; R6 one placement verdict, a section needing two is a
  SPLIT (bends plan D2); R7 500-line ceiling on every produced file. Also:
  fixed row order with a nine-row count replaced "findings first" (bends D1);
  the plan's "a fix targets the rule's intent" line was dropped.

## Next

Slice 4 (replay test; keep the existing "Open for slice 4" section as is),
then slice 5 (update `docs/section-by-section/spec.md` to match, then the
release skill). The user merges.

## Open for slice 4

The replay set does not fit `tests/harness/` (still unmerged, on
`claude/advisor-mode-framework-v2jhtw`): that harness scores an exact
expected hand; a replay item needs a judged match between the model's check
output and the recorded catch. Choose: add a case type there, or a small
runner here.
