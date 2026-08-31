# Round 3 Design-Review Re-Gate Ruling: executor-guard-normalization (2026-08-31 — Final)

MODE: **DESIGN-REVIEW** (re-gate, round 3 of 3)

## VERDICT

**BLOCKED** — the plan as written opens a new ALLOW *outside* the confinement set on a shape the guard denies today: `rm -r ~` with a temp `.cwd` resolves to `<scratchpad>/~`, which the unchanged `scratchpad` component match ALLOWs, while the shell deletes `$HOME`.

## PRIOR CLOSURE

| # | State | Evidence |
|---|---|---|
| N1, N2, N5, N6, N8 | CLOSED | `plan:61-69` (abs-replaces / rel-against-parent), `plan:100-105` (trailing-slash→`full`), `plan:185-202`, `plan:203-216`, `plan:246-251`. Verified first-hand: `readlink /tmp`→`private/tmp`, `readlink /var`→`private/var`, `bash --version`→3.2.57(1) arm64-apple-darwin25. |
| N3 | CLOSED, with residue | Decision 7 `plan:151-163` names channel + 6 failure modes. Silent on whether the existence check applies to the FINAL component — new finding 2. |
| N4 | CLOSED (owner) | Decision 8 `plan:164-184`. Not re-litigated; its *coverage* is new finding 1. |
| N7 | CLOSED, with residue | Decision 4 `plan:106-129` + P16/P17. P16's setup omits that `subdir` must exist — finding 2. |
| F1 | CLOSED | `plan:70-79` applies `.`/`..` collapse at every position in both modes; P18/P19 added. Verified `/private` and `/private/var` exist and the anchored matcher DENIES both. |
| F2 | CLOSED, set still incomplete | `{` added `plan:164-171`; P20 added. `~` absent — finding 1. |
| F3, F4, F6, F7 | CLOSED | P12 cycle moved to intermediate `plan:315`; `.cwd` semantics + probe choreography `plan:106-129`; P9 re-tagged fail-closed control `plan:312`; `_path_guard_` helpers + grep stated best-effort `plan:203-216`. |
| F5 | CLOSED (spec), unprobed live | Decision 11 `plan:217-232`. Ran the anchored matcher: `<repo>/tmp/x`→DENY, `/private/tmp/x`→ALLOW, `/var/folders/xx/T/f`→DENY. No live row discriminates it — finding 5. |
| F8 | CLOSED for P3/P9 | `<repo-rel>` defined `plan:292-295`. P1 still uses absolute `<repo>` after `/tmp/../` (yields `//`); benign, executable. |

## NEW FINDINGS

1. **LOAD-BEARING — bare `~` is not in decision 8's trigger set, and the plan turns today's DENY into an ALLOW** (`plan:164-171` vs `plan:217-232`). Probed live: `rm -r ~` is **DENIED today** (token `~` matches no temp substring). After this plan: decision 8 passes it (`~` is not `$`/backtick/`$(`/`{`), decision 1 resolves it against `.cwd`, giving `<scratchpad>/~`, which the *unchanged, unanchored* scratchpad component match ALLOWs — while the shell expands `~` to `/Users/harishamutha` (verified). Same for `~user`, `~+`, `~-`. Reachable with no adversarial setup under finding 2's reading; with a literal `~` directory (creatable by accident via `mkdir "~/x"`) under the other. Clears: add "token whose first character is `~`" to decision 8's trigger set — identical shape and rationale to F2's `{` — and add a `rm -r ~` probe row.
2. **LOAD-BEARING — decision 7 never says whether the existence check applies to the final component** (`plan:151-163` vs `plan:88-99`). Decision 3 says `parent` does not touch the final component; decision 7 lists "a component that does not exist" as a failure. Two defensible builds. This is the exact skip-the-final ambiguity F1 fixed for `.`/`..` and left unfixed for existence. It decides finding 1's blast radius, and no probe discriminates it: P16 (`plan:319`) expects ALLOW but never states `subdir` exists, so a correct Reading-A build FAILS the row. Clears: state that decision 7's existence check applies to every component including the final one, in both modes; state P16's `subdir` is created first.
3. **LOAD-BEARING, OUT OF SCOPE — decision 5's confinement claim is false as written** (`plan:130-146`). Probed live, `agent_type: executor-fast`: `true & rm -rf /Users/harishamutha/maddog-skills/agents` → **ALLOWED**. Also `(rm -r <repo>)` and `{ rm -r <repo>; }` → ALLOWED. `split_command` (`executor-guard.sh:166-175`) handles `&&` but not a single `&`, and no grouping construct. Newline IS handled (`:497`'s here-string). Pre-existing, orthogonal to `is_temp_path`, and **must not gate this fix** — but `docs/plans/executor-fast-read.md` inherits this proof standard by reference. Clears: narrow decision 5 to "path-token confinement, given the command reaches the check", and file the splitter gap separately.
4. **LOAD-BEARING — every quoted path token is newly denied; the plan is silent and no probe covers it** (`plan:217-232`). `quote_walk` retains quote characters in the literal token (verified: `rm -r '/private/tmp/foo'` tokenizes to `'/private/tmp/foo'`). Today the substring match ALLOWs it; anchored, it DENIES, and `normalize_path` sees a non-`/`-initial token → relative → nonexistent → DENY. Fail-closed but a real regression on a common form; all 21 rows are unquoted. Clears: record the regression, or strip balanced outer quotes before the scan; add one quoted row.
5. **COSMETIC — four rows deny by the mechanism they do not name.** P1, P3, P10, P17 all resolve to nonexistent paths (`/tmp/..`→`/private`, so P1 is `/private/Users/...`; `<scratchpad>/../<repo-rel>` is `<uuid>/Users/...`; P17's two `..` from a six-deep scratchpad lands at `/private/tmp/claude-501/Users/...`). Correct builds DENY via decision 7, never reaching the matcher. Their clauses still separate correct from the named wrong build, so no row is *wrong* — but P21, the only anchoring row, is confounded the same way live, leaving decision 11 with no discriminating PT2 probe. Clears: mark these four "denies via decision 7"; state that P21's `<repo>/tmp/x` is created for the live run.
6. **UNVERIFIED ASSUMPTION — decision 7's EACCES mode may not be implementable in Bash 3.2** (`plan:151-163`). `[ -L ]`/`[ -e ]` return false identically for "not a symlink" and "parent not searchable", so an unreadable component is silently under-resolved rather than failed. Failure direction is benign (an unsearchable component blocks `rm` too), but the contract claims detection it may not get. Everything else in the algorithm is 3.2-clean — no `mapfile`, associative array, `${var,,}`, or `&>>` is required. Clears: state EACCES as best-effort, or specify a `stat`/`ls` exit-code probe.

## IF BLOCKED

- **Owner decision:** finding 1 (widening an OWNER-DECISION trigger set — same class of call the owner already made, and F2 already extended once) and finding 3's disposition (narrow the claim now vs. widen the splitter as a separate change).
- **Mechanical:** findings 2, 4, 5, 6 — all are wording/probe-setup edits, no design open.
- Findings 1 and 2 are the only ones that gate. 3, 4, 5, 6 can ship recorded.

## DELEGATION LOG

none — all evidence gathered first-hand.

## NOTES

- **Partial merge is safe and no weaker.** PT1 alone leaves `executor-guard.sh:291` calling the anchored `is_temp_path` on raw tokens. Anchored ⊂ unanchored and `/var/folders/` is dropped, so the PT1-only window denies strictly more (`/var/folders/xx/T/f` and quoted temp paths flip ALLOW→DENY — verified). Fail-closed. A broken `source` → 127 → `all_temp=0` → deny.
- **`is_temp_path` is never reached with an unnormalized argument after PT2** — `:291` is its only call site and decision 7 bars calling it on a non-zero return. Decision 11's reasoning for dropping bare `/var/folders/` holds.
- **Round 2's two escapes are genuinely closed**, verified against the algorithm as it now reads: `/tmp/..`→`/private` and `/private/tmp/{x,..}` (denied by the `{` trigger).
- **Suspected, not demonstrated:** I could not create the literal `~` decoy directory to run finding 1 end-to-end — the live guard denies my writes (`executor-judge`, `deny_writes=1`; it denied my redirect once during this review). Both halves are separately verified: `rm -r ~` DENIED today, and `~` expanding to `/Users/harishamutha`.
- Nothing in the working tree was modified.
