# Mode-Template Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This plan executes the repo's own gated loop: `.claude/skills/author-agent/SKILL.md` is the binding procedure wherever this plan cites it; on any conflict, the skill wins.

**Goal:** Ship multi-select mode classification, the four-slot mode template, and three law fixes into `executor-fast` and `executor-fast-read`, gated and eval-refereed. The version bump is ruled at DECLARE from release §1.2's computed recommendation — this plan pre-commits to no number.

**Architecture:** The change is instruction text, so the pipeline is the author-agent SCALED loop — model (gated 2026-09-01; findings folded; D1–D3 awaiting user ruling) → incumbent sweep → packet → gate → user approval → fast-tier apply → verify — bracketed by baseline and after eval runs, closed by the release ritual. No application code exists; validation is behavioral (CONTRIBUTING.md §Validation).

**Tech Stack:** maddog agents (executor-judge for gates, executor-fast for applies, executor-smart for fixture migration), `.claude/workflows/agent-evals.js` invoked as a Workflow run by script path (there is no runner skill in this repo), release skill, git.

**Spec:** `docs/plans/mode-template-package-model.md` — every replacement text, fixture, amendment, and rule this plan applies is defined there by section ID (M0–M7). Executors read both files. The model gate's verdict is filed at `.claude/reviews/2026-09-01-mode-template-package-model-gate.md` (local by policy) and binds later gates as precedent. Execution starts only after the user rules D1 (misroute clause + stale-fixture migration), D2 (incumbent sweep), and D3 (eval scope).

## Cost (source for the step-0 lines author-agent requires)

- Eval runs, at the runner's own ~66k tokens/fixture: full scope [D3] ≈ 27 fixtures × 2 runs ≈ 3.6M tokens (haiku-priced dispatches plus grading), plus one single-fixture run ≈ 66k. Targeted alternative ≈ 0.7M × 2.
- Judge dispatches (opus): incumbent sweep [D2] ×1, packet gate ×1, plus one re-gate per rework round; model gate already spent.
- Apply dispatches (haiku) ×3; fixture-migration authoring (sonnet) ×1.
- Covered rework rounds: whatever count the user grants at the step-0 green light; each further round is its own green light.

## Global Constraints

- Shipped bodies name capabilities, never runtime tool identifiers or settings keys (`PHILOSOPHY.md` point 5; `CLAUDE.md` §Invariants).
- Merging to main publishes; all work stays on the feature branch until the release ritual's SHIP; the user's hand is the only merge.
- Commits: conventional, scoped to the surface (`feat(executors):`, `fix(evals):`, `chore:`); no co-author or generated-with trailers.
- **Never `git add` a gitignored path** — no `-f`, ever. `evals/last-run.md` and `.claude/reviews/**` stay local by policy; after every eval run, copy `evals/last-run.md` to a dated file under `.claude/reviews/` before anything else runs (the Report phase overwrites it wholesale).
- Eval invocations: `Workflow` on scriptPath `.claude/workflows/agent-evals.js`; scope via `args` (`{agents: [...], all: true}` or `{only: [ids]}`) — default scoping is core-only and will silently skip non-core fixtures. Models are pinned inside the workflow; run prompts stay neutral.
- Fixture ids are never renumbered; cross-file moves carry `migrated_from` (`evals/README.md` §Fields).
- Every apply dispatch states verbatim: the working tree's uncommitted changes are the deliverable; git checkout, restore, stash, and clean are forbidden; DONE-WHENs describe the dispatch's own delta ("your edits touch only X"), never tree state (author-agent step 6).
- The packet is the single authority for apply dispatches — never chat memory (author-agent step 2).
- Interactive checkpoints (step-0 green light with the Cost values above; D1–D3 rulings; packet approval; release DECLARE/RULE/SHIP) stop and wait for the user; they are never inferred.
- JSON validation commands (`python3 -c …`) run from the orchestrating session, whose Bash is not scoped by `scripts/executor-guard.sh`; if delegated instead, the hand must hold Write/Edit (the guard refused the read-only judge).
- The executing session's agent registry must resolve `maddog:executor-fast-read` before any dispatch or eval run — the agent merged 2026-09-01 and registers only after a plugin reload or a fresh session. The runner's preflight aborts the whole run otherwise (observed 2026-09-01: `preflight-agent-resolution` abort).

---

### Task 0: Branch, rulings, step-0 green light

**Files:**
- Branch: `feat/mode-template-package`
- Commit: `docs/plans/mode-template-package.md`, `docs/plans/mode-template-package-model.md`

**Interfaces:**
- Consumes: the model-gate verdict (filed locally), the user's D1–D3 rulings, the Cost section above.
- Produces: the branch every later task commits to; the green-light values the Task 4 packet must open with.

- [ ] **Step 1: Confirm the user has ruled D1, D2, D3 and granted the step-0 green light with a covered rework count.** Record the three rulings and the count verbatim — the packet opens with them. If a ruling changes the model, fold it and re-gate the changed section before proceeding.

- [ ] **Step 2: Create the branch (skip if it already exists from the verdict-fold commit)**

```bash
git checkout -b feat/mode-template-package
```

- [ ] **Step 3: Commit the plan and model if not already committed**

```bash
git add docs/plans/mode-template-package.md docs/plans/mode-template-package-model.md
git commit -m "chore(plans): add mode-template-package model and plan (post model-gate fold)"
```

### Task 1: Baseline eval run (before any text changes)

**Interfaces:**
- Produces: the local baseline record for the D3-ruled scope — a first-ever recorded run of both fast suites (no fast-tier fixture has a recorded run; model M6/F13).

- [ ] **Step 1: Run the workflow at the D3-ruled scope**

Workflow on scriptPath `.claude/workflows/agent-evals.js` with `args: {agents: ["executor-fast", "executor-fast-read"], all: true}` (or the D3-ruled `only` list — identical scope must be reused at Task 8).

- [ ] **Step 2: Preserve the record immediately**

```bash
cp evals/last-run.md .claude/reviews/eval-run-2026-09-01-baseline.md
```

- [ ] **Step 3: Confirm coverage against the ruled scope** — every in-scope fixture id has a result row, or appears in the report's dropped/delegation-skipped sections. Re-run only genuinely dropped fixtures via `args.only`. Nothing is committed — run records are local by policy.

### Task 2: Composite trap fixture + schema documentation (fixture-first)

**Files:**
- Modify: `evals/executor-fast-read.json` (append fixture), `evals/README.md` (§Fields)

**Interfaces:**
- Consumes: fixture JSON and README wording from model M6, verbatim.
- Produces: `fastread-chain-01` (core=false, mode expectation in `must` where the grader can see it) and README rows for `core`, `requiresDelegation`, and chained-mode fixtures.

- [ ] **Step 1: Append the M6 fixture verbatim to the `fixtures` array**

Validate from the orchestrating session: `python3 -c "import json;json.load(open('evals/executor-fast-read.json'))"` — Expected: silent exit 0.

- [ ] **Step 2: Amend `evals/README.md` §Fields per M6** — `core` row, `requiresDelegation` row, chained-mode paragraph (`mode` joined with `+`, id form `<agent>-chain-<nn>`, mode expectation encoded in `must`). The schema example's `law` value updates later, with the body (Task 8), so the README never leads the shipped text.

- [ ] **Step 3: Baseline the new fixture**

Workflow on the same scriptPath with `args: {only: ["fastread-chain-01"]}`, then:

```bash
cp evals/last-run.md .claude/reviews/eval-run-2026-09-01-chain-baseline.md
```

Expected baseline outcome per M6: the fixture FAILS its MODES `must` line under the current singular contract — that failure is the datum; record it, never tune it.

- [ ] **Step 4: Commit (tracked files only)**

```bash
git add evals/executor-fast-read.json evals/README.md
git commit -m "fix(evals): add fastread-chain-01 composite-mode trap; document core, requiresDelegation, chained-mode schema"
```

### Task 3: Incumbent sweep — the findings that legalize the trim [D2]

**Interfaces:**
- Consumes: both current agent bodies; the M5 function test as the sweep's review lens.
- Produces: an indicted-line list filed at `.claude/reviews/2026-09-01-incumbent-sweep.md` (local); the ONLY license for Task 4's cuts besides gate-named free cuts (author-agent: "the packet may drop only indicted lines").

- [ ] **Step 1: Dispatch ONE executor-judge** — target: `agents/executor-fast.md` + `agents/executor-fast-read.md` as shipped; contract: model M5's function test (a line must bind the executor, prime recognition, or carry a law name) plus the standing checklist; prior ruling supplied: the model-gate verdict file. Output: per-line findings (keep/cut/rewrite-with-reason), typed.

- [ ] **Step 2: File the sweep verdict** under `.claude/reviews/` (local; no commit). Accepted findings become the packet's cut list, item by item.

### Task 4: Author the packet

**Files:**
- Create: scratchpad file `packet-mode-template.md` (session scratchpad — never committed)

**Interfaces:**
- Consumes: model sections M2–M6 (texts), Task 0's recorded green-light values, Task 3's accepted findings.
- Produces: items P1–P4, each with target file, anchor, verbatim replacement text, and the model section or sweep finding it answers. Task 5 gates this file; Task 7 applies it.

- [ ] **Step 1: Open the packet with the step-0 line (Cost values), the user's green light, and the covered rework count** — recorded at Task 0 Step 1; the gate refuses a packet missing any of the three.

- [ ] **Step 2: Author P1 — `.claude/skills/review-agent/references/agent-template.md`**

All four M3 amendments, each with its anchor: (1) insert the template block verbatim after the rewritten mode-block spec; (2) rewrite the mode-block spec at its current `takes:`/`Output:` paragraph so the overlay carries exactly one spec; (3) amend the classify-first bullet for chain-capable agents; (4) append the instance and residue-destination rules to the rule lists. Rules 1–10 otherwise untouched.

- [ ] **Step 3: Author P2 — `agents/executor-fast-read.md` body revision**

M2 texts ("three", precedence sentence, [D1] misroute sentence per ruling, rule-4-aligned preamble, `MODES:` line, pluralized andon carve-out), M4 RECON block verbatim, three mode blocks conformed to M3 (instances real, ≤5, no padding). Cuts: only Task 3-indicted lines.

- [ ] **Step 4: Author P3 — `agents/executor-fast.md` body revision**

Same shared M2 texts with "seven" plus the TRANSFORM reword, M4 TOTALITY attribution and REPRODUCE block verbatim, seven mode blocks conformed to M3. Cuts: only Task 3-indicted lines.

- [ ] **Step 5: Author P4 — stale-fixture migration [D1, if ruled keep-and-migrate]**

`fast-distilled-01`, `fast-hint-01`, `fast-notes-01/02` re-vehicled per M6 — target file, `migrated_from`, preserved intent stated per fixture. Authored at smart tier; rides in the packet so the gate rules on it with the bodies it must match.

- [ ] **Step 6: Self-check** — every item names target + anchor + verbatim text + the M-section or sweep finding it answers; no item touches a file outside M0's target list; P2/P3 contain no runtime tool identifiers.

### Task 5: Gate the packet (author-agent step 3)

**Interfaces:**
- Consumes: the packet; evidence set per review-agent: target files, every file in `agents/`, the checklist, the agent template, the model, `CLAUDE.md`, `PHILOSOPHY.md`, `evals/README.md`; prior rulings supplied verbatim: the model-gate verdict and the incumbent-sweep verdict (local files).
- Produces: per-item verdict APPLY / APPLY-WITH-CUTS / REWORK with findings; free token cuts named verbatim.

- [ ] **Step 1: Dispatch ONE executor-judge with the full evidence set (paths, not paraphrase) and both prior rulings.**

- [ ] **Step 2: Rework loop per author-agent step 4** — fold named cuts exactly; rework REWORK items per their findings; re-gate only changed items, same judge while fresh or a fresh judge supplied every prior ruling verbatim. Each round beyond the covered count needs its own green light. The author never self-clears an item.

### Task 6: User approval (author-agent step 5 — interactive stop)

- [ ] **Step 1: Present final verbatim texts on screen by item ID, each citing the gate verdict that cleared it.** Wait for explicit approval. No apply before it.

### Task 7: Apply (author-agent step 6)

**Files:**
- Modify: `.claude/skills/review-agent/references/agent-template.md`, `agents/executor-fast-read.md`, `agents/executor-fast.md`, `evals/executor-fast.json`, `evals/executor-fast-read.json` (P4)

**Interfaces:**
- Consumes: the cleared packet, and nothing else.
- Produces: the working-tree texts Task 8 verifies.

- [ ] **Step 1: Dispatch executor-fast per item — exact packet texts, one dispatch per path, no two concurrent dispatches writing one path, dirty-tree language verbatim (Global Constraints).**

- [ ] **Step 2: Commit per surface**

```bash
git add .claude/skills/review-agent/references/agent-template.md
git commit -m "feat(review-agent): four-slot mode template, multi-select classify machinery, instance and residue rules"
git add agents/executor-fast-read.md agents/executor-fast.md
git commit -m "feat(executors): applicable-modes multi-select, template conformance, RECON/TOTALITY/REPRODUCE law fixes"
git add evals/executor-fast.json evals/executor-fast-read.json
git commit -m "fix(evals): migrate pre-split fixtures to owning agents with migrated_from"
```

### Task 8: Verify (author-agent step 7) + after-run referee

**Files:**
- Modify: `evals/executor-fast.json` (diagnose `mode` → `REPRODUCE`, ids kept), `evals/executor-fast-read.json` (`law` fields → `AUTHORITATIVE RESOLUTION` on `fastread-recon-01/02`), `evals/README.md` (schema example `law` value; any remaining single-mode or DIAGNOSE prose)

**Interfaces:**
- Consumes: packet (fidelity reference), Task 1/2 local baseline records.
- Produces: the before/after comparison and the verify record Task 9 reports.

- [ ] **Step 1: Placement/fidelity** — whitespace-normalized match of every applied item against the packet, at its anchor.

- [ ] **Step 2: Routing probes** — record explicitly: N/A, no frontmatter description changed in this package.

- [ ] **Step 3: Align every naming artifact to the shipped text** — `fast-diagnose-01/02` `mode` → `REPRODUCE`; `fastread-recon-01/02` `law` → `AUTHORITATIVE RESOLUTION`; README schema example's `law` value; grep both eval JSONs and `evals/README.md` for `INFORMATION SCENT`, `DIAGNOSE`, and single-mode classification prose in rubric/`must` fields — update per M6. Validate both JSONs parse. Commit:

```bash
git add evals/executor-fast.json evals/executor-fast-read.json evals/README.md
git commit -m "fix(evals): REPRODUCE and AUTHORITATIVE RESOLUTION renames, single-mode prose sweep"
```

- [ ] **Step 4: After-run** — same Workflow invocation and scope as Task 1, then immediately:

```bash
cp evals/last-run.md .claude/reviews/eval-run-2026-09-01-after.md
```

Compare per-fixture against the baseline copies, mapping migrated ids via `migrated_from`.

- [ ] **Step 5: Regression rule (M6)** — a regression traced to a locked model decision escalates to the user; anything else is fixed (text via a re-gated packet delta if load-bearing) and re-run. `fastread-chain-01` failing its MODES line after the change is a finding against M2's residual risk — report it, never tune the fixture.

### Task 9: Closing report (author-agent step 8)

**Interfaces:**
- Consumes: gate verdicts, placement results, probe records, fixture entries, the run comparison.
- Produces: `.claude/reviews/2026-09-01-mode-template-package-close.md` (LOCAL — never committed). Its full text is the release PR's body content (M7 records policy): that is how the record publishes.

- [ ] **Step 1: Write the report** — per item: clearing verdict ID, placement result, probe output or explicit N/A, fixture or fixture-debt entry; plus the baseline/after comparison table. An item missing any of the four is not closed; say so.

### Task 10: Release (release skill — interactive at DECLARE, RULE, SHIP)

**Files:**
- Modify: `.claude-plugin/plugin.json` (version), `CHANGELOG.md`
- Delete from git at the START of this task: `docs/plans/mode-template-package.md`, `docs/plans/mode-template-package-model.md` (local copies kept under `.claude/reviews/` — the RULE gate reads the model from there as its supplied spec, and no commit lands after RULE's verdict)

**Interfaces:**
- Consumes: the finished branch; surface classes per release §0: `agents/` SHIPPED, `.claude/**` + `evals/` INTERNAL → full ritual runs.
- Produces: pushed branch + open PR whose body carries the Task 9 report and whose RULE verdict names the branch's final head commit. Merge is the user's hand only.

- [ ] **Step 1: Retire the plan artifacts (before DECLARE, so RULE's verdict names the final head)**

```bash
cp docs/plans/mode-template-package.md docs/plans/mode-template-package-model.md .claude/reviews/
git rm docs/plans/mode-template-package.md docs/plans/mode-template-package-model.md
git commit -m "chore(plans): retire branch working artifacts; local copies kept as release-gate spec"
```

- [ ] **Step 2: Invoke the release skill.** At DECLARE, present the §1.2 computation honestly: the package removes a mode name, removes a law name, and renames the return-contract field — computed recommendation is major unless the user scopes §1.2's removal/rename to whole surfaces; the user rules, and the CHANGELOG heading follows the ruling. Entry body (date = DECLARE day):

```markdown
### Changed
- `executor-fast` and `executor-fast-read` now classify with APPLICABLE MODES (multi-select): a chained task names every mode whose actions it contains and holds each law for the actions it governs; when two held laws pull against each other, the prohibition wins; the return line is `MODES:`. A task fitting no mode returns blocked as a misroute
- Mode blocks in both fast bodies conformed to the four-slot template (definition with capped illustrative instances; law with operational prohibition; example ending at the residue's destination); template and rules added to the review-agent agent template, which now carries a single mode-block spec
- `executor-fast`'s DIAGNOSE mode rescoped to REPRODUCE: it delivers the trigger that makes a failure fire on demand; naming the cause stays with `executor-smart`
- RECON's law re-cited: AUTHORITATIVE RESOLUTION (DNS) replaces Information Scent, whose source theory prescribes abandoning a weakening trail — the opposite of the rule it was cited for
- TRANSFORM's TOTALITY law gains its missing attribution (total functions, computability)
- Both fast bodies trimmed against the incumbent-sweep findings under the review gate

### Added
- `fastread-chain-01` composite-mode trap fixture; `core`, `requiresDelegation`, and chained-mode schema documentation in `evals/`
- Pre-2.15.0 executor-fast fixtures migrated to their owning agents with `migrated_from`
```

- [ ] **Step 3: Supply RULE with the spec** — the model's local copy at `.claude/reviews/mode-template-package-model.md`, named in the RULE dispatch as the design artifact (checklist Dimension 1).

- [ ] **Step 4: Stop at push + open PR, body carrying the Task 9 report.** The merge is not this plan's to make.

---

## Self-review record (writing-plans checklist, re-run after the model-gate fold)

- Spec coverage: M0→Task 0 (rulings gate), M1 (doctrine — constrains packet texts), M2→Tasks 4/7/8, M3→Tasks 4(P1)/7, M4→Tasks 4/7/8(step 3), M5→Tasks 3/4 (findings-first cuts), M6→Tasks 1/2/4(P4)/8, M7→Tasks 9/10 (records policy, retirement ordering, bump). No uncovered section.
- Findings coverage: F1/F1b (local run-record policy, no gitignored adds), F2 (Workflow scriptPath invocations), F3 (core field, args.all, coverage acceptance rewritten), F4 (README rows), F5 (MODES expectation in `must`), F6→D1 (clause marked, migration task P4), F7 (precedence sentence, TRANSFORM and andon rewords in P2/P3), F8 (single mode-block spec, amendment 2), F9 (template block is amendment 1 with anchor), F10→D2 (incumbent sweep Task 3, cuts only against findings), F11 (Cost section + Task 0 step-0 gate), F12 (law-field and README-example renames, Task 8 Step 3), F13 (provenance labeled in M1/M4; no task depends on an eval-held set), F14 (retirement before DECLARE, RULE reads local copy), F15 (bump un-committed, §1.2 presented at DECLARE), C1–C4 folded.
- Placeholders: none — run-time-determined values (ruled version, CHANGELOG date, D1–D3 outcomes) each carry their determination rule.
- Consistency: `MODES:`, REPRODUCE, AUTHORITATIVE RESOLUTION, fixture ids, task numbers, and local record filenames match across tasks and model sections.
