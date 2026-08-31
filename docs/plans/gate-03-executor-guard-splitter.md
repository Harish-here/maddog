# Gate-03: Executor-Guard Splitter Design Review Re-gate Ruling (Final Round)

**Date:** 2026-08-31

## VERDICT
**BLOCKED** — the fixed build converts two currently-DENIED irreversible commands into ALLOWs: the new `&` boundary is escape-blind, so `find . \& -delete` (denied today, verified live) splits into two harmless-looking segments. Everything else in the plan is sound and every prior finding is genuinely closed.

## PRIOR CLOSURE
| # | Status | Evidence |
|---|---|---|
| F1 `$(cmd)` contradiction | CLOSED | Decision 2 `:134-145` states `$`-prefix untouched incl. `$(rm …)` ALLOW; re-homed at `:179-183`, `:354-357`. Residual: still no probe row (gate-02 ruled closed; not re-opened) |
| F2 insertion point | CLOSED | `:105-111` names after `:286`, before `:288`, and rejects `:263` by name |
| F3 Q2 non-discriminating | CLOSED | `:291` says so verbatim, points at Q6 |
| F4 wrapper family | CLOSED | `:184-190`, `:349-353`, `:386-390` |
| F5 doc-comment target | CLOSED | Decision 6 `:209-222`, "NOT the file header" |
| F6 Q7 decorative live half | CLOSED | `:296` direct-only |
| F7 no `deny_writes=1` row | CLOSED | Q13 `:302`, executor-lead |
| F8 newline quote-blindness | CLOSED | `:165-168`, `:383-385`, DONE-WHEN `:264-266` |
| N1 escape-blind lookbehind | CLOSED | I ran the patched walk: Q14=2, Q15=1; also `echo "a\>"& …`=2, `echo a\\\>& …`=2 |
| N2 "all named in Scope" | CLOSED | All five Decision-4 bullets present at `:349-366` |
| N3 "three bypasses" | CLOSED | `:334` reads two |
| N4 unsearchable quote | CLOSED | Quote is `:98` text only — grep hits 1 |
| N5 raw vs masked token | CLOSED | Decision 2 tests `tokens_masked[0]` `:113-118` |

Anchors: all nine quoted snippets grep to exactly 1 hit at the stated lines; `      *)` is unique at :221. `i=$((i + 1))` has 6 hits (141,150,159,205,215,226) but is pinned by the `*)` anchor. Bash 3.2.57 confirmed; `${cmd:i+1:1}` and `case` globs ran clean on it — no Bash 4 construct anywhere.

## ESCAPE RULE TRACE
Buffer appends in `quote_walk`, against the claimed single point (after `esac` :225, before `i=$((i + 1))` :226):
- `*)` :222, `'` :167/171, `"` :177/181, `&` fallthrough :192, `|` :208, `;` :218 — **all reach it.** The point exists as claimed.
- Skipped by `continue`: in_single :138, in_double :145, word-mode blank :156, and the four chain splits (:187,:198,:203,:213).
- Staleness is harmless in both directions: the chain splits leave `buf=""`, and `case "" in *'>')` cannot match; the quote paths always append the **closing quote** last, so `buf` can never end in `>` on exit from a quote. Confirmed empirically — `echo '>'& rm …` → 2 segments, `echo "a\>"& rm …` → 2 segments (correct splits, not suppressed).

## NEW FINDINGS
1. **[load-bearing] `docs/plans/executor-guard-splitter.md:65-72` — the `&` boundary is escape-blind; the fix opens a hole it does not disclose.** Decision 1 enumerates exactly two exclusions and says the split "mirrors the existing `';')` case exactly" — and that case has no `esc` check. Verified: shipped guard **DENIES** `find . \& -delete` and `git clean -x \& -fd`; the patched walk splits both into `find . \` / ` -delete` and `git clean -x \` / ` -fd`, and each of those four segments fed to the shipped guard **ALLOWs**. `find . '&' -delete` really deletes `.` in bash. No probe row would catch this. *Clears when:* the split additionally requires `[ "$esc" -eq 0 ]` (already live at that arm — no new state), plus a direct row (`find . \& -delete` → 1 segment) and a live executor-fast row expecting DENY.
2. **[load-bearing] `:344-366` — the residual register, quoted verbatim into the PR, misses a class and understates another.** Confirmed live ALLOW on the shipped guard: `\rm -r <repo>`, `"rm" -r <repo>`, `r''m -r <repo>` — a quoted/escaped leading word defeats `cmd0` and matches none of the four named bullets. Separately `:352-353` calls `find . -exec rm -rf {} \;` "suspected but not demonstrated"; I demonstrated the class — `find . \; -delete` → **ALLOW** live. *Clears by:* adding a fifth bullet and re-labelling the `;` line confirmed.
3. **[cosmetic] `:65-66`, T1 DONE-WHEN `:253-267` — no word-mode guard stated for the new branch.** If the new split is not wrapped in `[ "$mode" = "chain" ]`, word mode emits a token line with no `\x1f`, silently blanking `tokens_masked` for that token and weakening every masked redirect check. *Clears by:* saying so in Decision 1, or one probe (`quote_walk word 'a&b'` → 1 token).

## IF BLOCKED
- **Owner decision:** finding 1 only — accept the new `find . \& -delete` hole as documented debt (which then must be stated in the Scope text), or add the one condition. The fix itself is one clause.
- **Mechanical:** finding 1's implementation + 2 probe rows, finding 2 (text only), finding 3 (one clause).

## DELEGATION LOG
executor-fast (haiku) — anchor/uniqueness grep sweep of nine snippets + `*)` arms + function bounds + bash version — returned raw counts and line numbers; all quoted anchors unique.

## NOTES
- Plan's Q6-Q10, Q14, Q15 all reproduce exactly on my patched copy of `quote_walk`; Q14/Q15 genuinely discriminate, and Q10+Q14+Q15 together pin the parity check (a no-lookbehind build fails Q10, an any-backslash build fails Q15).
- Unverified: the seven live rows (Q1-Q5, Q11-Q13) — reasoned from code, not dispatched; that is T1's DONE-WHEN.
- No ordinary command is newly *denied* beyond the acknowledged `(`/`{` cost. Escaped `&` in URLs (`curl 'h?a=1\&b=2'` unquoted) mis-splits harmlessly.
- The guard denied one of my own commands (`2>/dev/null`, `executor-guard.sh:523`); re-run without redirects. No repo file was written or modified.
