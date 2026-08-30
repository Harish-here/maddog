---
name: release
description: >
  Runs the release ritual for any change to SHIPPED or GATE-INFRA surfaces headed
  for main (surface taxonomy in section 0) — the plugin marketplace installs from
  main HEAD, so every merge to main is a publish. Gates DECLARE (version +
  CHANGELOG) through READY, BEHAVIOR, RULE (adversarial judge verdict), and SHIP
  (push + PR citing the verdict) before merge; SEAL runs after. Changes confined
  to INTERNAL or DOCS take READY alone. This skill lives at .claude/skills/release/
  and is itself GATE-INFRA — self-application: a broken gate is a broken factory.
  Do NOT use for work staying off main (feature-branch WIP) or a PR that is not a
  release candidate. Do NOT use to merge anything: it NEVER merges — the skill and
  every hand it dispatches stop at push + open PR; the user's hand is the only
  merge, and only on a PR whose verdict names its current head commit.
metadata:
  internal: true
---

## 0. Surface taxonomy (cite this, never re-enumerate)

- SHIPPED: agents/, skills/, workflows/, .claude-plugin/ manifests — what users
  receive (the class governs triggers, not distribution).
- GATE-INFRA: .github/, hooks/, scripts/ — what enforces the gate and
  the guard. `.claude/skills/release/` is GATE-INFRA even though it lives under
  `.claude/` (self-application).
- INTERNAL: `.claude/`, `evals/` (except release/, above).
- DOCS: README.md, CHANGELOG.md, CLAUDE.md, CONTRIBUTING.md, SECURITY.md, LICENSE,
  .gitignore, PHILOSOPHY.md, DESIGN.md, assets/, skills.sh.json.
- DEFAULT: any unclassified path is GATE-INFRA until classified above — fail
  closed.
- D1 (behavior, restated from the router — M71): full ritual (all six
  phases) on SHIPPED ∪ GATE-INFRA; INTERNAL and DOCS take READY alone.

## Branch lifecycle

The candidate branch exists before any phase runs. DECLARE opens or adopts it;
version + CHANGELOG commit to it; every later phase tests its committed tree,
synced per L6 — never a dirty working tree. Multi-PR work stages on a feature
branch until whole (L9). SHIP pushes it and opens the PR.

## 1. DECLARE — session/advisor tier (interactive; holds user ruling and acceptance)

1. `git fetch origin`; rebase the candidate branch onto `origin/main` — never
   operate on an unsynced or dirty tree (L6).
2. Compute the delta class against `origin/main` HEAD: removal or rename →
   major-rec; addition → minor-rec; fix → patch-rec.
3. Present the computed recommendation to the user; the USER rules the actual
   bump (D5); log the ruling verbatim.
4. Uniqueness check, against `origin/main` (never the candidate — its CHANGELOG
   headings may be mid-revert): the ruled version appears in none of
   `origin/main`'s CHANGELOG headings, and no existing git tag matches it.
5. Commit the version bump (`.claude-plugin/plugin.json`) and the new CHANGELOG
   entry to the candidate branch.

## 2. READY — fast-tier executor, objective checklist, on the synced candidate tree

1. **CI-equivalent, extracted and executed verbatim (L6):** open
   `.github/workflows/validate.yml`; extract the Python heredoc between `<<
   'VALIDATE'` and the closing `VALIDATE` marker. Confirm the surrounding shape
   is still checkout → setup-python 3.11 → `pip install pyyaml` → this heredoc;
   if changed, FAIL CLOSED — do not substitute a remembered copy, report the
   mismatch as a READY failure. Otherwise run the extracted script verbatim
   (`python3`, pyyaml installed) against the candidate tree. Today it checks:
   frontmatter YAML parses on `skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`,
   `agents/*.md`; JSON parses on `.claude-plugin/*.json` and `evals/*.json`;
   `plugin.json`'s `version` equals CHANGELOG.md's first `## [...]` heading.
2. **Shell gate (E14):** `bash -n` on every GATE-INFRA shell file
   (`scripts/*.sh`); JSON-parse `hooks/hooks.json`; every hook
   command path in it resolves to an existing file; run
   `scripts/executor-guard.sh` twice — a benign payload must pass, a
   known-dangerous payload must be REFUSED.
3. **Manifest re-derivation (L4):** enumerate agents/, skills/, workflows/ from
   the filesystem; diff against both manifests (`.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json`). Repo-wide grep sweep for by-name
   cross-references to anything added, renamed, or removed this release.
4. **CHANGELOG check:** entry present, styled per the file's existing
   convention, matches what DECLARE ruled.

## 3. BEHAVIOR — pre-merge probes: steps 1, 3 fast-tier; step 2 MID-TIER (M67)

1. `run-skill-routing.sh` where a fixture home exists — derive the list from
   `evals/*.json` on the candidate tree, never from memory (L4's spirit); for
   each changed surface with no fixture home, record UNVERIFIED + named debt
   (E13 recorded the coverage gap at adoption; re-derive, don't re-quote).
2. For every description added or changed: fresh-session `claude -p` probes —
   happy path plus each moved routing boundary, both directions. MID-TIER
   hand: deriving which boundaries moved from the description diff and
   composing prompts that DISCRIMINATE old routing from new is local
   judgment — a probe any description would pass is vacuous and does not
   count as a probe.
3. Plugin-mode probe (bare-name agent resolution under a plugin install) where
   relevant — currently never run (E9); record UNVERIFIED + named debt E9 until
   it is.
4. Anything that cannot run in this environment: record UNVERIFIED with a
   named debt (L1) — never silently skip it.

## 4. RULE — executor-judge (fix-less), the gate

1. Dispatch one adversarial release-review to executor-judge; evidence set =
   the candidate diff, READY's and BEHAVIOR's results, the surface taxonomy,
   and (on REMEDY) the prior verdict as precedent.
2. Verdict: CLEAR or BLOCKED, with findings; the verdict names the exact commit
   (head SHA) it covers.
3. No verdict from a hand that can fix (L5) — the release's author never clears
   their own gate. Includes the incident lane: expedited, never waived.
4. On the REMEDY lane this step is replaced by the EXPEDITED verdict — see
   REMEDY below; same judge structure, narrower question.

## 5. SHIP — fast-tier executor, exact texts

1. Push the candidate branch to origin.
2. Open (or update) the PR against main. PR body must cite: the RULE verdict
   (CLEAR, the commit SHA it names), every check READY and BEHAVIOR ran with
   results, every UNVERIFIED item with its named debt, and — until D3's
   branch-protection hardening lands as a separate repo-settings change — the
   local check results in full, standing in for required status checks.
3. STOP. Never merge — that is the user's hand, always (L2).
4. State to the user explicitly: merge ONLY a PR whose verdict names its
   current head commit (M52) — a superseded or absent verdict (e.g. after a
   force-push) holds the merge, whatever produced the mismatch.

## 6. SEAL — fast-tier executor, post-merge

1. Tag the merge commit `vX.Y.Z` (D2) — never before merge (L3); then, on
   that same commit, run `claude plugin tag --push` from the repo root,
   producing `maddog--vX.Y.Z` — a dependency-resolution tag that lets OTHER
   plugins declare semver constraints on this one (plugin-dependencies.md);
   never before merge either. Dispositions on the command's own refusals:
   tag already exists on this commit → the required end-state already
   holds — record and continue, NOT a failure; dirty tree under the plugin
   directory (the repo root) → stash or commit, never discard; if the dirt
   is not yours, hand back to the user; `plugin.json`/marketplace version
   disagreement, or any other validation failure → affirmative SEAL
   failure; tag created but the push failed → run the printed `git push`
   yourself — a local-only tag is not a pass. Record BOTH CLI lines:
   `Created tag maddog--vX.Y.Z` and `Pushed to origin`.
2. Confirm CI is green on main for the merge commit.
3. Run a fresh plugin-install probe, or record UNVERIFIED + debt.
4. Post a SEAL comment on the merged PR: tag, `maddog--vX.Y.Z` tag (with
   both CLI output lines), CI-on-main status, install probe results.
5. SEAL PASSES when every probe succeeded or is recorded UNVERIFIED with a
   named debt; it FAILS only on an affirmative failure. "Fully-gated" means
   gated per the ritual with debts named — the record says which.
6. On an affirmative SEAL failure: enter REMEDY — unless the failed release
   was itself a REMEDY, in which case run the full ritual with the judge
   present (L11).

## REMEDY — incident lane, a bad release already on main

1. **Preemption (M48):** REMEDY outranks a release in flight — the in-flight
   candidate holds unmerged, or aborts (user's call); the incident goes first.
2. **Unit of work (D7):** the chain of pure reverts restoring the LAST
   FULLY-GATED STATE (computed from the release record, below) — never a
   partial revert that strands a dependent, never a revert-plus-fix.
3. **Forward version rule (E18):** a remedy is a new FORWARD release — patch
   bump on the highest version ever shipped, read from `origin/main`'s
   `plugin.json` `version` (M58) — never from tags (tags can be backfilled or
   moved; `plugin.json` on main cannot silently lie about what shipped), never
   from the candidate tree (the reverts under review rewrite it). The CHANGELOG
   entry names the restoration; the bad tag and heading stay as history;
   versions are monotonic, always. On this lane the forward rule IS the
   standing D5 ruling — no human ruling blocks mid-incident.
4. **Path:** every phase EXCEPT BEHAVIOR, in order — DECLARE (forward bump +
   uniqueness) → READY → EXPEDITED JUDGE verdict at RULE → SHIP → SEAL, all in
   their normal form; SHIP's merge-side prohibition (M52) binds here too
   (M59).
5. **Expedited verdict:** the judge answers exactly one narrow question — "is
   this candidate exactly the chain of pure reverts restoring the last
   fully-gated state, plus one bounded bump commit (`plugin.json` version line
   + new CHANGELOG entry only, value per the forward rule), and nothing else?"
   — with the regenerated reverts (named `-m` parents, E17) supplied as
   evidence.
6. **Judge guidance, not mechanism:** a revert touching GATE-INFRA (E17) or a
   conflicted revert means judgment has entered — the judge may still clear it
   or route to the full ritual; the call is the judge's, present, never
   waived. Until D3's hardening lands, this discretion is the ONLY guard on a
   `validate.yml`-deleting revert (M57) — named here, not hidden.
7. **Why BEHAVIOR is skipped:** this exact content was previously live in
   users' hands (M55) — "it was gated" would overclaim, since gating permits
   named UNVERIFIED debts; the judge's verdict states this explicitly.
8. **Honest price (M49):** a failed remedy escalates to the full ritual with
   users broken meanwhile; the escalated RULE dispatch may trim BEHAVIOR's
   probe set to the incident's scope — the judge rules on the trim; state the
   exposure in the release record, not hidden.
9. The novel fix always follows later, at ritual pace — the lane only ever
   restores.

## RETURN ARC — origin/main moved after DECLARE, before merge

1. Re-enter at DECLARE: re-sync, recompute the delta class, run uniqueness
   again; the user re-rules ONLY if the delta class changed or the version
   collided.
2. Re-run ALL phases in order: READY in full; BEHAVIOR scoped to the
   candidate's delta ∪ any intervening renames/removals; RULE re-affirmed by a
   fresh judge with the prior verdict supplied as binding precedent, new
   verdict naming the new head.
3. Update the PR via a sanctioned force-push to the CANDIDATE branch only.
4. BOUNDED: two re-runs. A third `origin/main` movement STOPS the arc — the
   user chooses either abort (candidate survives, ritual ends) or an
   explicitly authorized restart at DECLARE with a fresh counter. No third
   option, no implicit continuation.

## RELEASE FREEZE (D10)

- One release in flight at a time, as discipline (not a structural lock —
  `lock_branch` was tried and reversed on evidence E19; GitHub rulesets remain
  a future hardening option, out of this model).
- The sole merger is the user; entering DECLARE means the user's other
  sessions do not merge to main until this release SHIPs or aborts.
- The release record notes freeze start and end.

## The release record

GitHub-native; no push-to-main needed to record anything.

- THE RELEASE PR IS THE RECORD: SHIP's PR body cites the RULE verdict naming
  the head commit, every probe run, and every UNVERIFIED item with its named
  debt.
- SEAL posts its results (tag, `maddog--vX.Y.Z` tag output, CI-on-main,
  install probes) as a comment on the merged PR.
- SEAL passes when every probe succeeded or is recorded UNVERIFIED with a
  named debt; it FAILS only on an affirmative failure.
- LAST FULLY-GATED STATE := the most recent merge commit on main whose PR
  carries a verdict naming its head AND a SEAL comment that passed. Compute
  this from PRs (`gh`), never infer it from versions or trees.
- BOOTSTRAP: see "First run" below.

## Laws (prohibitions — hold under pressure; obligations don't)

- **L1** No silent skips: no release claim while any phase check is unrun or
  unrecorded. Unrunnable probes → UNVERIFIED + named debt.
- **L2** Never merge: the skill and every hand it dispatches are forbidden
  from merging; the gate is never chained to the merge.
- **L3** No tag before merge: tags land on merge commits only.
- **L4** No manifest text from memory: enumerations re-derived from the
  filesystem every release.
- **L5** No verdict from a hand that can fix — the release's author never
  clears their own gate. Includes the incident lane: expedited, never waived.
- **L6** No decisions or checks on unsynced trees, no remembered check lists:
  the live `validate.yml` logic, extracted and executed verbatim, failing
  closed on unexpected shape.
- **L7** The incident lane ships nothing but reverts plus DECLARE's bounded
  bump commit — bounded to the `plugin.json` version line and the new
  CHANGELOG entry only, its value equal to the forward rule's computed
  number, confirmed by the expedited judge verdict against the regenerated
  chain — never asserted, never self-certified.
- **L8** `validate.yml` gains no paths: filter while required; `validate.yml`
  edits take the full ritual.
- **L9** No intermediate main: multi-PR work stages until whole; a REMEDY
  chain-unit satisfies this by restoring the gated state whole.
- **L10** No PR deletes `validate.yml` while it is required: un-require first
  — a deliberate repo-settings change, itself full ritual.
- **L11** No remedy of a remedy: a failed remedy escalates to the full
  ritual, judge present — reverting a revert re-ships the bad content under a
  climbing version.
- **L12** No growth without removal: this skill may not gain a mechanism
  without removing or consolidating one. ENFORCEMENT: since
  `.claude/skills/release/` is GATE-INFRA, every change to this skill faces
  RULE — and that judge must answer "could a fast-tier agent execute each
  mechanical phase from its checklist alone?"; a NO is a BLOCKED verdict.
  (The unit of account for "mechanism" is defined in the locked model at
  `references/release-model.md`, committed beside this file; the RULE judge
  applies it from there.)

## First run / bootstrap

1. At adoption, the user attests the then-current main HEAD as the gated
   baseline; record that attestation in the adoption PR.
2. The adoption PR itself runs the full ritual (self-application: this file
   is GATE-INFRA under D1, not INTERNAL) — it becomes the first true release
   record. (D3's interim mode, while it applies, is defined in SHIP step 2.)
