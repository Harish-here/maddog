VERDICT: FAIL — P1 goes back for rework; P2 and P3 clear.

## VERDICT-ID

`SBS-GATE-1`

## RULING ON THE DECLARED CONTRACT

- **ACCEPTED** — Dimension 2's five-slot executor-family shape (checklist L112-142) excluded: that block is headed "every executor-family description" and `description-standard.md` §8 confirms it binds `agents/executor-*.md`. No agent is authored.
- **ACCEPTED** — `agent-template.md` excluded entirely: its own line 2 scopes it to "authoring agent files in this repo." The declaration is correct.
- **ACCEPTED** — Dimension 4(b) mode-output × return-field matrix excluded: the matrix is defined over an agent envelope with `STATUS:`/`MODE:` fields; a `SKILL.md` has neither.
- **ACCEPTED** — Dimension 8 excused in its checklist sense: D8's subject is "always-resident text only" (checklist L214); the body is per-invocation and `description-standard.md` §5 puts the description out of context under `disable-model-invocation: true`. The WARM substitute was in fact run and the file measures under ceiling (see NOTES).
- **ACCEPTED** — Dimension 9 NOT EXECUTED: I enumerated the routers myself; no agent or skill in the live tree names `section-by-section` or a class it is bound to, and P2/P3 add no router edge. NOT EXECUTED is the correct result, not a skipped check.
- **REJECTED** — the packet's Partition (a) claim that "efficient-md's own positive side ... is untouched; nothing in P1 weakens its shape" (packet:111-113). It is touched, on efficient-md's S3, not its S1. See F7. This is the one wrongly-excused piece of analysis and it is load-bearing.

## PER ITEM

- **P1 — REWORK.** Six load-bearing defects: three spec elements dropped in rendering (F1, F2, F6) and three silent-failure paths where an agent proceeds without the user or destroys an output (F3, F5, F8), plus an unguarded citation the file's own prohibition forbids (F4).
- **P2 — APPLY**, sequenced after P1. Both anchors verified byte-exact and unique as whole lines at the stated line numbers; wrap, indentation and bullet form match the live file; DESIGN.md §7 "one line per shipped thing" satisfied.
- **P3 — APPLY**, sequenced after P1. `  "version": "3.0.1",` matches `plugin.json:3` byte-exact including the two leading spaces; the string is unique in the file; `marketplace.json` carries no version field, so no second bump is owed.

## FINDINGS

**F1 — load-bearing — Dimension 1 — packet:174-175 (vs spec.md:32)**
The Contract's IN line admits only "a `SKILL.md` or an agent definition file." Spec §2 places a `references/` file out of scope *"unless the user names it as the target of its own run."* That carve-out did not land. Failure: the user invokes the skill on `skills/efficient-md/references/warm.md`; the agent reads IN, sees a file that is neither a SKILL.md nor an agent definition, and refuses a run the spec explicitly permits. Fix is an addition to the IN line, not a spec change.

**F2 — load-bearing — Dimension 1 — packet:191 (vs spec.md:48)**
Spec's MOVE row carries two user-sentences: `"Right rule, wrong place." / "Keep it, but out of the body."` P1 keeps only the first. The body's own line 182 says that column "is the test for choosing between them," so a dropped sentence is a dropped test. Failure: a 40-line worked example the user wants moved into `references/` runs the tests — removal no, duplicate no, format matches — and lands on WEIGHT, "needed but longer than its instruction → COMPRESS." The agent proposes COMPRESS and destroys the example, where spec §10's own validation list requires "heavy example → MOVE to a references file."

**F3 — load-bearing — Dimension 3/4 — packet:257-261**
"Description last" is the only review block in the file with no closure sentence. The Walk's closure law ("Only the user's closure counts," packet:251) is scoped to "each section in file order"; the description is explicitly *excluded* from the section map and named "the anchor during the walk." The Prohibition "Never close a section without the user" (packet:296) does not reach it, because the body has just told the reader the description is not a section. Failure: the agent tests the description, judges it drifted, and writes a rewritten HOT description into the draft on its own authority — the single highest-consequence line in the target file, closed without the user. This is exactly the silent failure the skill exists to prevent.

**F4 — load-bearing — Dimension 7 (and 3, 4a) — packet:270 and packet:162, against `skills/efficient-md/SKILL.md:53-59`**
Two unconditional citations of `efficient-md`: Arrange step 2 ("the whole under the warm ceiling the efficient-md skill states for skill bodies") and description S3 ("that is efficient-md"). The efficient-md SHIP RULE requires a shipped file to "replace unconditional citations of session-scoped or absent artifacts with self-contained statements or in-repo pointers; a citation guarded by an existence check is the sanctioned fallback." P1's own Prohibition 4 (packet:298-300) states the same law about itself — so the file contradicts its own premium-slot prohibition. The repo's house form is the guard: `.claude/skills/author-agent/SKILL.md:72` ("Where the efficient-md skill is installed…") and `skills/mine-session/SKILL.md` ("…if one is installed"). Failure on the `npx skills add` path where a user takes this skill without efficient-md: Arrange step 2 names a ceiling the agent has no path to read (checklist ground-truth class 8), so it silently skips the ceiling clause and hands back an over-weight arrangement; and the description's only neighbour-redirect points at a skill that is not there.

**F5 — load-bearing — Dimension 3 — packet:277-278 and packet:295**
Assemble step 1: "Where a MOVE targets another file, write that file too, beside the draft, never at any existing path." No naming rule is given. Failure: the target is `skills/foo/SKILL.md`, a MOVE sends S7 to `skills/bar/SKILL.md`, and both drafts are written "beside the draft" under the same basename — the second write silently destroys the pass's primary output. Separately, the premium bottom slot protects only one path: "Never write to the target path." The MOVE-destination file is not "the target," so an agent re-reading the Prohibitions at the end of a long pass has no bottom-slot rule stopping it writing the merged text straight into the live `skills/bar/SKILL.md`. Two repairs, both valid, caller's choice: give the MOVE-destination draft a derived name in Assemble step 1, or widen the Prohibition to every existing path — I choose neither.

**F6 — load-bearing — Dimension 1/4 — packet:175, 206-207, 243 (vs spec.md:62)**
Spec §4 marks Observations **"(optional)."** P1's Contract states them as part of IN without qualification, and Open step 2 makes citation mandatory: "Every proposal cites the ids supporting it." The sole canonical exemplar ends "Verdict: MERGE into S9. Evidence: O1." Failure: the user runs the skill on a file that has not misbehaved and supplies no observations; every proposal now carries an `Evidence:` field with nothing legal to put in it, and the agent either invents an observation id to fill the exemplar's shape or blocks at Open step 2 on an input the spec calls optional.

**F7 — load-bearing — Dimension 6/2 — `skills/efficient-md/SKILL.md:9-10`**
efficient-md's S3 reads: *"Not for reviewing or rendering a verdict on text that already exists — do that directly, no skill."* Once P1 ships, that disposition is false — there is now a skill for precisely that. The packet asserts the opposite at packet:111-113 and proposes no third edit. Failure: a maintainer or a later router reading efficient-md's menu entry is told to do the job directly and never learns `section-by-section` exists — the D-DESC-3 destination is a stale claim in a HOT surface. Two valid repairs, caller's decision: add a fourth packet item editing efficient-md's S3, or record an accepted decision that `disable-model-invocation: true` keeps the model out of contention and the staleness is human-facing only. I choose neither. Note this exceeds spec §11's shipping list but touches no §12 decision.

**F8 — load-bearing — Dimension 3/5 — packet:199 vs packet:266-273**
The marker table says HOLD "must be resolved before Arrange"; Arrange step 3 *is* "Resolve every HOLD" — a step **of** Arrange. Nothing in the Walk sends the agent back to open HOLDs. Worse, Arrange steps 1-4 read as the skill's own work and the only user sentence in the block is step 5, scoped to "the arrangement," not to the held sections' verdicts. Failure: the agent reaches Arrange with three HOLDs, reads step 3 as its own task, assigns the three verdicts itself, and the user closes only the ordering — three sections closed without the user, through the one closure path with no user in the sentence.

**F9 — load-bearing — Dimension 5 — packet:251**
Spec §6.2 makes "Write the ledger row at every closure" a numbered step (4 of 4). P1 demotes it to the trailing clause of a prose paragraph. Skipping it is entirely silent: the final ledger at Assemble step 2 is written anyway, so nothing downstream detects that no row existed mid-pass. Converting structure available: artifact-first ordering — the next section's proposal may not be posted until the previous row is written; the body has no such structure today.

**F10 — load-bearing — Dimension 3/5 — packet:302-303 vs packet:204 and 216-217**
Open gates judgment on step 5 closing ("Nothing is judged before step 5 closes"), but the premium-slot Prohibition gates only on two of the five: "Never judge a section before the intent anchor and the section map are confirmed." Naming the draft and ledger paths (Open step 5) is unprotected. Failure: the agent confirms the section map, walks S1, closes it, and only then discovers no ledger path was ever named — the first row has nowhere to go and is written to an invented path or lost.

**F11 — cosmetic — Dimension 1/0 — packet:284-286**
The ledger specimen is introduced as "a markdown table" but carries no header separator row, unlike the file's own verdict table at packet:185 which has `|---|---|---|`. Failure: the ledger file the user opens renders as a wall of pipes in every markdown viewer. Spec §7 carries the same omission; the fix is one line in the packet, not a spec change.

**F12 — cosmetic — Dimension 6 — `skills.sh.json:4-20`**
All five shipped skills are grouped; the packet updates no grouping. With `"notGrouped": "bottom"`, `section-by-section` renders ungrouped at the bottom of the skills.sh listing while every other maddog skill sits in a curated group. README §Releasing classifies `skills.sh.json` as DOCS, so this is a cheap addition, not a gate.

**F13 — cosmetic — Dimension 4(c) — packet:160-161 with packet:174**
"drifted" as a trigger names cross-file drift as naturally as intra-file drift, but the WEIGHT test only handles "Two sections that contradict each other" *within* the file, and IN fixes "one target file per run." Failure: a user whose real problem is agent A contradicting agent B invokes the ritual on A, walks it, and closes clean — the defect is untouched. Mitigated but not eliminated by the IN line and Prohibition 5, which the agent will at least state.

**F14 — unverified assumption — Dimension 2 — packet:99-105**
The eight verdict names were dropped to hold ≤500 characters. The trade itself survives: at `disable-model-invocation: true` the description never enters routing context, so the vocabulary costs nothing at the routing edge, and "one of eight verdicts" is enough for a human picking from the `/` menu. But the stated justification misreads the standard — D-DESC-7b grades **over 500 as a NOTE, not a failure**, and §1's truncation rule bites at 1,536, nowhere near 494. The trade was made against a ceiling that was never binding. Not a rework ground; the reasoning should not be carried forward as precedent.

**F15 — unverified assumption — Dimension 7 — packet:216-217**
"Default: the session's scratch directory" has no degraded fallback for a runtime that has none — the `npx skills add` path installs "into other agent runtimes" (README:76-80). "The user may name a durable path" is a user option, not a fallback for absence. Failure: on such a runtime the agent invents a path; the NEVER law still holds, so the blast radius is confusion, not destruction.

## SPEC-LEVEL

None. Every finding is repairable in the packet text without touching `spec.md` or a §12 decision. F1, F2, F5, F8, F10 and F11 correspond to places where the spec carries the same gap or the same omission, but in each case the fix is a rendering change the spec permits, not a reopened decision. F7 exceeds spec §11's shipping list; §12 holds no decision about efficient-md's description, so it stays in bounds.

## CHECKED-CLEAN

- **Dimension 0 (file hygiene)** — read packet:154-303 as bytes. Frontmatter opens at 154 and closes at 167; no tool-call or XML residue; no truncated rule; no duplicated block. The shipped file contains no fences at all (indented blocks throughout), so extraction between the four-backtick fences at packet:153/304 is unambiguous. `argument-hint: [goal]`-style unquoted flow sequence matches the live precedent in `skills/advisor-mode/SKILL.md`.
- **Dimension 2, name rules** — D-NAME-1 through D-NAME-4 all pass: `section-by-section` is 18 chars, matches `^[a-z0-9]+(-[a-z0-9]+)*$`, equals the directory name in the target path (directory does not yet exist — confirmed), bare domain phrase, no generic-only token, no plugin prefix.
- **Dimension 2, description slots** — S1/S2/S3/S4 present in order; no procedure text, no first/second person, no XML, no marketing adjectives, no reference to the body; 494 characters measured (my count agrees with the author's within one newline), inside both budgets. D-DESC-1/2/4/5/6/7a/7b/9 clean.
- **Dimension 2, partition (D-PART-1/2/3)** — I enumerated all 11 `agents/*.md`, all 5 `skills/*/SKILL.md` and all 3 `.claude/skills/*/SKILL.md` myself rather than taking the packet's list, and read the load-bearing competitors at source. No keyword monopoly: "review", "section", "ledger", "verdict", "draft" all appear in neighbouring descriptions. `executor-smart` ("ONE delegated task … inside a fixed boundary … review against explicit criteria") and `executor-judge` ("renders independent acceptance verdicts … at a gate") are partitioned by a positive discriminator on both sides — they are one-shot delegated hands; P1 is "with the user, who closes each." `plain-english` and `mine-session` do not contend. The efficient-md double-match is real but sits on efficient-md's side (F7), not P1's. No uncovered shape found.
- **Dimension 7, invariant compliance** — swept the whole body: no occurrence of `author-agent`, `review-agent`, `executor-*`, `advisor-mode`, or any repo-internal tooling; no runtime tool identifier, settings key, or API in prose. Spec §6.5's "In this repo it is the author-agent loop" was correctly dropped at packet:290-291. Frontmatter keys are adapter surface per CLAUDE.md §Invariants. Only `efficient-md` is cited, and that is the F4 issue, not an invariant breach.
- **Dimension 1, body order** — spec §9's seven-element order (Contract+verdict table, Open, Walk, Description last, Arrange, Assemble and hand off, Prohibitions) lands exactly, in order, at packet:172 / 202 / 219 / 257 / 264 / 275 / 293. Frontmatter keys match spec §9. All six spec §8 prohibitions present. Spec §5's five tests present in order with the RESHAPE precedence rule intact.
- **Dimension 6, anchor verification** — `grep -n -x -F` confirms all six P2 anchor lines match as whole lines at README.md:166,167,168,172,173,174 and `plugin.json:3`, byte-for-byte including indentation and the `→`/`—`/`'` characters. `marketplace.json` carries no version and enumerates no skills — no update owed. `CLAUDE.md`, `PHILOSOPHY.md`, `DESIGN.md`, `CONTRIBUTING.md` and README §Architecture enumerate no shipped-skill set, so none goes stale. F7 and F12 are the only two stale by-name references found.
- **Dimension 9** — NOT EXECUTED, correctly: no router in the live tree names this hand or its class.

## NOT EXECUTED

- **Dimension 9 (routing edges)** — NOT EXECUTED by its own rule (checklist L236: "NOT EXECUTED: no router names this hand or its class"), not by omission. Verified against `skills/advisor-mode/SKILL.md`, all `agents/*.md`, and both plugin manifests.

## DELEGATION LOG

- `executor-fast-read` — asked for a verbatim frontmatter inventory of all `agents/*.md`, all `skills/*/SKILL.md` and all `.claude/skills/*/SKILL.md`, with `description:` line numbers, `references/` filenames, and directory listings to confirm coverage. Returned 11 + 5 + 3 files with complete frontmatter blocks. I re-verified every load-bearing quote at source before using it: efficient-md's S3 and the description-standard citations by direct read, the plain-english and mine-session S3 lines by grep.

## NOTES

- **The dispatch's "~157 lines" premise does not hold.** Measured: `sed -n '154,303p' | wc -l` = **150** lines total, of which frontmatter is 14 and the body proper is **136**. The file is inside spec §9's "~150 lines" ceiling with room to spare. No cut is owed, and the packet's decision not to fork a `references/` file is correct — spec §9 permits that fork only on an actual breach.
- The packet's residency-class table, apply ordering (P1 before P2/P3), and its reading of `disable-model-invocation: true` against description-standard §5 are all sound and I took no issue with them.
- Pre-existing, not this packet's ground: `.claude/skills/release/references/release-model.md:81` (E13) still counts "13 shipped surfaces" and names an eval-fixture debt for a harness removed in 3.0.1. Already stale before this change; flagging only so it is not mistaken for packet fallout.
- `CHANGELOG.md` was treated as out of scope per the dispatcher's decision and is not a rework ground.
- This gate carried no prior verdict and was judged fresh.
- Relevant paths: the packet at `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/759469df-44b7-4c84-b7b6-ec8ace8db919/scratchpad/section-by-section-packet.md`; `/Users/harishamutha/maddog-skills/docs/section-by-section/spec.md`; `/Users/harishamutha/maddog-skills/skills/efficient-md/SKILL.md`; `/Users/harishamutha/maddog-skills/skills.sh.json`; `/Users/harishamutha/maddog-skills/README.md`; `/Users/harishamutha/maddog-skills/.claude-plugin/plugin.json`.
