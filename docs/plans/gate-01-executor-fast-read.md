# Round 1 Design-Review Ruling on `docs/plans/executor-fast-read.md` (2026-08-31)

MODE: DESIGN-REVIEW
STATUS: done

## VERDICT
**BLOCKED** — T3 cannot deliver decision 6 as written (its DONE-WHEN pins containment to a string test that is not session-scoped, while the actual mechanism sits unanswered in OPEN QUESTIONS), and the plan leaves five shipped by-name consumers of the three removed modes untouched and un-exempted.

**Feasibility answer up front: decision 6 IS buildable.** A hook can learn the session scratchpad. Verified first-hand: `CLAUDE_CODE_SESSION_ID=33fb7a5e-ca43-48ef-8e70-259319f83be5` is present in the subagent's process environment and is exactly the uuid segment of this session's scratchpad path; the layout is `/private/tmp/claude-<uid>/<cwd-with-slashes-as-dashes>/<session-uuid>/scratchpad` (confirmed by `ls /private/tmp/claude-501/*/`), and PreToolUse payloads already carry `.cwd` and `.session_id`. So the inputs exist — the plan is underspecified, not unbuildable. Caveat: the layout is an undocumented convention and no env var carries the path itself.

## FINDINGS

1. **BLOCKER — T3 as written does not deliver decision 6.** `docs/plans/executor-fast-read.md:142-143` requires reusing `is_temp_path()` (`scripts/executor-guard.sh:63-72`), a pure string-component match that ALLOWS `/tmp/*`, `/var/folders/*`, any *other* session's scratchpad, and any repo path containing a `scratchpad` component. Decision 6 (`:47-49`) says *the session* scratchpad. Compounding: `:375-377` leaves the resolution mechanism in OPEN QUESTIONS while `:3` declares the plan frozen and executable. Clear it: name the mechanism (session_id + cwd derivation), and rewrite T3's DONE-WHEN to a session-scoped prefix test after real-path resolution.

2. **BLOCKER — shipped consumers of the removed modes are neither updated nor exempted.** `workflows/sdd-task-loop.js:205` dispatches `executor-fast` for `brief-lint` ("lint these briefs for execution-readiness… only readiness") — a VERIFY-shaped task the trimmed hand can no longer classify; `agents/product-pm.md:40`, `agents/product-ux.md:22`, `agents/product-be.md:26`, `agents/product-ui.md:25` dispatch it by name for RECON/enumeration. Decision 13 (`:67-71`) exempts only `product-qa`. Clear it: add a task retargeting these, or extend the out-of-scope list explicitly.

3. **MAJOR — T7 is scoped too narrowly to keep the judge coherent.** `agents/executor-judge.md:14-15` (frontmatter description), `:31` and `:33` all name `executor-fast`; T7 (`plan:227-238`) touches only the DELEGATION section and its DONE-WHEN checks only that section. Post-T5 the shipped description would advertise a dispatch the guard denies.

4. **MAJOR — the READY step is misstated and drops its load-bearing clause.** `plan:288` asserts `executor-fast-read` "must appear in both" manifests; `.claude-plugin/plugin.json` enumerates no agents at all (verified — no agents key). The plan also omits §2 step 3's "Repo-wide grep sweep for by-name cross-references to anything added, renamed, or removed" (`.claude/skills/release/SKILL.md`, READY step 3) — the exact check that catches Finding 2.

5. **MAJOR — T6 violates the eval coverage rule.** `evals/README.md:83-87` requires a happy and a trap fixture for every mode *and every standing law*; T6's DONE-WHEN (`plan:216-220`) requires only 6 migrated + ≥4 guard fixtures, leaving the new hand's three standing laws (DISTILLED RETURN, FAITHFUL REPORT, STOP UP) with none — `evals/executor-fast.json` carries `fast-distilled-01`, `fast-faithful-01`, `fast-andon-01/02` for the equivalent.

6. **MAJOR — the new fixture file is invisible to the eval harness.** `.claude/workflows/agent-evals.js:55` (`AGENTS` default), `:65` (`RUN_MODEL` "CLOSED mapping"), `:134` ("Read these four fixture files") hard-name four agents; no task updates them, so T3's fixtures — declared the *only* accepted evidence (`plan:329`) — never run under the workflow.

7. **MINOR — id churn against a stated rule.** `evals/README.md:61` "Never renumber — results are tracked by id"; `evals/last-run.md` exists, so results are on disk. `plan:186-189` renames `fast-recon-01` → `fastread-recon-01`; the Risks note (`:344-348`) asks for traceability but T6's DONE-WHEN does not require it.

8. **MINOR — T1's content spec writes runtime mechanics into a shipped body.** `plan:102-104` instructs the body to name the Write tool and the scratchpad; `CLAUDE.md` §Invariants (adapter set) says shipped bodies name capabilities, never runtime tool identifiers. T1's DONE-WHEN requires a CLEAR review-agent verdict, so this stalls T1.

9. **MINOR — T7's reduction baseline is wrong.** DELEGATION is `agents/executor-judge.md:96-120` (25 lines); `plan:58` and `:227` cite 96-129 / "~33 lines", mistaking the return contract's `DELEGATION LOG:` (`:129`) for the section end. A line-count DONE-WHEN measured against a phantom baseline is unfalsifiable.

10. **MINOR — T4 leaves the guard's own denial text wrong.** `plan:155-157` updates only the header; `scripts/executor-guard.sh:420,425,428` tell the denied agent to "route the change through an executor that holds Write/Edit" — the read hand holds Write. `CLAUDE.md` §Invariants also still names two agents in the write-denial set and is not in any task.

11. **MINOR (unverified assumption) — `.agent_type` on Write payloads.** `scripts/judge-dispatch-guard.sh:11-17` confirms payload shape for `Agent`; `executor-guard.sh` relies on it for `Bash`. Presence on a `Write` payload is assumed, never captured. If absent, T3 fails open and containment silently vanishes.

## DELEGATION LOG
none — all evidence read or run first-hand.

## NOTES
- Task ordering itself holds: T1 → T2/T3/T4/T5 → T6/T7 → T8 → T9, and T9 merges T1-T8 as one candidate branch, so the window where the retargeted guard and the judge's unshrunk prose disagree is intra-branch only. Not a finding.
- Unverified: whether hook config (`hooks/hooks.json`) reloads on the same schedule as agent files under a plugin update — `CLAUDE.md` §Distribution mechanics documents skills-live/agents-need-reload but is silent on hooks, so a mixed-state session after the release is possible and untested.
- Unverified: `evals/README.md:75` says "There is no runner yet" while `.claude/workflows/agent-evals.js` exists; I did not reconcile which is authoritative, and Finding 6 holds either way (by-hand execution remains available).
- Nothing in the working tree was modified.
