# Plan: executor-guard-splitter — fix the command-splitting defect

STATUS: frozen, ready to execute. Split out per owner decision: this
defect (`docs/plans/gate-03-executor-guard-normalization.md` finding 3)
is more severe than the path-normalization defect
`docs/plans/executor-guard-normalization.md` fixes — that plan narrows
which paths a matched `rm` is allowed to touch; this plan fixes whether
the dangerous command is ever matched at all. **This plan ships FIRST.**
Neither plan merges with, restates, or depends on the other beyond this
ordering. Decisions are CLOSED — do not redesign.

## Why this exists

`scripts/executor-guard.sh` decides what a command does by inspecting
the FIRST WORD (`cmd0`) of each segment `split_command` (`quote_walk
chain` mode, `:97-219`) produces. Verified live and by direct function
call against the unmodified script (2026-08-31):

- A single `&` (background operator) is never recognized as a boundary
  — `&` only splits when the *next* char is also `&` (`:166-175`). `true
  & rm -r <repo>` stays ONE segment, `cmd0="true"`, the `rm` is never
  examined. **ALLOWED — confirmed live.**
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

1. **Single `&` becomes a chain-mode segment boundary, with two
   exclusions.** In `quote_walk`'s `chain` mode, the existing `'&')`
   case (`:166-175`) currently: splits on `&&` (2 chars), otherwise
   falls through and appends `&` as a literal character. Change the
   fallthrough: a bare, unquoted `&` splits the segment (mirrors the
   existing `;` case exactly — close current buffer, skip 1 char, start
   a new segment) UNLESS either holds:
   - the **next** character is `>` (the `&>`/`&>>` redirect forms), or
   - the **last character already written to the current buffer** is
     `>` (the `>&`, `2>&1`, `1>&2`, `>&-` fd-duplication/close forms).
   Both exclusion checks read state already available at that point in
   the walk (the lookahead char and the buffer's last char) — no new
   state variable is needed. The `&&` check runs first and is
   unaffected; order the new checks after it, before the boundary
   split.
2. **Fail-closed rule for subshells and brace/paren groups (resolves
   finding 3's second and third probes).** After a segment is
   tokenized (`quote_walk word` mode) into `tokens`/`tokens_masked`,
   before any per-command check runs: if `tokens[0]` (the RAW literal
   token, not `cmd0` which has already had a path prefix stripped)
   starts with an unquoted `(` (covers `(cmd)` subshells, `((expr))`
   arithmetic commands, and a bare `$(cmd)` used as an entire leading
   word), OR `tokens[0]` is exactly `{` (covers `{ cmd; }` brace
   groups) — deny the segment outright with a "cannot confidently
   identify the leading command" reason, the same fail-closed shape as
   the brief requires, rather than attempting to parse inside the
   group. This is deliberately blunt: it also denies a harmless bare
   `((x++))` (Q5 documents this as an accepted false-positive cost, not
   a defect) and a harmless `(cd x && ls)`. An agent that hits this
   denial rewrites the command without the wrapper — the guard does
   not need to see inside a subshell to do its job, only to never
   silently skip past one.
   **What this rule does NOT touch (verified — must not regress):**
   `tokens[0]` starting with `$` (parameter expansion `${VAR}`,
   command substitution `$(cmd)`, arithmetic expansion `$((expr))`)
   does not start with a bare `(` and is untouched by this rule; a `(`
   or `{` appearing in a NON-leading token (e.g. `echo $(date)`, `cp
   {a,b} dst`) is untouched, since the check inspects `tokens[0]` only.
3. **Newline — verify, correct the citation, preserve by construction.**
   Confirmed live and by direct call: a literal newline embedded in
   `.tool_input.command` DOES cause a segment split today (`true\nrm -r
   <repo>` → DENY, matching the plain `rm -r <repo>` control). The
   brief's citation is imprecise: `quote_walk`'s `chain`-mode case
   statement has NO explicit branch for `\n` — it falls to the default
   `*)` case and is appended into the buffer as an ordinary character,
   quote-state and all. The split happens one layer up: each finished
   segment is printed via `printf '%s\n' "${out[@]}"` and re-consumed by
   a line-oriented `while IFS= read -r segment` loop; a literal newline
   *inside* one buffered segment is byte-for-byte indistinguishable from
   the record terminator `printf` appends, so it silently acts as a
   segment boundary regardless of quote state. `scripts/executor-guard.sh:497`'s
   here-string is not the mechanism — it is merely the outer loop that
   inherits this side effect. **This plan does not change that
   mechanism.** Task 1's diff must not strip, join, or otherwise
   normalize embedded newlines inside `quote_walk`'s chain-mode buffer
   — doing so would silently remove a protection that currently works
   by accident. No probe row is needed to prove no-regression here
   beyond the existing control already run above (recorded, not
   retested per row).
4. **Scope boundary — named, not tasked.** Command substitution
   (`$(...)`, backticks) and process substitution (`<(...)`, `>(...)`)
   used as an ARGUMENT (not the segment's leading token) embed a
   runnable command inside a word rather than at a segment boundary —
   a different escape category (argument-embedded execution) from
   "command splitting." Decision 2 already prevents them from being
   mistaken for the leading command; going further (recursively
   inspecting their contents) is out of this plan's scope, named here
   so it is not silently dropped. Likewise, a leading word obscured by
   a variable-assignment prefix (`x=$(rm -r /)`) or a keyword prefix
   (`if`, `time`, `!`) is a `cmd0`-derivation gap, not a segment-boundary
   gap — a different defect class, not tasked here.
5. **Proof standard.** Same as the sibling plan: direct function
   probes (calling `quote_walk`/`split_command` directly, checking
   segment count) prove the parsing primitive; live probes (dispatched
   with `agent_type: executor-fast`, run and recorded by hand) prove
   the end-to-end ALLOW/DENY outcome. Both are required per probe-table
   row where marked.
6. **Header comment update.** `scripts/executor-guard.sh:1-49`'s header
   documents `split_command`'s segment-boundary set. Update it to state
   the full set (decision 1's `&`/`;`/`&&`/`||`/`|` plus decision 2's
   fail-closed subshell/group rule) and decision 3's newline mechanism
   (accidental, preserved, not a designed case branch) — so the next
   reader does not have to re-derive it from the diff.

## Task list

**T1 — Fix `split_command`'s `&` handling + add the fail-closed
subshell/group rule** [executor-smart BUILD, gated by review-agent —
GATE-INFRA]
- Files: `scripts/executor-guard.sh` (the `'&')` case in `quote_walk`
  chain mode, `:166-175`; a new check inserted after tokenization and
  before the per-command-type checks, `:263` area; header comment
  `:1-49` per decision 6).
- Depends on: none.
- Bash 3.2 constraint (this repo's target, confirmed
  `bash --version` → 3.2.57): the exclusion checks (lookahead char,
  last-buffer-char) and the `tokens[0]` prefix/equality tests are all
  3.2-clean glob/case matching — no `mapfile`, associative array, or
  `${var,,}` needed.
- DONE-WHEN:
  - `bash -n scripts/executor-guard.sh` passes;
  - every "direct" row in the probe table below, called directly
    against `quote_walk`/`split_command` (no live dispatch), returns
    its expected segment count;
  - every "live" row, dispatched with `agent_type: executor-fast`
    against the live script, returns its expected ALLOW/DENY;
  - the header comment states the full boundary set and the newline
    mechanism per decision 6;
  - review-agent verdict CLEAR.

**T2 — Release** [release skill, all six phases — GATE-INFRA surface:
`scripts/`]
- Files: none directly.
- Depends on: T1 merged to the candidate branch.
- READY re-runs the full probe table live (not `bash -n` alone).
- DONE-WHEN: PR open citing a RULE verdict naming the PR's head commit;
  user merges; SEAL posts tag + CI result.

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
| Q2 | `cd <scratchpad> && true & rm -r <repo>` (mixes `&&` and a bare `&` — ordering pitfall) | executor-fast | live | DENY | wrong build checks the new bare-`&` rule before confirming the char isn't part of `&&`, mis-splitting `&&` itself and corrupting the segment containing `rm` so `cmd0` never resolves to `"rm"` → ALLOWs. |
| Q3 | `(rm -r <repo>)` | executor-fast | live | DENY | wrong build has no fail-closed check for a leading unquoted `(`; `cmd0` is `"(rm"`, never `"rm"` → ALLOWs. |
| Q4 | `{ rm -r <repo>; }` | executor-fast | live | DENY | wrong build has no fail-closed check for a lone `{` token; `cmd0` is `"{"`, never `"rm"` → ALLOWs. |
| Q5 | `((x++))` (bare arithmetic; no dangerous payload — documents the accepted false-positive cost) | executor-fast | live | DENY | wrong build matches only an EXACT `(` token, not "starts with"; the glued, space-free `((x++))` token fails an equality test and ALLOWs, showing the rule must be a prefix match. |
| Q6 | `true && rm -r <scratchpad>/x` | n/a | direct (segment count) | 2 segments | wrong build's new bare-`&` logic fires on the first `&` of `&&` before checking the second char, producing 3 segments or a corrupted split instead of 2. |
| Q7 | `echo "a & b"` | executor-fast | direct (1 segment) + live | ALLOW | wrong build checks for a bare `&` before the existing quote-state branches, splitting inside the quoted string and denying or misparsing a harmless command. |
| Q8 | `printf x &>/dev/null` | n/a | direct (1 segment) | n/a (parsing correctness, not danger) | wrong build treats every unquoted `&` not forming `&&` as a boundary with no lookahead for `>`, splitting `&>` into two segments. |
| Q9 | `printf x &>>/tmp/log` | n/a | direct (1 segment) | n/a | same as Q8, for the two-character `>>` after `&`. |
| Q10 | `rm -r <scratchpad>/x 2>&1` | n/a | direct (1 segment) | n/a | wrong build has no lookbehind for a preceding `>`; it splits `>&` into two segments (`"...2>"`, `"1"`). |
| Q11 | `cp {a,b} <scratchpad>/` | executor-fast | live | ALLOW | wrong build's fail-closed rule matches `{` anywhere in any token, not just `tokens[0]`, and denies ordinary brace expansion. |
| Q12 | `echo $(date)` | executor-fast | live | ALLOW | wrong build's fail-closed rule matches an unquoted `(` anywhere in the command, not just at `tokens[0]`, and denies ordinary command substitution used as an argument. |

12 rows total (Q1-Q12). Newline (decision 3) is a recorded control, not
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
   verdict and every READY result. STOP — never merge; user merges.
6. **SEAL**: tag `vX.Y.Z`; `claude plugin tag --push`; confirm CI green;
   post SEAL comment on the merged PR.

## Risks

- The fail-closed subshell/group rule (decision 2) trades false
  positives (Q5-style benign arithmetic/grouping) for closing a real
  bypass — accepted cost, not a defect to fix later.
- Decision 4's excluded categories (argument-embedded command/process
  substitution, assignment/keyword-prefixed leading words) remain live
  gaps after this plan ships; they are a different defect class and
  need their own finding before they get their own plan.

## Observation — not tasked (per brief)

`scripts/executor-guard.sh:237`'s agent-scoping `case` statement ends
`*) exit 0 ;;` — any `agent_type` not literally `executor-fast`,
`executor-smart`, `executor-lead`, `executor-judge` (or their
plugin-namespaced forms) is completely unguarded by this file, with no
warning. This is a standing dependency for any future guarded agent: it
must be added to this case list explicitly, or it inherits none of
these protections. Recorded here as a dependency for other work, not
tasked in this plan.

## NOTES

- This plan does not touch `is_temp_path`, `normalize_path`, or any
  path-matching logic — that is
  `docs/plans/executor-guard-normalization.md`'s scope entirely.
- Judgment call: decision 2's rule denies by TOKEN SHAPE (`tokens[0]`
  starts with `(` or equals `{`), not by attempting to balance
  parens/braces and recurse into the group's contents — a mini shell
  parser in Bash 3.2 carries more bypass risk (an unbalanced or
  misparsed nested case) than the blunt fail-closed denial does. This
  is the first option that clears the brief's own bar ("if the command
  cannot be parsed into segments confidently, deny") rather than the
  most complete one.
</content>
