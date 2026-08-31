# Plan: executor-guard-splitter — fix the command-splitting defect

STATUS: frozen, ready to execute. Revised to address every finding in
`docs/plans/gate-01-executor-guard-splitter.md` (F1-F8, all applied or
rejected with evidence), every finding in
`docs/plans/gate-02-executor-guard-splitter.md` (N1-N5, all applied),
and every finding in `docs/plans/gate-03-executor-guard-splitter.md`
(1-3, all applied — see those files for the original rulings). Split
out per owner decision: this defect
(`docs/plans/gate-03-executor-guard-normalization.md` finding 3) is
more severe than the path-normalization defect
`docs/plans/executor-guard-normalization.md` fixes — that plan narrows
which paths a matched `rm` is allowed to touch; this plan fixes whether
the dangerous command is ever matched at all. **This plan ships FIRST.**
Neither plan merges with, restates, or depends on the other beyond this
ordering. Decisions are CLOSED — do not redesign.

## Anchoring convention (read this before touching any citation below)

Every file reference in this plan is anchored by **function name plus
a verbatim quoted snippet** from `scripts/executor-guard.sh`; the line
number is a secondary hint only, written "(currently around :NNN)".
Line numbers drift on every merge that touches the file — release
2.14.1 moved 56 lines and every citation in this plan's first pass went
stale, which is what blocked it. A quoted snippet does not drift: if
the line number is wrong, search the file for the quoted text — inside
the named function, it should still be unique. When you edit this plan
later, keep this convention; do not revert to line-number-only
citations.

## Why this exists

`scripts/executor-guard.sh` decides what a command does by inspecting
the FIRST WORD (`cmd0`) of each segment that `quote_walk` in `chain`
mode produces (function `quote_walk`, currently `:116-234`; the
`split_command` wrapper that calls it, currently `:236-238`). Verified
live and by direct function call against the unmodified script
(2026-08-31):

- A single `&` (background operator) is never recognized as a boundary
  — `&` only splits when the *next* char is also `&`, inside the `'&')`
  case (currently around `:185-194`). `true & rm -r <repo>` stays ONE
  segment, `cmd0="true"`, the `rm` is never examined. **ALLOWED —
  confirmed live.**
- A subshell `(cmd)` and a brace group `{ cmd; }` are not recognized as
  command boundaries at all. `(rm -r <repo>)` tokenizes to `cmd0="(rm"`;
  `{ rm -r <repo>; }` tokenizes (after its internal `;` split, which
  *is* already handled) to `cmd0="{"` on the first sub-segment. Neither
  equals `"rm"`. **ALLOWED — confirmed live and by direct tokenization.**

This applies to all four guarded identities: `executor-fast` and
`executor-smart` (irreversible-command denial) and `executor-lead` /
`executor-judge` (both layers — the write-denial block keys off the
same `cmd0`/token derivation).

## Decisions

1. **Single `&` becomes a chain-mode segment boundary, gated to chain
   mode, with two exclusions — one of which must be escape-aware — plus
   the boundary itself must require the `&` be unescaped.** In
   `quote_walk`'s `chain` mode, the existing `'&')` case — the block
   beginning `'&')` and containing the line
   `if [ "$mode" = "chain" ] && [ "${cmd:i:2}" = "&&" ]; then`
   (currently around `:185-194`) — currently: splits on `&&` (2 chars),
   otherwise falls through and appends `&` as a literal character.
   Change the fallthrough: a bare, unquoted, **unescaped** `&` in
   **chain mode only** splits the segment (mirrors the existing `';')`
   case exactly — close current buffer, skip 1 char, start a new
   segment) UNLESS either holds:
   - the **next** character is `>` (the `&>`/`&>>` redirect forms), or
   - the **last character already written to the current buffer** is
     an **UNESCAPED** `>` (the `>&`, `2>&1`, `1>&2`, `>&-`
     fd-duplication/close forms). An escaped `\>` is a literal
     character inside an argument, not a redirect operator — the `&`
     immediately after it is a genuine background operator and must
     still split. Gate 02 demonstrated the gap in this plan's first
     pass: simulated against a bare one-character lookback with no
     escape awareness, `echo a\>& rm -r <repo>` stays ONE segment
     (`cmd0="echo"`, `rm` never examined), while a real shell runs
     both commands — `bash -c 'echo a\>& echo SECOND_COMMAND_RAN'`
     printed `a>` then `SECOND_COMMAND_RAN`.

   **New guard, gate-03 finding 1 (load-bearing) — the `&` itself must
   be unescaped.** The two exclusions above are about what surrounds
   the `&`; this is about the `&` character's own escape state, and is
   a separate condition, checked alongside them: the boundary-split
   fires only when `[ "$esc" -eq 0 ]` at the iteration where `c` is
   `&` — `esc` is the loop's existing escape-parity variable (see
   `:120-135`), already live and computed at the top of every loop
   iteration before this `case "$c" in` runs, so no new variable is
   needed for this one. Without it, an escaped `\&` (a literal `&`
   character inside an argument, e.g. `find`'s own operand syntax) is
   treated the same as a genuine background operator and split anyway.
   Confirmed live against the unmodified script (2026-08-31): the
   shipped guard (which never splits on a bare `&` at all, escaped or
   not) **DENIES** `find . \& -delete` (cmd0 `find`, token `-delete`
   present) and **DENIES** `git clean -x \& -fd` (cmd0 `git clean`,
   flags `-x` and `-fd` both present in one segment). Simulated against
   Decision 1 as drafted before this guard existed: both split into two
   fragments — `find . \` / `-delete` and `git clean -x \` / `-fd` —
   and each fragment ALLOWs on its own (the `-delete`/`-fd` token lands
   in a segment whose `cmd0` is no longer `find`/`git`). Requiring
   `esc -eq 0` on the `&` itself closes this; Q16 and Q17 below are the
   evidence.

   **New guard, gate-03 finding 3 (cosmetic) — chain-mode only.** The
   entire bare-`&` boundary-split arm above (both exclusions and the
   new `esc -eq 0` check) must be conditioned on `[ "$mode" = "chain" ]`
   the same way the existing `&&` check already is — not left to run
   unconditionally the way the pre-existing literal-append fallthrough
   does. `quote_walk`'s `&` case is shared code, reached in `word` mode
   too (tokenizing one already-chain-split segment into arguments); a
   residual `&` that survives into a segment (inside the `&>`/`>&`
   exclusion shapes, or an escaped `\&`) is still visited by this same
   case arm during word-mode tokenizing. If the new split logic is not
   itself gated to chain mode, it would still be reachable in principle
   there; `out+=("$buf")` in that branch omits the `${US}${mbuf}`
   separator word-mode tokens require, so the tokenizer's
   `while IFS=$'\x1f' read -r tok_lit tok_masked` loop reads a line
   with no separator, assigns the whole thing to `tok_lit`, and leaves
   `tok_masked` empty for that token — silently blanking
   `tokens_masked` at that index and defeating every masked check
   (`awk`'s `>` scan, the bare-redirect scan) for it. Q18 below is the
   evidence: `quote_walk word 'a&b'` called directly must return
   exactly 1 output line (one token, unsplit, separator intact) — a
   build that omits the mode gate returns 2.

   **RETRACTED from this plan's first pass:** the claim that "no new
   state variable is needed" for these two exclusions. That is wrong
   for the lookbehind. By the time the walk reaches `&`, the loop's
   `esc` variable already describes `&` itself, not the earlier `>` —
   a bare last-character check on `buf` cannot recover whether that
   `>` was escaped at the moment it was written. Add one new state
   variable — e.g. `buf_last_esc` — set to the current iteration's
   `esc` value at the single point every non-`continue` path through
   the walk already reaches after appending a character to `buf`:
   immediately after the default `*)` case arm (the line reading
   exactly `      *)`, currently around `:221`, the last arm before
   this `case "$c" in`'s closing `esac`) and before the loop's
   `i=$((i + 1))` (currently around `:226`). This reuses the
   escape-parity mechanism (`esc`/`esc_next`) already computed for
   quote handling (currently around `:120-135`) — it is bookkeeping
   for that existing parity, not a second parser. The lookbehind
   exclusion then reads: last buffer char is `>` **AND**
   `buf_last_esc` is `0`. The lookahead exclusion (next character is
   `>`) needs no such state — it inspects `cmd` directly, not `buf`.

   Both exclusion checks, the `esc -eq 0` guard on the `&` itself, and
   the `mode = "chain"` guard all run after the `&&` check, which is
   unaffected; order them before the boundary split.
2. **Fail-closed rule for subshells and brace/paren groups (resolves
   finding 3's second and third probes).** After a segment is
   tokenized (`quote_walk word` mode) into `tokens`/`tokens_masked`,
   insert the new check INSIDE the segment loop: after the line
   `[ "${#tokens[@]}" -eq 0 ] && continue` (currently around `:286`)
   and before the line `cmd0="${tokens[0]##*/}"` (currently around
   `:288`). NOT the `.cwd` comment area near `:263` — that point sits
   outside the loop that begins at the line `while IFS= read -r
   segment; do` (currently around `:269`); `tokens`/`tokens_masked` do
   not exist there.
   Test `tokens_masked[0]` — the masked companion `quote_walk word`
   mode already builds alongside `tokens[0]`, with every character
   consumed inside a quote replaced by `Q` (see the function comment,
   currently around `:105-108`). Testing the masked copy, not the raw
   `tokens[0]`, is what makes this an UNQUOTED check: a quoted leading
   `(` or `{` would appear as `Q` in `tokens_masked[0]`, not as the
   literal character, and so would not match. (`tokens[0]` itself is
   the RAW literal token, not `cmd0` which has already had a path
   prefix stripped — keep using `tokens[0]`, not `cmd0`, everywhere
   else in this rule; only the quote test reads the masked array.) If
   `tokens_masked[0]` starts with `(` (covers `(cmd)` subshells and
   `((expr))` arithmetic commands), OR `tokens_masked[0]` is exactly
   `{` (covers `{ cmd; }` brace groups) — deny the segment outright
   with a "cannot confidently identify the leading command" reason,
   the same fail-closed shape the brief
   requires, rather than attempting to parse inside the group. This is
   deliberately blunt: it also denies a harmless bare `((x++))` (Q5
   documents this as an accepted false-positive cost, not a defect)
   and a harmless `(cd x && ls)`. An agent that hits this denial
   rewrites the command without the wrapper — the guard does not need
   to see inside a subshell to do its job, only to never silently skip
   past one.
   **What this rule does NOT touch (verified — must not regress):**
   `tokens[0]` starting with `$` (parameter expansion `${VAR}`,
   command substitution `$(cmd)`, arithmetic expansion `$((expr))`)
   does not start with a bare `(` and is untouched by this rule —
   INCLUDING a bare `$(rm -r <repo>)` (or backtick `` `rm -r <repo>` ``)
   used as the entire leading word. Confirmed live: **ALLOW**. This is
   a real, confirmed-live bypass that this rule does not close; per the
   owner decision it is not widened into this plan — see Decision 4
   and "Scope: what this closes, and what remains open" below. A `(`
   or `{` appearing in a NON-leading token (e.g. `echo $(date)`, `cp
   {a,b} dst`) is likewise untouched, since the check inspects
   `tokens[0]` only.
3. **Newline — verify, correct the citation, preserve by construction,
   note the quote-blind gap.** Confirmed live and by direct call: a
   literal newline embedded in `.tool_input.command` DOES cause a
   segment split today (`true\nrm -r <repo>` → DENY, matching the plain
   `rm -r <repo>` control). `quote_walk`'s `chain`-mode case statement
   has NO explicit branch for `\n` — it falls to the default `*)` case
   and is appended into the buffer as an ordinary character, quote-state
   and all. The split happens one layer up: each finished segment is
   printed via `printf '%s\n' "${out[@]}"` and re-consumed by a
   line-oriented `while IFS= read -r segment` loop, fed by the
   here-string on the line `done <<< "$segments_raw"` (currently
   around `:529`, not the mechanism itself — merely the outer loop that
   inherits this side effect); a literal newline *inside* one buffered
   segment is byte-for-byte indistinguishable from the record
   terminator `printf` appends, so it silently acts as a segment
   boundary regardless of quote state. **This plan does not change
   that mechanism.** Task 1's diff must not strip, join, or otherwise
   normalize embedded newlines inside `quote_walk`'s chain-mode buffer
   — doing so would silently remove a protection that currently works
   by accident. Because the boundary is quote-blind, a multi-line
   *quoted* argument is judged as separate commands the same as an
   unquoted one — a known false-positive source this plan accepts, not
   fixes; Decision 6's doc-comment update must state it. No probe row
   is needed to prove no-regression here beyond the existing control
   already run above (recorded, not retested per row).
4. **Scope boundary — named, not tasked (owner decision: fix the
   splitter only; do not widen this plan to wrapper commands or
   command substitution).**
   - Command substitution (`$(...)`, backticks) and process
     substitution (`<(...)`, `>(...)`) used as an ARGUMENT (not the
     segment's leading token) embed a runnable command inside a word
     rather than at a segment boundary — a different escape category
     (argument-embedded execution) from "command splitting."
   - Command substitution/backticks used as the ENTIRE LEADING WORD
     (`$(rm -r <repo>)`, `` `rm -r <repo>` ``) is the confirmed-live
     bypass named in Decision 2's regression note — `tokens_masked[0]`
     starts with `$` or `` ` ``, not `(`, so Decision 2's rule does not
     match it. Same "not tasked" category.
   - Wrapper commands run the dangerous command as an argument or
     subprocess of a different first word, which is a `cmd0`-derivation
     gap, not a segment-boundary gap. All confirmed ALLOWED live as
     `executor-fast`: `nohup rm -r <repo>`, `env rm -r <repo>`,
     `command rm -r <repo>`, `xargs rm -r <repo>`, `eval "rm -r
     <repo>"`, `sh -c "rm -r <repo>"`, `$(rm -r <repo>)`, and the
     backtick form.
   - **CONFIRMED** (gate-03 finding 2, relabelled from "suspected"):
     `find . -exec rm -rf {} \;` — chain mode splits on the escaped `;`
     with no escape (`esc`) check (pre-existing, not touched by this
     plan), and the command's own first word is `find` with no
     `-delete` (the only `find` check this guard has), so neither the
     recursive-delete check nor the `find -delete` check fires.
     Demonstrated live via `find . \; -delete` → ALLOW on the
     unmodified script.
   - Likewise, a leading word obscured by a variable-assignment prefix
     (`x=$(rm -r /)`) or a keyword prefix (`if`, `time`, `!`) is a
     `cmd0`-derivation gap, not a segment-boundary gap — a different
     defect class, not tasked here.
   - **Escaped or quoted leading words** (gate-03 finding 2, new
     bullet): `cmd0` keeps a leading escape/quote character verbatim,
     defeating the `"rm"`/`"find"`/`"git"` equality checks. Confirmed
     ALLOWED live as `executor-fast`: `\rm -r <repo>`,
     `"rm" -r <repo>`, `r''m -r <repo>`. A `cmd0`-derivation gap, not a
     segment-boundary gap.
   All of the above are named in "Scope: what this closes, and what
   remains open" below, worded for direct reuse in the release PR body.
5. **Proof standard.** Same as the sibling plan: direct function
   probes (calling `quote_walk`/`split_command` directly, checking
   segment count) prove the parsing primitive; live probes (dispatched
   with `agent_type: executor-fast` or `executor-lead`, run and
   recorded by hand) prove the end-to-end ALLOW/DENY outcome. Both are
   required per probe-table row where marked.
6. **Doc-comment update (NOT the file header block).** The file's top
   header block (currently `:1-65`) does NOT document the
   segment-boundary set — verified against the ruling that blocked
   this plan's first pass. That sentence instead lives inside
   `quote_walk`'s own function doc comment, in the `mode="chain"`
   bullet starting with the line `splits a full command into
   pipeline/chain segments on` (currently `:98`, the bullet continues
   through `:101`). Update THAT sentence — not the header — to state
   the full boundary set
   (decision 1's `&`/`;`/`&&`/`||`/`|` plus decision 2's fail-closed
   subshell/group rule) and decision 3's newline mechanism (accidental,
   preserved, not a designed case branch, and quote-blind — a
   multi-line quoted argument can be misjudged as multiple commands) —
   so the next reader does not have to re-derive either from the diff.

## Task list

**T1 — Fix `split_command`'s `&` handling + add the fail-closed
subshell/group rule** [executor-smart BUILD, gated by review-agent —
GATE-INFRA]
- Files: `scripts/executor-guard.sh` — the `'&')` case inside
  `quote_walk`'s `chain` mode (currently around `:185-194`, quoted
  snippet in Decision 1); the new `buf_last_esc` state update after
  the default `*)` case arm (currently around `:221-226`, quoted
  snippet in Decision 1); the new check inserted inside the segment
  loop, between the lines quoted in Decision 2 (currently around
  `:286`-`:288`, testing `tokens_masked[0]` per Decision 2's revised
  wording); the `mode="chain"` doc-comment sentence inside
  `quote_walk`'s function comment (currently `:98-101`, per Decision
  6).
- Depends on: none.
- Bash 3.2 constraint (this repo's target, confirmed
  `bash --version` → 3.2.57): the exclusion checks (lookahead char,
  last-buffer-char, the new `buf_last_esc` assignment) and the
  `tokens_masked[0]` prefix/equality tests are all 3.2-clean
  glob/case matching — no `mapfile`, associative array, or `${var,,}`
  needed.
- **Implementation trap (Gate 02):** `${buf: -1}` (with the space) is
  the last character of `buf`; `${buf:-1}` (no space) is Bash's
  default-value substitution and silently means something else
  entirely — the two are one keystroke apart and the bug produces no
  syntax error. Use a `case "$buf" in *'>') ... ;; esac` form for the
  lookbehind instead of `${buf: -1}` string comparison, to avoid the
  hazard outright rather than relying on getting the spacing right.
- DONE-WHEN:
  - `bash -n scripts/executor-guard.sh` passes;
  - every "direct" row in the probe table below, called directly
    against `quote_walk`/`split_command` (no live dispatch), returns
    its expected segment count — including Q14 and Q15, the two
    escape-parity rows, and Q16-Q18 (gate-03 findings 1 and 3);
  - every "live" row, dispatched with the stated agent identity
    against the live script, returns its expected ALLOW/DENY;
  - the lookbehind exclusion denies the split only when the buffer's
    trailing `>` is unescaped (`buf_last_esc` is `0`) — Q14 and Q15
    together are the evidence for this;
  - the boundary split itself fires only when the `&` character is
    unescaped (`esc` is `0` at that iteration) — Q16 and Q17 together
    are the evidence for this (gate-03 finding 1);
  - the boundary split is reachable only in `mode = "chain"` — Q18 is
    the evidence for this (gate-03 finding 3);
  - the `mode="chain"` doc-comment sentence (Decision 6's target,
    NOT the file header) states the full boundary set and the newline
    mechanism including its quote-blindness;
  - review-agent verdict CLEAR.

**T2 — Release** [release skill, all six phases — GATE-INFRA surface:
`scripts/`]
- Files: none directly.
- Depends on: T1 merged to the candidate branch.
- READY re-runs the full probe table live (not `bash -n` alone).
- DONE-WHEN: PR open citing a RULE verdict naming the PR's head commit;
  user merges; SEAL posts tag + CI result. The PR body should quote
  "Scope: what this closes, and what remains open" below verbatim.

## Probe table

`<repo>` = this repo's absolute path; `<scratchpad>` = a scratchpad dir
under `/private/tmp/claude-*`. "Direct" = called against
`quote_walk`/`split_command` directly (segment count only — sidesteps
an unrelated, pre-existing gap where a redirect token glued onto an
`rm` argument list is misread as a bogus path by the recursive-delete
check, confounding live ALLOW/DENY for redirect-only shapes). "Live" =
dispatched end-to-end with the stated agent identity.

| ID | Shape | Agent identity | Verified at | Expected | Discriminates |
|---|---|---|---|---|---|
| Q1 | `true & rm -r <repo>` | executor-fast | live | DENY | wrong build never splits a lone `&`; whole string is one segment, `cmd0="true"`, the `rm` is never examined → ALLOWs. |
| Q2 | `cd <scratchpad> && true & rm -r <repo>` (mixes `&&` and a bare `&`) | executor-fast | live | DENY | control only, does NOT discriminate build correctness: simulated against the misordered build, the `rm` segment still ends up intact with `cmd0="rm"`, so a wrong build ALSO denies here. Kept as an end-to-end sanity check that the dangerous segment is denied regardless of split boundaries; **Q6 is the row that actually discriminates the `&`/`&&` ordering pitfall.** |
| Q3 | `(rm -r <repo>)` | executor-fast | live | DENY | wrong build has no fail-closed check for a leading unquoted `(`; `cmd0` is `"(rm"`, never `"rm"` → ALLOWs. |
| Q4 | `{ rm -r <repo>; }` | executor-fast | live | DENY | wrong build has no fail-closed check for a lone `{` token; `cmd0` is `"{"`, never `"rm"` → ALLOWs. |
| Q5 | `((x++))` (bare arithmetic; no dangerous payload — documents the accepted false-positive cost) | executor-fast | live | DENY | wrong build matches only an EXACT `(` token, not "starts with"; the glued, space-free `((x++))` token fails an equality test and ALLOWs, showing the rule must be a prefix match. |
| Q6 | `true && rm -r <scratchpad>/x` | n/a | direct (segment count) | 2 segments | wrong build's new bare-`&` logic fires on the first `&` of `&&` before checking the second char, producing 3 segments or a corrupted split instead of 2 — this is the row that catches the `&`/`&&` ordering pitfall Q2's shape does not. |
| Q7 | `echo "a & b"` | n/a | direct (1 segment) | 1 segment (parsing correctness only — no live check: neither possible split makes any resulting segment dangerous, so `executor-fast` would ALLOW either way and the live half is decorative) | wrong build checks for a bare `&` before the existing quote-state branches, splitting inside the quoted string into 2 segments instead of 1. |
| Q8 | `printf x &>/dev/null` | n/a | direct (1 segment) | 1 segment (parsing correctness, not danger) | wrong build treats every unquoted `&` not forming `&&` as a boundary with no lookahead for `>`, splitting `&>` into two segments. |
| Q9 | `printf x &>>/tmp/log` | n/a | direct (1 segment) | 1 segment | same as Q8, for the two-character `>>` after `&`. |
| Q10 | `rm -r <scratchpad>/x 2>&1` | n/a | direct (1 segment) | 1 segment | wrong build has no lookbehind for a preceding `>`; it splits `>&` into two segments (`"...2>"`, `"1"`). |
| Q11 | `cp {a,b} <scratchpad>/` | executor-fast | live | ALLOW | wrong build's fail-closed rule matches `{` anywhere in any token, not just `tokens[0]`, and denies ordinary brace expansion. |
| Q12 | `echo $(date)` | executor-fast | live | ALLOW | wrong build's fail-closed rule matches an unquoted `(` anywhere in the command, not just at `tokens[0]`, and denies ordinary command substitution used as an argument. |
| Q13 | `true & touch <scratchpad>/x` | executor-lead (`deny_writes=1`) | live | DENY | exercises the file-write-denial layer, which shares the same segment/token derivation: wrong build never splits the lone `&`; whole string is one segment, `cmd0="true"`, `touch` is never examined by the write-denial checks → ALLOWs. |
| Q14 | `echo a\>& rm -r <repo>` | n/a | direct (segment count) | 2 segments | wrong build's lookbehind sees the buffer's trailing character is `>` and stops there, with no memory of the backslash that preceded it — it treats an escaped `\>` the same as a genuine redirect `>`, suppresses the split, and produces 1 segment (`cmd0="echo"`, `rm` never examined) — a real shell runs both commands (`bash -c 'echo a\>& echo SECOND_COMMAND_RAN'` printed `a>` then `SECOND_COMMAND_RAN`). |
| Q15 | `printf x 2\\>&1` | n/a | direct (segment count) | 1 segment | confirms the escape-aware fix does not over-correct: the doubled backslash collapses to one literal backslash under escape parity, leaving the `>` genuinely UNESCAPED before `&` — a real `>&` redirect that must still suppress the split; a build that disqualifies the lookbehind on any preceding backslash, rather than checking parity, wrongly splits this into 2 segments. |
| Q16 | `find . \& -delete` | n/a | direct (segment count) | 1 segment | gate-03 finding 1: wrong build has no `esc -eq 0` guard on the `&` itself, so an escaped `\&` (a literal argument character, not a background operator) still splits, corrupting the segment so `-delete` lands away from `cmd0="find"`. |
| Q17 | `find . \& -delete` | executor-fast | live | DENY | gate-03 finding 1, live confirmation: shipped guard DENIES this today (verified); a wrong build's escape-blind split turns it into two ALLOWed fragments. |
| Q18 | `quote_walk word 'a&b'` (direct function call, word mode, no chain split first) | n/a | direct (output line count) | 1 output line | gate-03 finding 3: wrong build does not gate the new bare-`&` split to `mode = "chain"`, so it also fires during word-mode tokenizing; the resulting `out+=("$buf")` line has no `${US}${mbuf}` separator, so `tokens_masked` silently ends up empty for that token instead of `1` line containing `a&b${US}a&b`. |

18 rows total (Q1-Q18). Newline (decision 3) is a recorded control, not
a numbered row — already confirmed against the unmodified script and
unaffected by this plan's diff.

## Release sequence

Per `.claude/skills/release/SKILL.md` §0: `scripts/` is GATE-INFRA, so
the INTERNAL/DOCS-only shortcut does not apply — full six phases,
identical shape to the sibling plan's release sequence:

1. **DECLARE**: sync to `origin/main`; fix → patch-rec; user rules the
   bump; version + CHANGELOG commit.
2. **READY**: `bash -n`; the full probe table above, run live; CHANGELOG
   check.
3. **BEHAVIOR**: not description-routing-relevant (no agent frontmatter
   touched) — record as not applicable.
4. **RULE** (executor-judge, fix-less): one adversarial release-review;
   evidence = candidate diff, READY results, the probe table. Verdict
   CLEAR or BLOCKED naming head SHA.
5. **SHIP**: push candidate branch; open/update PR citing the RULE
   verdict and every READY result, quoting "Scope: what this closes,
   and what remains open" below in the PR body. STOP — never merge;
   user merges.
6. **SEAL**: tag `vX.Y.Z`; `claude plugin tag --push`; confirm CI green;
   post SEAL comment on the merged PR.

## Scope: what this closes, and what remains open (quote directly into the PR body)

This change closes two splitting-primitive bypasses: a bare background
`&` no longer hides a trailing command from inspection, and a subshell
`(...)`, brace group `{ ...; }`, or arithmetic command `((...))` used
as the leading word of a segment is now denied fail-closed instead of
silently passing through as an unrecognized `cmd0`. The `&>`/`>&`
redirect-form exclusions close no bypass by themselves — they exist so
the new `&` boundary does not mis-split an ordinary redirect
(`2>&1`, `&>/dev/null`) into a false-positive denial; without them
this fix would trade one class of defect for a class of noise.

It does **not** close the following. All are confirmed or suspected
live against the unmodified script and are named here in full because
this section is quoted verbatim into the release PR body:
- **Wrapper commands** run the dangerous command as an argument or
  subprocess of a different first word — a `cmd0`-derivation gap, not
  a segment-boundary gap. Confirmed ALLOWED live as `executor-fast`,
  unchanged by this fix: `nohup rm -r <repo>`, `env rm -r <repo>`,
  `command rm -r <repo>`, `xargs rm -r <repo>`, `eval "rm -r <repo>"`,
  `sh -c "rm -r <repo>"`. **Confirmed** (gate-03 finding 2, relabelled
  from "suspected"): `find . -exec rm -rf {} \;` — demonstrated live
  via `find . \; -delete` → ALLOW on the unmodified script: chain
  mode's `;` case has no escape check (pre-existing, not touched by
  this plan), so an escaped `\;` still splits, and separately `find`'s
  only check is for a bare `-delete` token, which `-exec rm -rf {} \;`
  never contains.
- **Command substitution/backticks used as the entire leading word**
  (`$(rm -r <repo>)`, `` `rm -r <repo>` ``) — confirmed ALLOWED live.
  `tokens_masked[0]` starts with `$` or `` ` ``, not `(`, so decision
  2's fail-closed rule does not match it.
- **Argument-embedded command or process substitution** — a runnable
  command inside a word rather than at a segment boundary: `echo $(rm
  -r <repo>)`, `<(rm -r <repo>)`, `>(rm -r <repo>)`. Not demonstrated
  live; a different escape category (argument-embedded execution)
  from command splitting.
- **Assignment- or keyword-prefixed leading words** — a leading word
  obscured by a variable-assignment prefix (`x=$(rm -r /)`) or a
  keyword prefix (`if`, `time`, `!`) is a `cmd0`-derivation gap, not a
  segment-boundary gap. Not demonstrated live.
- **Escaped or quoted leading words** (gate-03 finding 2, new bullet —
  fits none of the four above) — `cmd0` is derived from `tokens[0]`'s
  raw literal text with only a path prefix stripped, so an escape or
  quote mark inside the leading word survives into `cmd0` and defeats
  the `"rm"`/`"find"`/`"git"` string-equality checks. Confirmed ALLOWED
  live as `executor-fast`, unchanged by this fix: `\rm -r <repo>`
  (`cmd0="\rm"`), `"rm" -r <repo>` (`cmd0="\"rm\""`), `r''m -r <repo>`
  (`cmd0="r''m"`, an empty single-quoted string spliced mid-word — a
  real shell concatenates this to `rm`). A `cmd0`-derivation gap, not a
  segment-boundary gap.

The guard reads the command as TEXT before any shell runs it; every
form above puts something other than the bare dangerous command in
front of it or embeds it in an argument, and no version of this
text-inspection fix changes that. Closing these classes needs either a
recursive/allowlist redesign of `cmd0` derivation, argument-level
scanning for embedded substitution, or a different enforcement layer
entirely — scoped out of this plan by owner decision, not an
oversight, and tracked here as documented open debt rather than
silently dropped.

## Risks

- The fail-closed subshell/group rule (decision 2) trades false
  positives (Q5-style benign arithmetic/grouping) for closing a real
  bypass — accepted cost, not a defect to fix later.
- The newline segment boundary (decision 3) is quote-blind: a
  multi-line quoted argument is misjudged as multiple commands —
  accepted false-positive cost, not fixed here.
- Decision 4's excluded categories (argument-embedded command/process
  substitution, command-substitution-as-leading-word, wrapper
  commands including the now-confirmed `find -exec`, escaped/quoted
  leading words, assignment/keyword-prefixed leading words) remain
  live gaps after this plan ships — see "Scope" above; they need their
  own finding before they get their own plan.

## Observation — not tasked (per brief)

`scripts/executor-guard.sh`'s agent-scoping `case` statement — the
block starting `case "$agent_type" in` and ending `*) exit 0 ;;`
(currently around `:251-257`, the catch-all at `:256`) — exits 0
(ALLOW) for any `agent_type` not literally `executor-fast`,
`executor-smart`, `executor-lead`, `executor-judge` (or their
plugin-namespaced forms). **This is intentional, not a defect**: the
fail-open default is required because the main conversation (which
carries no `agent_type`, or an unlisted one) must never be guarded by
this file. It is a registration dependency for any future guarded
agent — that agent must be added to this case list explicitly, or it
inherits none of these protections — recorded here as a dependency for
other work, not tasked in this plan.

## NOTES

- This plan does not touch `is_temp_path`, `normalize_path`, or any
  path-matching logic — that is
  `docs/plans/executor-guard-normalization.md`'s scope entirely.
- Judgment call: decision 2's rule denies by TOKEN SHAPE
  (`tokens_masked[0]` starts with `(` or equals `{`), not by attempting to balance
  parens/braces and recurse into the group's contents — a mini shell
  parser in Bash 3.2 carries more bypass risk (an unbalanced or
  misparsed nested case) than the blunt fail-closed denial does. This
  is the first option that clears the brief's own bar ("if the command
  cannot be parsed into segments confidently, deny") rather than the
  most complete one.
- Judgment call: Q2 is kept as a control rather than deleted (gate-01
  offered either fix) because it documents, by simulation, that the
  ordering pitfall it names does not actually corrupt this particular
  shape — useful negative evidence alongside Q6's positive
  discrimination of the same pitfall on a different shape.
- gate-03 findings 1-3 (`docs/plans/gate-03-executor-guard-splitter.md`)
  all APPLIED: finding 1 (load-bearing, escape-blind `&` split) via the
  `esc -eq 0` guard added to Decision 1 plus Q16/Q17; finding 2
  (load-bearing, residual register) via the fifth Scope bullet
  (escaped/quoted leading words) and the `find -exec` relabel to
  confirmed; finding 3 (cosmetic, mode gate) via the `mode = "chain"`
  guard added to Decision 1 plus Q18. Probe table is now Q1-Q18 (was
  Q1-Q15).
