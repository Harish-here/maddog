# Gate Ruling: Round 2 Design-Review Re-Gate on `docs/plans/executor-fast-read.md`
**Date: 2026-08-31**

## VERDICT

**BLOCKED** — decision 18's normalization algorithm, as specified, does not close probe case 2 and introduces a new ALLOW bypass; T4/T5's mandated function-sharing is not achievable by any tasked file; and T8's eval fixtures cannot supply the evidence T4/T5 name as their only accepted proof.

## ROUND 1 CLOSURE

| # | State | Evidence |
|---|---|---|
| 1 | CLOSED (superseded by D-A) | Session scoping dropped; "normalize before match" promoted to T4. Spec quality is New Finding 1/4. |
| 2 | **STILL OPEN (partial)** | Five dispatch callers correctly retargeted — I read all six `sdd-task-loop.js` sites; :384 writes `review-dossier.md` and :354/:448 mutate git, so the exclusions hold. But `agents/executor-smart.md:17` and `README.md:86,161` still route "search, extraction" to `executor-fast` and are in no task. See NF5. |
| 3 | CLOSED | Grep gives exactly `executor-judge.md:14,15,31,33,106`; T9 covers all three sites. |
| 4 | CLOSED | `grep -n executor .claude-plugin/*.json` → only the `keywords` line. No by-name enumeration in either manifest; READY now names the §2-step-3 sweep. |
| 5 | CLOSED | T8 DONE-WHEN requires 6 standing-law fixtures. |
| 6 | CLOSED | `.claude/workflows/agent-evals.js` is the only copy (`ls workflows` → `sdd-task-loop.js` only); T8 hits AGENTS/RUN_MODEL/Load prompt. |
| 7 | CLOSED WITH DEFECT | Breadcrumb required, but no schema slot exists. See NF6. |
| 8 | CLOSED | Body spec names capability only; `Write` survives solely in frontmatter, an adapter path per `CLAUDE.md`. |
| 9 | CLOSED | Verified: DELEGATION is `agents/executor-judge.md:96-120`, 25 lines. |
| 10 | CLOSED | Lines 420/425/428 confirmed carrying the false "route through an executor that holds Write/Edit" text; T6 rewrites them. |
| 11 | CLOSED | Per owner instruction; not reopened. |

## NEW FINDINGS

1. **LOAD-BEARING — decision 18's ordering is unsound; it cannot close the four probe cases** (`plan:131-138`, `plan:226`). Collapsing `..` lexically *before* symlink resolution computes a different path than the kernel will open. With `link -> /Users/harishamutha/maddog-skills/agents`, the target `/private/tmp/scratchpad/link/../victim` collapses lexically to `/private/tmp/scratchpad/victim` → `is_temp_path` TRUE → ALLOW, while the kernel writes `/Users/harishamutha/maddog-skills/victim`. Separately, "resolve symlinks one hop at a time via `readlink`" over the *whole path* only ever inspects the final component, so probe case 2 (an intermediate symlink, `plan:226`) is untouched: `readlink` on a non-symlink leaf returns nothing, the loop exits, `/scratchpad/` matches, ALLOW. Clear it: T4 must specify a left-to-right per-component walk from the root, resolving each symlink as encountered and applying `..` only to the already-resolved prefix, with a hop budget — and its DONE-WHEN must add these two shapes as probes, not just the four already known.
2. **LOAD-BEARING — T5 cannot call T4's function; no task creates a shared library** (`plan:243-248`, `plan:258-259`). `scripts/executor-guard.sh:222` runs `input="$(cat 2>/dev/null)"` at top level and the whole guard body follows to `:499`; sourcing it consumes the caller's stdin and executes the guard. T4's Files list is `executor-guard.sh` alone, T5's is the new script + `hooks.json`. So T4's DONE-WHEN ("T5's hook calls this same function... not reimplemented") is unsatisfiable as tasked. Clear it: task the extraction of `normalize_path`/`is_temp_path` into a sourceable `scripts/` helper both hooks read.
3. **LOAD-BEARING — the named evidence cannot fail.** T4 (`plan:243-245`), T5 (`plan:272-273`) and Risks (`plan:486-492`) make T8 eval fixtures the only accepted proof. But `evals/README.md` (`setup.files` row) states the runner "materialises these in a fresh temp dir and runs the agent with that as cwd. Fixtures never touch this repo." Every fixture cwd is therefore already inside `/var/folders` or `/private/tmp`, where BROAD confinement passes by construction, and the one target that would prove an escape — a repo path — is forbidden by the harness's own rule. Clear it: point T4/T5's DONE-WHEN at direct payload probes against the scripts (the shape run in this review), which the release READY step already lists (`plan:440-441`); keep fixtures as behavioural supplement.
4. **LOAD-BEARING — one shared `normalize_path` is wrong for one of its two call sites** (`plan:231-242`). `rm -r` does not dereference a trailing symlink; the `Write` tool does. Full resolution at the leaf therefore turns a currently-correct deny into an allow: `rm -rf <repo-symlink -> /tmp/cache>` normalizes to `/tmp/cache`, passes `is_temp_path`, and `rm` then deletes the repo symlink. The fix opens a hole in the check it repairs. Clear it: T4 must state final-component handling per call site (parent-only resolution for `:291`, full resolution for T5) and add both directions as probes.
5. **LOAD-BEARING — round 1 finding 2 is not fully closed.** `agents/executor-smart.md:17` ships a HOT description reading "Do NOT use for mechanical, objective work (bulk edits, test runs, **search, extraction**...) — executor-fast, cheaper"; `README.md:86-88` and `:158-161` likewise. Post-T2 these route two removed modes to a hand that no longer classifies them. `plan:514-519` names this in Risks and explicitly declines to task it. Clear it: add both files to T3's group B, or record them as owner-accepted debt with a named follow-up.
6. **MINOR — T8's DONE-WHEN is self-contradictory** (`plan:326-327`, `plan:360-364`). It requires each migrated fixture to "carry its prior id as a comment/field" *and* validate against `evals/README.md`'s schema, whose Fields table is a closed list with no such slot; JSON has no comments. Clear it: T8's Files entry must extend the Fields table, not only the schema line.
7. **MINOR (unverified assumption) — cwd resolution is asserted, not established.** `grep -n "cwd\|realpath\|readlink\|normalize"` over both guards exits 1: neither reads `.cwd` today. T4 assumes the payload carries it (round 1's ruling verified this for PreToolUse) and assumes payload cwd equals the shell's cwd — untrue when a chained segment does `cd`, which `split_command` evaluates independently. Clear it: DONE-WHEN asserts `.cwd` extraction and records the chained-`cd` limit.
8. **COSMETIC** — decision 9 (`plan:83-84`) cites "T8's corrected baseline"; it is T9's. `plan:229-230` says `:419-421` denies `rm` "before any path is examined" — `:291` examines first; the outcome is unchanged, the rationale is wrong.

## DELEGATION LOG

none — all evidence read or run first-hand.

## NOTES

- Probed the guard directly with the four payloads: `/tmp/..` escape and `scratchpad/..` escape produce no deny (ALLOWED); the plain repo path denies. The confirmed-defect premise holds first-hand.
- Finding 4 rests on POSIX `rm` semantics (a trailing symlink is unlinked, not followed), reasoned rather than probed — I hold no write tool to plant a symlink.
- **Open questions: both safely deferrable.** The `version` field is a flat integer (`evals/README.md:31`, `executor-fast.json:3`, `executor-judge.json:3`) with no stated convention — nothing consumes it, so no task stalls. T10's one-sentence question is a sufficiency preference; T10's DONE-WHEN is objective without it.
- **Task ordering holds.** T1←∅; T2←T1; T3←T1,T2; T4←∅; T5,T6←T1,T4; T7←T1; T8←T1-T7; T9←T7; T10←T1; T11←T1-T10. Acyclic, and T4 correctly gates both writers of the path logic. No partial stop leaves main self-contradictory: T11 merges one candidate branch, so every intermediate disagreement is intra-branch. T4 alone would be a strict improvement.
- **Length is fine.** 538 lines is navigable: every task states Files/Depends/DONE-WHEN in the same shape, and decisions are numbered and cited from tasks. Not a finding.
- Nothing in the working tree was modified.
