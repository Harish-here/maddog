# Round 2 Design-Review Re-Gate Ruling: executor-guard-normalization.md
**Date:** 2026-08-31

MODE: DESIGN-REVIEW (re-gate, round 2 of 3). Verdict below.

## VERDICT

**BLOCKED** — the revised algorithm still ALLOWs a destructive delete outside the settled confinement set via two shapes I demonstrated (`.`/`..` in final position under `parent` mode; brace expansion, which decision 8's trigger set does not name), and one probe row (P12) expects a result the specified algorithm cannot produce.

## ROUND 1 CLOSURE

| # | State | Evidence |
|---|---|---|
| N1 | CLOSED (spec) | `plan:52-60` states absolute-target-replaces-prefix and relative-against-parent, exactly as N1 asked. `readlink /tmp` → `private/tmp`, `readlink /var` → `private/var` confirmed. Probe P9 is weak — new F6. |
| N2 | CLOSED | `plan:78-83` trailing-slash forces `full`; P11 added and discriminates (a `parent`-only build fails it). |
| N3 | CLOSED | `plan:118-130` names return channel + six failure modes + partial-prefix rule. One mode omitted — new F4. |
| N4 | CLOSED (owner) | Decision 8 `plan:131-147`. Not re-litigated. Its *coverage* is F2. |
| N5 | CLOSED | `plan:148-165`. Verified first-hand: `executor-guard.sh:51` is `set -uo pipefail` (no `-e`); `:291` is `is_temp_path "$p" || all_temp=0`; 127 is falsy → `all_temp=0` → `:294` deny. Trace holds. `dirname "${BASH_SOURCE[0]}"` idiom confirmed at `setup-watchdog.sh:9`. |
| N6 | CLOSED | Ran decision 10(a) on this platform: `printf 'MARKER\n' | bash -c 'read -r l; test "$l" = MARKER'` → 0; with a top-level stdin consumer → 1. It does catch a consuming library on bash 3.2.57. Two weaknesses — F7. |
| N7 | CLOSED | P16/P17 added (`plan:256-257`) and PT2's DONE-WHEN lists P9-P17 (`plan:216-219`). Executability caveat — F5. |
| N8 | CLOSED | `plan:188-194` names bash 3.2 and that `bash -n` cannot catch a 4-ism. Confirmed `bash --version` → 3.2.57(1) arm64-apple-darwin25. |

## NEW FINDINGS

1. **LOAD-BEARING — `.`/`..` in FINAL position is never applied under `parent` mode** (`plan:69-74` against `plan:42-45`). Decision 1 says apply `..` against the resolved prefix; decision 3 says `parent` "resolves every path component except the final one". For `rm -r /tmp/..` the two read differently, and the skip-the-final reading yields `/private/tmp/..`, which I ran through the real matcher (`executor-guard.sh:63-72`): **ALLOW** — deleting `/private`. Same for `/var/folders/..` → **ALLOW**, deleting `/private/var`. Clears: state that `.`/`..` are collapsed against the resolved prefix in every position including the final one; `parent`'s exemption covers only *symlink dereference* of the final component. Add both as probes.
2. **LOAD-BEARING — brace expansion slips decision 8's trigger set** (`plan:131-147`). Ruling on the asked question: `${X}`, escaped and quoted `$`/backtick forms are covered (the raw token retains the `$`); glob (`*`, `?`, `[`) and tilde are covered *incidentally* by decision 7's nonexistent-component deny. **Brace is not.** `echo /private/tmp/{x,..}` → `/private/tmp/x /private/tmp/..`; the guard's single literal token `/private/tmp/{x,..}` normalizes (final component unresolved) to itself → **ALLOW** (ran it), while the shell deletes `/private`. `/var/folders/{x,..}` likewise. No `$`, no backtick. This survives fixing F1. Clears: add `{` to decision 8's trigger set, or resolve the final component's literal existence.
3. **LOAD-BEARING — P12 expects a result the algorithm cannot produce** (`plan:252`). `rm -r /tmp/cycle-a` with the cycle at the *final* component: under `parent` mode that component is never dereferenced, so no cycle is ever entered and the hop budget never trips. Resolved `/private/tmp/cycle-a` → ALLOW; the table says DENY. A correct build fails this row. Clears: move the cycle to an intermediate component (`rm -r /tmp/cycle-a/x`), or restate the expected result as ALLOW with rationale.
4. **LOAD-BEARING — decision 4 mis-states `.cwd`, and P16/P17 have no stated setup** (`plan:84-91`, `plan:256-257`). Official docs (code.claude.com/docs/en/hooks, Common Fields): `"cwd": "string (current working directory)"` — *"Always present; changes when Claude executes `cd` commands or enters a worktree."* So `.cwd` is **not** "the dispatch's starting directory"; it tracks `cd` across tool calls. The recorded limit is narrower than written (only an *in-command* chained `cd` is unseen). Consequence: PT2's DONE-WHEN requires P16/P17 live with `.cwd = <scratchpad>`, and the plan never says how that is arranged. Clears: correct the semantics; specify the `cd`-first setup step for P16/P17.
5. **LOAD-BEARING (limited blast radius) — the matcher stays unanchored after normalization** (`plan:288-289`). `is_temp_path` matches `*"/tmp/"*` as a substring. Ran it: `/Users/harishamutha/maddog-skills/tmp/x` → **ALLOW**. Normalization cannot fix this; any directory named `tmp` anywhere becomes deletable, which is outside the settled confinement set (`/tmp`, `/private/tmp`, `/var/folders`, `scratchpad` component). Clears: anchor the temp prefixes to `/private/tmp/`, `/private/var/folders/`, `/tmp/` at string start, leaving `scratchpad` component-matched as settled.
6. **COSMETIC — P9 does not discriminate for the defect it cites** (`plan:249`). Both the correct build (relative target against the symlink's parent) and the N1-wrong build (against root) land on a nonexistent path and DENY via decision 7. Round 1's own note (`gate-01:41`) says no false ALLOW from N1 could be constructed; P9 therefore verifies nothing beyond fail-closed. Clears: mark it a fail-closed control, or drop the N1 attribution.
7. **COSMETIC — decision 10's static check over-constrains and under-detects** (`plan:166-176`). `declare -F` listing *exactly* two functions forbids any internal helper a component walk plausibly needs. The `grep -n '^[^[:space:]#]'` check is indentation-convention-only by the plan's own admission — an indented top-level `set`/`exit` passes. Clears: allow helpers under a name prefix; state the grep as best-effort.
8. **COSMETIC — P3 and P9 are not literally executable as notated** (`plan:243`, `plan:249`). `<scratchpad>/../<repo>` with `<repo>` defined as an absolute path yields `//Users/...`; P9's `../<repo-relative-path>` leaves the base unstated. PT2/PT3 DONE-WHENs demand each row run end-to-end. Clears: notate the relative suffixes concretely.

## DELEGATION LOG

researcher — extract verbatim PreToolUse payload schema for `cwd`/`agent_type` from official docs — returned quoted field definitions and URL (evidence used in F4). No verdict delegated.

## NOTES

- **Partial merge is safe and no weaker.** Verified at `executor-guard.sh:51` and `:285-296`: PT1 alone leaves `:291` calling `is_temp_path` on the raw token byte-identically to today; a broken `source` yields 127 → `all_temp=0` → deny every recursive delete. Noisy, never weaker. `gate-01:42` holds.
- **Fail-closed sweep.** Decision 7's six modes all reach `all_temp=0`. Two modes are outside it: an empty/unusable `.cwd` (docs say always present, so low risk — but unspecified), and `jq` absent (`:225` `exit 0`, pre-existing documented fail-open, out of scope).
- **Could not construct a repo-reaching ALLOW.** Every `..`-climb toward `/Users/harishamutha/maddog-skills` puts the climb in intermediate position, where the walk resolves it and the matcher then denies. F1/F2 reach `/private` and `/private/var`, not the repo — serious, and outside the settled confinement set, but I did not demonstrate a repo file deleted.
- **Suspected, not demonstrated:** that a directory literally named `a{,` (creatable by an executor) could be combined with brace expansion for a deeper climb. Every variant I traced resolved to a non-temp path and denied.
- Nothing in the working tree was modified. My own probes were twice denied by the live guard's redirect check (I am `executor-judge`, `deny_writes=1`); both were re-run without redirection.
