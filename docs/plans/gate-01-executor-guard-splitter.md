# Gate 01: Round 1 Design Review of executor-guard-splitter.md
**Date:** 2026-08-31

## VERDICT

**BLOCKED** — every load-bearing line citation in the plan is stale (one points *outside* the loop the new check must live in), Decision 2 contradicts itself and leaves a confirmed-live bypass it claims to close, and probe Q2's discrimination clause is false.

## STALE REFERENCES

| Plan citation | Accurate? | What it is now |
|---|---|---|
| `split_command` / `quote_walk chain`, `:97-219` (L15) | No | `quote_walk` is `:116-234`; `split_command` `:236-238` |
| `'&')` case at `:166-175` (L37, L126) | No | `:185-194`. `:166-175` is now the `"'"` (single-quote) case |
| New check "`:263` area, after tokenization" (L127) | No | `:263` is the `.cwd` comment, **before** the `while` loop (`:269`). Correct point is `:286-290` |
| Header `:1-49` documents the boundary set (L113, L128) | No, twice | Header block is `:1-65` and does **not** document the boundary set; that text is in `quote_walk`'s doc comment at `:98-101` |
| Here-string `:497` (L86) | No | `done <<< "$segments_raw"` is `:529`; `:497` is the `git checkout` case |
| Agent-scoping `case` at `:237` (L215) | No | `case` is `:251-257`, `*) exit 0 ;;` at `:256` |
| `2>&1`-glued-onto-`rm` confounds live ALLOW/DENY (L159-161) | Premise holds, mechanism drifted | 2.14.1's `normalize_path` now rejects the metacharacter and denies closed (`:322`); I confirmed `rm -r /private/tmp/claude-501/x 2>&1` → DENY vs. bare form → ALLOW |

## NEW FINDINGS

1. **[load-bearing] `docs/plans/executor-guard-splitter.md:57-58` vs `:69-73` — self-contradiction; a claimed-closed bypass stays open.** L57-58 says the "starts with unquoted `(`" rule "covers … a bare `$(cmd)` used as an entire leading word"; L69-73 says `tokens[0]` starting with `$` "is untouched by this rule". Both cannot hold. `$(rm -r …)` tokenizes to `$(rm` — starts with `$`, not `(` — so the rule as specified does **not** catch it. Confirmed live: `$(rm -r /Users/harishamutha/maddog-skills/agents)` → **ALLOW**; backtick form `` `rm -r …` `` → **ALLOW**. Clears when: L57 drops the `$(cmd)` claim and the row is either tasked (prefix test also matching `$(` and `` ` ``) or moved to Decision 4's named-not-tasked list, plus a probe row.
2. **[load-bearing] `:127` — the insertion point is on the wrong side of the loop.** `:263` is outside the `while IFS= read -r segment` loop, where `tokens`/`tokens_masked` do not exist. An executor anchoring to it writes dead or erroring code. Clears when the file reference names the point after `:286` (`[ "${#tokens[@]}" -eq 0 ] && continue`) and before `:294`.
3. **[load-bearing] `:166-169` (Q2) — the row does not discriminate.** I simulated the exact ordering pitfall Q2 names: it yields `[cd /tmp ]`, `[]`, `[ true ]`, `[ rm -r /repo]` — the `rm` segment is **intact**, `cmd0="rm"`, so the wrong build **also** DENYs. Q2 passes on both builds. (Q6 does catch it: wrong build → 3 lines, not 2.) Clears when Q2's clause is corrected or the row is replaced by a shape whose wrong-build result differs.
4. **[load-bearing] `:104-106`, `:209-211` — the residual-gap register omits its largest family.** Decision 4 names only argument-embedded substitution, assignment prefix, and keyword prefix (`if`, `time`, `!`). It does not name *wrapper commands*. All confirmed ALLOW live as `executor-fast`: `nohup rm -r <repo>`, `env rm -r <repo>`, `command rm -r <repo>`, `xargs rm -r <repo>`, `eval "rm -r <repo>"`, `sh -c "rm -r <repo>"`. Each is a full bypass of equal severity to Q1's. Clears when they are named in Decision 4 and the Risks list.
5. **[load-bearing] `:113-118` (Decision 6) — the update targets a block that does not contain the text.** Per stale-ref table row 4. Rewriting `:1-65` leaves the actually-wrong boundary-set sentence at `:98-101` ("splits … on unquoted `&&`, `||`, `;`, and `|`") intact and now doubly wrong. Clears when Decision 6 and T1's file list name `:98-115`.
6. **[cosmetic] `:172` (Q7) — the live half is decorative.** A build that split inside `"a & b"` yields `echo "a` / `b"`; neither segment is dangerous, so `executor-fast` ALLOWs either way. Only the direct segment-count half discriminates. Clears by dropping "+ live" or stating the row is direct-only.
7. **[cosmetic] `:29-32` vs probe table — no probe exercises `deny_writes=1`.** The plan asserts the defect hits all four identities including the file-write layer; all twelve rows run `executor-fast` or direct. The loop is shared, so risk is low, but T1's DONE-WHEN never tests the claim. Clears with one `executor-lead` row (e.g. `true & touch <scratchpad>/x` → DENY).
8. **[unverified assumption] `:74-94` (Decision 3) — the newline accident is quote-blind.** I confirmed the control (`true\nrm -r <repo>` → deny). Not tested: a newline *inside quotes* also acts as a boundary, so a multi-line quoted argument is judged as separate commands — a live false-positive source the plan blesses as "preserved". Clears by stating that in Decision 6's header text.

**Separator set / Bash 3.2 / path-guard-lib:** `;` `|` `&&` `||` `&` + newline is complete for *boundaries*; every remaining escape I found is `cmd0`-derivation (finding 4), not splitting. The `&>` lookahead and `>&`/`2>&1` lookbehind exclusions are sound — I could not construct a real background `&` whose preceding buffer char is `>`. `((x++))`/`(cd x && ls)`/`{ …; }` are the only newly-denied ordinary forms, all acknowledged. No Bash 4 construct is required (`${buf: -1}`, `${cmd:i:1}`, `case` globs are 3.2-clean; confirmed 3.2.57). The change is orthogonal to `scripts/path-guard-lib.sh` — the new `tokens[0]` check runs strictly *before* the `rm` path logic and only reduces calls into `normalize_path`; no accounting needed beyond the drifted note in the stale table.

**Catch-all ruling (`:213-222`):** leaving it untasked is **defensible**. `*) exit 0 ;;` is fail-open by design — the main conversation must not be guarded (`scripts/executor-guard.sh:50-51`) — so it is a registration dependency, not a defect in the splitter's blast radius. One correction: the observation should say fail-open is intentional for unlisted callers, so a later reader does not close it as a bug.

## DELEGATION LOG

none — all evidence gathered by own Bash (guard invoked with synthetic PreToolUse payloads; no command under test was executed).

## NOTES

- Working tree unmodified; no file written. The guard did not deny any of my own commands (`cmd0` was `printf`/`for`/`bash`/`jq` throughout).
- Suspected but **not demonstrated**: `find . -exec rm -rf {} \;` — chain mode splits on the escaped `;` without an `esc` check (`scripts/executor-guard.sh:211`), and `cmd0="find"` with no `-delete`. Pre-existing, outside this plan's stated scope; I did not run it.
- Unverified: whether any repo workflow issues a leading `(` or `{` command that the fail-closed rule would newly deny. I did not sweep `workflows/`.
