# executor-smart dispatch census — 2026-08-13 to 2026-09-09 (162 dispatches, classified against the eight pre-schema modes)

**1. Corpus.** 162 dispatches to `(maddog:)?executor-smart`, 2026-08-13T15:45 to 2026-09-09T15:57 (the 162nd is the census dispatch itself).

**2. Counts.**

| mode | single | as part of multi-kind | share % of 162 |
|---|---|---|---|
| AUTHOR | 66 | 3 | 42.6 |
| FIX | 26 | 12 | 23.5 |
| CHOREOGRAPH | 22 | 11 | 20.4 |
| BUILD | 17 | 2 | 11.7 |
| REVIEW | 7 | 0 | 4.3 |
| DIAGNOSE | 0 | 2 | 1.2 |
| PORT | 1 | 0 | 0.6 |
| DECOMPOSE | 1 | 0 | 0.6 |
| NO FIT | 7 | — | 4.3 |

Multi-kind dispatches: 15 (all two-mode pairs). Reconciliation: 140 single + 15 multi + 7 NO FIT = 162. Prompts that named a mode: 16; two named a name outside the eight (OPERATE, OVERHAUL); the other 14 agreed with the classification.

**3. Examples per mode (date | description | paraphrase).**
- BUILD: 08-13 Build the eval runner workflow | new workflow file, closed design; 08-13 Build and wire the executor-fast guard hook; 08-27 Grant Skill tool to fast and smart; 08-30 Build design-system HTML page; 08-31 Build read-hand code tasks.
- PORT: 08-15 Move review-agent skill, un-ship it | relocate skill dir, remove from marketplace.
- AUTHOR: 08-13 Author executor-fast eval fixtures; 08-14 Draft executor-lead.md rewrite; 08-24 Draft skill name/description standard; 08-31 Author executor-fast-read plan; 09-07 Author plain-english overhaul packet.
- DECOMPOSE: 08-31 Split guard fix into own plan | carve one finding cluster into its own plan file.
- FIX: 08-13 Fix delegate tiebreaker law and fixture; 08-15 Apply gate fixes to product agents; 08-27 Apply judge fixes F1 F3 F4 F6; 08-31 Remove stray untracked file, no -rf; 09-06 Fix stale Running section in evals README.
- REVIEW: 08-13 Adversarial dead-weight audit of both agents; 08-30 Review plugin descriptions from user POV; 09-05 Review conformance script against II.7; 09-06 Delta slim vs shipped executor-fast; 09-07 Review efficient-md skill.
- DIAGNOSE (only paired with FIX): 08-27 Fix eval harness agent resolution | why all 39 fixtures failed, repair; 08-31 Fix cleanup regression in guard.
- CHOREOGRAPH: 08-18 Run release ritual, open PR; 08-26 DECLARE phase for 2.8.0; 08-27 Rebase plugin-only branch onto merged 2.10.0 main; 08-27 SEAL release 2.12.0; 09-08 DECLARE: branch, changelog, version bump.

**4. NO FIT, all rows (date | description | paraphrase | uncovered verb).**
- 08-30 Draw three pixel dog heads | render logo colour candidates for user to pick | render/generate visual options
- 08-30 Draw cartoon curious dog heads | three logo takes for selection | same
- 08-30 Draw block-style maddog head (Opus) | another logo candidate | same
- 08-30 Draw full-body dog silhouette marks | silhouette candidates | same
- 08-30 Draft ASCII wordmark options | lettering candidates to pick from | same
- 08-31 Measure real resume cost from transcripts | quantify a cost claim from historical data | measure/quantify a claim
- 09-09 Census of executor-smart dispatches by mode | classify a corpus against a taxonomy | classify/survey a corpus

**5. AWKWARD FIT, all rows (date | description | mode | why it stretches).**
- 08-13 Commit and push the guard hook | CHOREOGRAPH | one git push, not a pipeline
- 08-13 Pin effort high and mark core fixtures | BUILD | a config tweak
- 08-18 Draft LinkedIn post | AUTHOR | a post is published, never executed
- 08-27 Commit work and sync branch | CHOREOGRAPH | one commit+push
- 08-27 Commit harness fixes and open PR | CHOREOGRAPH | same
- 08-30 Build design-system HTML page | BUILD | standalone page, no system it joins
- 08-30 Draft wordmark lockup and DS §3 | AUTHOR | rendered art, not executable text
- 08-30 Apply S4 subtitle band to lockup | BUILD | visual treatment to art
- 09-06 Delta slim vs shipped executor-fast | REVIEW | compares two drafts for loss
- 09-06 Delta slim vs shipped executor-fast-read | REVIEW | same

**6. Candidate classes (proposals from the census hand; the derivation decides).** RENDER — produce several concrete variants of one artifact so a person can choose (5 rows). MEASURE — establish a number or comparison from existing data to confirm or refute a claim (1 row). SURVEY — sort a corpus of prior artifacts into named categories, producing counts (1 row). Merge/drop candidates by frequency: PORT (1), DECOMPOSE (1), DIAGNOSE (0 alone). User ruling: DIAGNOSE merges into FIX; PORT and DECOMPOSE stay.

**7. Top task shapes.** Apply gate/judge/review findings to shipped files ~24; run a release-ritual phase ~21; author a packet of verbatim replacement text for a later gate ~20; build a closed-design feature into a shipped file ~16; draft or fix eval/routing fixtures ~15; revise a plan/draft after a gate blocked it ~14; commit/push/open a PR as a discrete step ~9; apply an approved decision to shipped files ~8; findings-only audit ~7; visual design candidates 5.

**8. Hygiene.** 154 of 162 carried a DONE-WHEN or acceptance string (the 8 without were release-ritual phase runs). 0 of the 161 historical dispatches asked the hand to dispatch others; a 2026-08-13 dispatch "Remove delegation from executor-smart" removed the Agent tool deliberately. User ruling 2026-09-09: the Agent grant (decision 9) stands regardless.

## Method

`grep -l` shortlist over the JSONL files, then a python pass parsing `message.content` tool_use items with `name` in (Agent, Task) and `subagent_type` matching the pattern, sorted by timestamp; classification by description plus the first ~260 characters of each prompt; two judgment calls stated by the hand: revising an unshipped packet scored AUTHOR while applying to shipped files scored FIX or BUILD, and every release-ritual phase run scored CHOREOGRAPH.
