# maddog release doctrine — LOCKED model, rev 9 (2026-08-17)

CANONICAL, agent-facing. The published HTML artifact is a rendered view of
this file for the user; this file is the authority packets cite.
Rev 9 names the forward version rule's input source and restores the
uniqueness check's origin/main anchor (M58 — the last live descendant of
rev 7's compression), completes REMEDY's phase path (M59), scopes L12's
unit of account (M60), restores SEAL's recency qualifier (M61), and folds
the D3 addendum into D3 (M62). Rev 8 restored two prohibitions lost in
rev 7's compression and pinned the merge method (M51–M57; rulings filed
in session task record a76d847). Rev 7 was the SIMPLIFICATION (user-ruled, D11): mechanisms
removed with reversal evidence recorded; expedited judge replaces waiver
machinery; release record specified.

THESIS: the plugin marketplace installs from main HEAD (`source: "./"`), so
every merge to main IS a release. The ritual gates BEFORE merge; a seal runs
after; an incident lane exists for a bad release already published. The
ritual must stay executable by a fast-tier agent mid-incident (L12) — a
check nobody can run under pressure is not a check.

## Evidence register (first-hand: advisor-read, recon-quoted, or judge-demonstrated)

- E1: marketplace.json points plugin source at repo root — installs track
  main HEAD; merge = publish.
- E2: 14 CHANGELOG releases in 17 days (1.0.0→2.2.0); merge cadence can be
  ~1/hour (PRs #8/#9/#10 on 2026-08-17).
- E3: only 2.0.0 ever tagged (v2.0.0 + maddog--v2.0.0, same release); the
  directory submission is pinned to tags while the marketplace tracks HEAD.
  Versions are the only handle the directory submission has.
- E4: CI validate.yml checks exactly three things: frontmatter YAML parses,
  JSON parses (.claude-plugin/*.json, evals/*.json — NOT hooks/hooks.json),
  plugin.json version == CHANGELOG top entry (first-match regex — internal
  parity only, no uniqueness against history). On pull_request its checkout
  is the MERGE REF. It never lints or executes shell.
- E5: branch protection on main: force-push and deletion blocked; zero
  required reviews; no required_status_checks key; enforce_admins=false.
- E6: CLAUDE.md canon: conventional commits, scoped; bump plugin.json
  version when the shipped agent/skill set changes.
- E7: eval harness exists (evals/ + run-skill-routing.sh); CI parse-checks
  fixture JSON but never runs the harness; nor does any release step.
- E8: 2.2.0: manifest enumerations + cross-refs fixed by hand-driven sweep;
  nothing mechanical checks manifests match what ships.
- E9: standing debt: plugin-only bare-name agent-resolution probe never run.
- E10: jobbunny prior art unrecoverable locally.
- E11: every release 2.0.0+ went through a merged PR (judge-verified);
  merge is ALWAYS the user's hand.
- E12: GitHub docs — protection restrictions don't bind admins unless
  enforce_admins=true. Source: docs.github.com branch-protection REST +
  about-protected-branches (researcher return, 2026-08-17).
- E13: NAMED DEBT — 8 of 13 shipped surfaces have no eval fixture
  (advisor-mode, researcher, five product-*, product-engineering skill).
- E14: hooks/hooks.json runs scripts/executor-guard.sh before every Bash
  call in every plugin user's session — highest-blast-radius shipped file;
  its refusal path is live and testable.
- E15: local clones drift; decisions or checks on unsynced trees target
  something other than what ships.
- E16: install.sh is destructive to $CLAUDE_DIR and reads CLAUDE_DIR from
  the environment; an EMPTY sandbox exercises neither the backup branch nor
  foreign-link pruning — only a populated fixture does.
- E17: judge-demonstrated — a pure revert can DELETE validate.yml
  (`git revert -m 1 6dd9d0e`); reverting a merge needs a named `-m` parent.
- E18: judge-demonstrated — release merges carry their own bump, so a pure
  revert rolls the version BACKWARD; and not every merge bumps.
- E19: judge-probed — `lock_branch` has no sub-endpoint; it is settable
  only via a full-payload PUT of the protection object whose other four
  parameters (including enforce_admins and required_status_checks — D3's
  hardening) are Required, "set null to disable". Docs say lock_branch
  blocks PUSHES; silent on PR merges and admins. The unused rulesets
  surface exists (`/rulesets` → []). Grounds for the M45/M47 reversal.
- E20: judge-probed — all three merge methods are enabled on the repo
  (merge commit, squash, rebase) and delete_branch_on_merge is on (PR
  records survive branch deletion). The model depends on merge commits in
  four places; the method must be pinned (D3 addendum). PR bodies and
  SEAL comments are author-editable — edit history is retained and is the
  recourse if a record is disputed (M54).

## Failure modes → catching phase

| Failure | Evidence | Caught by |
|---|---|---|
| Routing regression ships silently | E7, E1 | BEHAVIOR |
| Manifest drift vs shipped reality | E8 | READY |
| Dangling by-name cross-refs | E8, E6 | READY |
| Version ruled on a stale base or after validation | E2 | DECLARE (synced, first) |
| Version collision under concurrent releases | E4, E2 | DECLARE uniqueness |
| Mid-flight main movement invalidates cleared work | E2 | FREEZE (D10) + bounded RETURN ARC |
| CHANGELOG/version holes beyond CI parity | E4 | READY |
| Red/unrun CI merged anyway | E5, E12 | D3 hardening once landed; INTERIM: READY stands in, SHIP's PR cites results; packet first-priority |
| Shipped hook/script breaks every user's Bash | E14, E4 | READY shell gate (syntax + pass/refuse smoke) |
| Bad release published | E1 | REMEDY (expedited judge) |
| Bad remedy | judge demo | L11: escalate, never revert a remedy |
| Revert rolls version backward / orphans tag | E18 | forward version rule |
| Directory pin left on a bad release | E3 | SEAL second-channel repair or named debt |
| Symlink-mode regression damages live ~/.claude | E16 | BEHAVIOR populated-fixture probe, pre-merge |
| Checks stale vs CI / unsynced trees | E15 | L6 |
| Intermediate HEAD published mid-multi-PR work | E1 | L9 |
| Surface lists drift | 3 prior findings | one SURFACE TAXONOMY, cited never re-enumerated |
| Unclassified path falls through | judge | taxonomy DEFAULT: fail closed to GATE-INFRA |
| Ritual outgrows what a pressured agent can run | M50 | L12 |
| Checks silently skipped under pressure | user's charge | L1 |

## Surface taxonomy (defined ONCE; D1, the shell gate, and judge guidance cite it)

- SHIPPED: agents/, skills/, workflows/, .claude-plugin/ manifests — what
  users receive (workflows/ reaches symlink installs only; the class
  governs triggers, not distribution).
- GATE-INFRA: .github/, hooks/, scripts/, install.sh — what enforces or
  wires the gate and the guard.
- INTERNAL: .claude/, evals/ — except .claude/skills/release/, which is
  GATE-INFRA (self-application: a broken gate is a broken factory).
- DOCS: README.md, CHANGELOG.md, CLAUDE.md, CONTRIBUTING.md, SECURITY.md,
  LICENSE, .gitignore.
- DEFAULT (fail closed): any unclassified path is GATE-INFRA until
  classified here. Growth is real; the interval defaults strict.

## Branch lifecycle

The candidate branch exists before any phase runs: DECLARE opens or adopts
it; version + CHANGELOG edits commit to it; phases test its committed tree,
synced per L6 — never a dirty working tree. Multi-PR work stages on a
feature branch until whole (L9). SHIP pushes and opens the PR.

## The release record (M46 — specified)

GitHub-native; no push-to-main needed. THE RELEASE PR IS THE RECORD:
- SHIP's PR body cites the RULE verdict naming the head commit, the probes
  run, and every UNVERIFIED item with its named debt.
- SEAL posts its results (tag, CI-on-main, install probes, second-channel
  state) as a comment on the merged PR.
- SEAL passes when every probe succeeded or is recorded UNVERIFIED with a
  named debt; it FAILS only on an affirmative failure. "Fully-gated" means
  gated per the ritual with debts named — the record says which.
- LAST FULLY-GATED STATE := the most recent merge commit on main whose PR
  carries a verdict naming its head AND a SEAL comment that passed.
  Computed from PRs (gh), never inferred from versions or trees.
- BOOTSTRAP: at skill adoption the user attests the then-current main HEAD
  as the gated baseline (recorded in the adoption PR); the adoption PR —
  full ritual, per self-application — becomes the first true record.

## Phases

1. DECLARE — version first, on a fresh base: sync (fetch origin, rebase
   candidate onto origin/main — L6 binds this phase); delta class computed
   against origin/main HEAD (removal/rename→major-rec, addition→minor-rec,
   fix→patch-rec); USER rules the bump (D5), ruling logged; UNIQUENESS
   check (version in none of origin/main's CHANGELOG headings — the
   candidate's is no anchor, its headings may be under revert — and no
   tag; M58 restores rev 6's origin/main qualifier); version + CHANGELOG
   committed to the candidate.
2. READY — fast-tier, mechanical, on the synced candidate tree:
   - CI's checks run locally by EXTRACTING the VALIDATE heredoc from the
     live validate.yml and executing it verbatim; the extractor asserts the
     workflow's expected shape and FAILS CLOSED on mismatch (L6).
   - Shell gate (E14): bash -n on GATE-INFRA shell; JSON-parse hooks.json;
     hook command paths must resolve; executor-guard.sh run twice — benign
     payload passes, known-dangerous payload is REFUSED.
   - Manifest enumerations re-derived from the filesystem, diffed against
     both manifests (L4). Repo-wide sweep for added/renamed/removed names.
   - CHANGELOG entry present + styled — validating what DECLARE ruled.
3. BEHAVIOR — probes, pre-merge: run-skill-routing.sh where a fixture home
   exists (else cite E13); fresh-session claude -p probes per changed
   description (happy path + moved boundaries); plugin-mode probe where
   relevant (E9); populated-fixture install.sh probe when GATE-INFRA
   touched (E16). Unrunnable ⇒ UNVERIFIED with named debt (under L1).
4. RULE — the gate: adversarial release-review by a fix-less judge;
   CLEAR/BLOCKED with findings; the verdict names the commit it covers.
   On the REMEDY lane this is the EXPEDITED verdict (see REMEDY) — smaller
   question, same judge structure, never waived.
5. SHIP — fast-tier, exact texts: push, PR citing the verdict (and, until
   D3 lands, the local check results). Merge = user's hand, always — and
   THE USER MERGES ONLY A PR WHOSE VERDICT NAMES ITS HEAD COMMIT (M52,
   restoring rev 6's merge-side prohibition): a superseded or absent
   verdict holds the merge, whatever produced the mismatch.
6. SEAL — post-merge: tag per D2 on the merge commit (L3); CI green on
   main; fresh plugin-install probe or UNVERIFIED record; live install.sh
   run licensed ONLY by BEHAVIOR's populated-fixture pass THIS RELEASE
   (M61 restores rev 6's recency qualifier — a prior release's pass
   licenses nothing against `~/.claude`, the E16 fence); second-channel check
   (directory pin updated/resubmitted or debt named); SEAL comment posted
   on the PR. On an affirmative SEAL failure: REMEDY — unless the failed
   release was itself a REMEDY: then the full ritual, judge present (L11).

RELEASE FREEZE (D10) — one release in flight at a time, as discipline: the
sole merger is the user; entering DECLARE means their other sessions do not
merge to main until SHIP or abort. The release record notes freeze start
and end. (Structural enforcement via lock_branch was adopted and REVERSED
on evidence E19; rulesets remain a future hardening option, out of model.)

RETURN ARC — origin/main moved after DECLARE, before merge: re-enter at
DECLARE (re-sync; recompute; uniqueness again; user re-rules only if delta
class changed or version collided), then ALL phases re-run in order —
READY in full, BEHAVIOR scoped to candidate delta ∪ intervening renames/
removals, RULE re-affirmed by a fresh judge with the prior verdict supplied
as binding precedent, verdict naming the new head. PR updated via a
sanctioned force-push to the CANDIDATE branch only. BOUNDED: two re-runs;
a third movement STOPS — the user chooses abort (candidate survives, ritual
ends) or an explicitly authorized restart at DECLARE with a fresh counter.
No third option, no implicit continuation.

REMEDY — the incident lane for a bad release already on main:
- PREEMPTION (M48): REMEDY outranks a release in flight — the in-flight
  candidate holds unmerged (or aborts, user's call); the incident goes
  first.
- Unit of work (D7): the chain of pure reverts restoring the LAST
  FULLY-GATED STATE (as computed from the release record) — never a
  partial revert that strands a dependent, never a revert-plus-fix.
- FORWARD VERSION RULE (E18): a remedy is a new FORWARD release — patch
  bump on the highest version ever shipped, READ FROM origin/main's
  plugin.json `version` (M58): merge = publish, so main's manifest IS the
  highest shipped, and CI's parity check pins the CHANGELOG top heading to
  it. Tags are NEVER the source — E3: most shipped versions were never
  tagged, so a tag-sourced bump ships a remedy numbered below what users
  hold (M32's failure via unnamed input). The candidate tree is never the
  source either — the reverts under review rewrite it. Whether or not the
  offending merge bumped, the CHANGELOG entry names the restoration; the
  bad tag and heading stay as history; versions are monotonic, always. On this lane
  the forward rule IS the standing user ruling under D5 — no human ruling
  blocks mid-incident.
- Path: every phase in order EXCEPT BEHAVIOR — DECLARE (forward bump +
  uniqueness) + READY + an EXPEDITED JUDGE verdict at RULE + SHIP + SEAL
  in their normal form; SHIP's merge-side prohibition binds here as
  everywhere (M59). The expedited verdict (replacing rev 4-6's waiver
  machinery): the judge answers one narrow question — "is this candidate exactly the chain of pure reverts
  restoring the last fully-gated state, plus one bounded bump commit
  (plugin.json version line + new CHANGELOG entry only, value per the
  forward rule — M51), and nothing else?" — with the regenerated reverts
  (named -m parents, E17) supplied as evidence.
  JUDGE GUIDANCE, not mechanism: a revert touching GATE-INFRA (E17) or a
  conflicted revert means judgment has entered — the judge may still clear
  it or may route to the full ritual; the call is the judge's, present,
  never waived. (M57: until D3 lands, L10 is dormant and this discretion
  is the ONLY guard on a validate.yml-deleting revert — named here, not
  hidden.) BEHAVIOR is skipped on this lane because this exact content was
  previously live in users' hands (M55 — the honest justification; "it
  was gated" would overclaim, since gating permits named UNVERIFIED
  debts); the judge's verdict says so explicitly.
- HONEST PRICE (M49): a failed remedy escalates to the full ritual with
  users broken meanwhile; the escalated RULE dispatch may trim BEHAVIOR's
  probe set to the incident's scope — the judge rules on the trim. The
  exposure is stated in the release record, not hidden.
- The novel fix always follows at ritual pace; the lane only ever restores.

## Laws (prohibitions — prohibitions hold under pressure; obligations don't)

- L1 No silent skips: no release claim while any phase check is unrun or
  unrecorded. (Unrunnable probes: UNVERIFIED + named debt.)
- L2 Never merge: the skill and every hand it dispatches are forbidden
  from merging; the gate is never chained to the merge.
- L3 No tag before merge: tags land on merge commits only.
- L4 No manifest text from memory: enumerations re-derived from the
  filesystem every release.
- L5 No verdict from a hand that can fix — and the release's author never
  clears their own gate. THIS INCLUDES THE INCIDENT LANE: expedited, never
  waived.
- L6 No decisions or checks on unsynced trees, no remembered check lists:
  the live validate.yml logic, extracted and executed verbatim, failing
  closed on unexpected shape.
- L7 The incident lane ships nothing but reverts PLUS DECLARE's bounded
  bump commit — bounded (M51, restoring rev 4's carve-out) to the
  plugin.json version line and the new CHANGELOG entry only, its value
  equal to the forward rule's computed number — confirmed by the expedited
  judge verdict against the regenerated chain, never asserted, never
  self-certified.
- L8 validate.yml gains no paths: filter while required; validate.yml
  edits take the full ritual.
- L9 No intermediate main: multi-PR work stages until whole; a REMEDY
  chain-unit satisfies this by restoring the gated state whole.
- L10 No PR deletes validate.yml while it is required: un-require first —
  a deliberate repo-settings change, itself full ritual.
- L11 No remedy of a remedy: a failed remedy escalates to the full ritual,
  judge present — reverting a revert re-ships the bad content under a
  climbing version.
- L12 (M50) No growth without removal: this model and the skill authored
  from it may not gain a mechanism without removing or consolidating one.
  ENFORCEMENT (M56): .claude/skills/release/ is GATE-INFRA, so every skill
  change faces RULE — and that judge must answer "could a fast-tier agent
  execute each mechanical phase from its checklist alone?"; a NO is a
  BLOCKED verdict, giving the executability clause a test and an owner.
  A ritual too heavy to run under pressure will be skipped under pressure,
  and L1 cannot catch what nobody starts.
  UNIT OF ACCOUNT (M60): a mechanism is anything the ritual must EXECUTE
  or a hand must MAINTAIN — a phase, check, lane, gate question, or
  standing procedure. Not mechanisms: evidence entries, decision records,
  restorations of previously-gated text, and one-time repo settings
  (which count once, at adoption, as packet items — the rev 8 merge-method
  pin is settings, not growth).

## Locked decisions (user-ruled 2026-08-17)

- D1: full ritual on SHIPPED ∪ GATE-INFRA (see taxonomy); INTERNAL and
  DOCS take READY alone.
- D2: every release tagged vX.Y.Z post-merge; maddog--vX.Y.Z reserved for
  directory submissions.
- D3: repo hardening = the packet's FIRST-PRIORITY items (repo changes,
  not skill wishes): validate required, enforce_admins=true (E12),
  strict=false, under L8/L10 — and MERGE METHOD PINNED (M53, E20): repo
  settings allow merge commits only, squash and rebase merge disabled.
  The model depends on merge commits in four places: the record's
  computation, L3's referent, D7's chains, and E17's -m parents. One
  dropdown click must not disable the incident lane.
- D4: internal skill at .claude/skills/release/, /release; never ships.
- D5: semver = computed rec, user rules, logged — in DECLARE, synced,
  unique, before READY validates. On the incident lane the forward rule is
  the standing ruling.
- D6: maddog evidence alone; jobbunny prior art unrecoverable (E10).
- D7: the incident unit = the chain of pure reverts restoring the last
  fully-gated state (operational definition in The Release Record).
- D8/D9 (superseded as mechanism, preserved as guidance): gate-infra
  reverts and conflicted reverts signal entered judgment — the expedited
  judge weighs them, present, never waived.
- D10 (re-ruled at rev 7 on E19): the freeze is DISCIPLINE + the bounded
  RETURN ARC; structural lock_branch adopted at rev 6 and reversed —
  full-payload PUT would rewrite D3's hardening from memory, and the
  lock's merge-blocking is undocumented. Rulesets: future option.
- D11 (rev 7, user-ruled): SIMPLIFY over fix-forward — the waiver and its
  qualifying machinery are replaced by the expedited judge; L12 bounds all
  future growth.
- (D3 addendum folded into D3 at rev 9 — M62, define once and cite.)
