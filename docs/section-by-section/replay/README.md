# section-by-section replay set

Built 2026-09-27 for slice 2 of `../plan-2026-09-27.md`. Each item is one
moment in a real run where the user caught something the skill's own checks
should have caught. Slice 4 replays the items against the new draft and,
as control, the main file.

## Item shape

- Heading `<session prefix>-L<catch line>`.
- `pattern` — primary pattern number from the plan; `also` — secondary ones.
- `target`, `section` — the file under review and the section as the run named it.
- `session`, `lines` — the transcript and the line numbers of the proposal and
  the catch in it. Transcripts are local only:
  `~/.claude/projects/-Users-harishamutha-maddog-skills/<session>.jsonl`.
- `context` — pattern 10 only: the earlier ruling the proposal lost.
- **Proposal** — the skill's turn the catch answers: replacement text, or the
  diagnosis that missed the defect. Verbatim, trimmed at block boundaries,
  cuts marked `[...]`.
- **Catch** — the user's words, verbatim. This is the key.

## Counts

| Pattern | File | Items |
|---|---|---|
| 1 | p01-terms-and-pointers.md | 9 |
| 2 | p02-redundancy.md | 11 |
| 3 | p03-untested-proposal-text.md | 14 |
| 4 | p04-form-fit.md | 14 |
| 5 | p05-several-verdicts.md | 3 |
| 6 | p06-two-readings.md | 4 |
| 7 | p07-concrete-test.md | 1 |
| 8 | p08-section-omits.md | 11 |
| 9 | p09-wrong-section.md | 4 |
| 10 | p10-lost-rulings.md | 1 |
| 11 | p11-intent-anchor-first.md | 1 |
| | Total | 73 |

## Gaps

- Pattern 7 (1 item), pattern 10 (1), pattern 11 (1): the transcripts hold
  only one user catch each. The plan estimated 4 and 2 for patterns 7 and 10.
- Weak fit: `01c6d363-L1268` sits under pattern 8; the defect is a coherence
  hit the run argued away, which no pattern names exactly.

## Left out

- Executor-family catches: byte-identical text across executor files, moves
  into or out of the shared constitution, family-law neutrality, matching
  another tier's shape. 137dd3e7 L1038 L1178 L1213 L1273 L1286; babf14f7
  L126 L166 L203; d8a02f04 L503 L517 L774 L1558 L1573; ec3c9100 L163 L198
  L336; f09ade50 L141 L235 L241 L247 L295 L301 L997 L1008.
- Catches on a Judge's or a probe run's finding rather than the skill's own
  turn (e.g. ec3c9100 L1070 L2141), and turns where an agent played the user
  (d8a02f04 after L963).
- Two catches fit no pattern, both d8a02f04: L676 "Does 'git push' requires
  judge's verdict? - stressing the law" (a new rule's scope too broad) and
  L693 "Now issue the git operation creeeped into the core law it" (tool
  vocabulary in a general law).
