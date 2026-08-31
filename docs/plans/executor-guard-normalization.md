# Plan: executor-guard-normalization — fix the path-normalization defect

STATUS: frozen, ready to execute. Split out of
`docs/plans/executor-fast-read.md` by owner decision: round 2
(`docs/plans/gate-02-executor-fast-read.md`) blocked that plan on this
defect's spec quality alone (NF1-NF4, NF7, NF8), while everything else in
that plan cleared. This plan ships FIRST, as its own release.
`docs/plans/executor-fast-read.md` depends on this plan's merge and
sources its output rather than reimplementing path logic. Decisions are
CLOSED — do not redesign.

Revision note: this revision closes `docs/plans/gate-01-executor-guard-normalization.md`'s
findings N1-N8. NF1-NF6's and NF8's prior resolutions (decisions 1-2, 5-6
below) are extended, not replaced; NF7 is closed by N7 (decision 4 +
probes P16/P17). N4 (owner decision) is decision 8.

Round 2 revision note: this revision closes
`docs/plans/gate-02-executor-guard-normalization.md`'s findings F1-F8.
F1 corrects decisions 1 and 3 (the final-component `.`/`..` collapse gap).
F2 widens decision 8's trigger set (brace, never weakening the owner's
decision). F3 moves probe P12's cycle to an intermediate component. F4
corrects decision 4's `.cwd` semantics and states P16/P17's setup. F5
adds decision 11 (anchored temp-prefix matching). F6 and F8 correct
probes P9 and P3. F7 corrects decision 10's static check.

Post-release revision note: commit `186b1ba` (v2.14.1) shipped this plan.
Its RULE verdict cleared, but flagged a behaviour regression: decision
7's uniform final-component existence check denies two ordinary temp
operations that were ALLOWED before — idempotent cleanup of an
already-deleted path (`rm -rf /tmp/some-already-deleted-dir`) and glob
cleanup inside a temp directory (`rm -rf /private/tmp/claude-501/*`).
The owner decided to fix rather than document. This revision amends
decision 7 (narrow relaxation, stated precisely in decision 7's own
text below) and adds probes P24-P28; it revises P9's expected column
(ALLOW, was DENY) as a direct, intended consequence of the same
amendment — see decision 7 and P9's row for why this is not a
reopened bypass. No other decision or probe changes.

Round 3 revision note: this revision closes
`docs/plans/gate-03-executor-guard-normalization.md`'s findings G1-G6 (the
ruling's own numbering 1-6, prefixed G to fit this plan's per-round
letter convention). G1 (owner decision) widens decision 8's trigger set
to a leading `~`, adds probe P22. G2 states decision 7's existence check
covers the final component in both modes, and states P16's setup. G3
(owner decision) narrows decision 5's confinement claim to path-token
confinement given the command reaches the check, and cross-references
`docs/plans/executor-guard-splitter.md` (ships before this plan). G4
adds decision 12 (quote stripping) and probe P23. G5 corrects the
denial-mechanism clause on P1/P3/P10/P17 and states P21's setup. G6
states decision 7's EACCES detection as best-effort. See "## Gate
status" below for what round 3 authorises.

## Why this exists

`is_temp_path()` (`scripts/executor-guard.sh:63-72`) matches a path string
by component only, with no normalization first. Its one call site
(`scripts/executor-guard.sh:291`, inside the recursive-delete `rm -r`
check) inherits the gap. Confirmed first-hand, `agent_type:
executor-fast`:

- `rm -r /tmp/../<repo path>` — ALLOWED (should be DENIED).
- the same path reached through a symlink planted inside a scratchpad
  directory — ALLOWED (should be DENIED).
- `rm -r <scratchpad path>/../<repo path>` — ALLOWED (should be DENIED).
- the plain repo path, no `..` — correctly DENIED (regression control,
  must stay DENIED).

`executor-lead`/`executor-judge` are unaffected, but not because no path
is ever examined: `:291`'s check does examine paths. Both agents hit the
file-write-denial block's unconditional `rm` deny first (currently
`scripts/executor-guard.sh:419-421`), which fires regardless of path and
never reaches the recursive-delete-specific check. Round 1's plan
mis-stated this as "denies every rm before any path is examined" —
corrected here per NF8.

## Gate status

Three design-review gate rounds are spent: `docs/plans/gate-01-executor-guard-normalization.md`
(N1-N8), `docs/plans/gate-02-executor-guard-normalization.md` (F1-F8),
`docs/plans/gate-03-executor-guard-normalization.md` (G1-G6, BLOCKED
pending this revision). The owner has authorised building from this plan
once G1-G6 are applied — no further judge round. Acceptance is the
mechanical check named in PT1/PT2's DONE-WHENs: every row of the probe
table (P1-P28, per the post-release revision note above) run, live where tagged, against the built script, plus
`bash -n` and decision 10's sourceability checks. PT3's release-phase
RULE verdict (executor-judge, fix-less, per the release skill) is a
separate, later gate on the release candidate diff — not a fourth design
round on this plan's content.

## Decisions

1. **Normalization algorithm (resolves NF1, N1).** Left-to-right, per-component
   walk starting from the root. At each step: apply `.`/`..` only against
   the already-resolved prefix (never lexically pre-collapsed against the
   raw, unresolved path); if the resolved-so-far component is itself a
   symlink, resolve it (one `readlink` hop) and continue walking its
   target's components; bound total hops against cycles (e.g. 40). A
   relative input path resolves against the payload's `.cwd` before the
   walk starts. This closes both round-2 counter-examples: the lexical
   collapse that crosses a symlink boundary, and an intermediate (not
   just trailing) symlink.
   **Symlink target resolution (resolves N1):** an ABSOLUTE `readlink`
   target REPLACES the entire resolved-so-far prefix — the walk restarts
   from root using the target's components. A RELATIVE `readlink` target
   resolves against the symlink's PARENT directory (the resolved prefix
   minus the symlink's own final component) — never against root, never
   against `.cwd`. This is not an edge case on this platform: `readlink
   /tmp` returns `private/tmp`, a relative target, so nearly every
   `/tmp/...` path takes this branch on its very first hop, landing at
   `/private/tmp/...`.
   **Final-position collapse (resolves F1).** The `.`/`..`-against-resolved-prefix
   collapse above applies to EVERY component, including the final one,
   regardless of the call-site mode (decision 3). The `parent`/`full` mode
   split governs only whether a symlink AT the final component is
   dereferenced — never whether `.`/`..` at the final component is
   collapsed. Without this, `rm -r /tmp/..` under a skip-the-final reading
   of decision 3 stops at `/private/tmp` and ALLOWs; collapsing the final
   `..` against the resolved prefix instead yields `/private`, which
   decision 11's anchored `is_temp_path` correctly denies. Same shape for
   `/var/folders/..` → `/private/var` after the `/var` symlink hop.
2. **Shared, sourceable helper (resolves NF2).** `normalize_path` and
   `is_temp_path` move out of `scripts/executor-guard.sh`'s body into a
   new file, `scripts/path-guard-lib.sh`, with no top-level stdin read and
   no side effect on `source`. `scripts/executor-guard.sh` cannot be
   sourced (it reads stdin and runs its whole body at top level to line
   ~499) — extraction is required, not optional, for any second caller
   (e.g. a future Write-scoping hook) to reuse the same logic instead of
   reimplementing it.
3. **Per-call-site final-component handling (resolves NF4, N2; F1 correction).**
   The mode split governs SYMLINK DEREFERENCE ONLY, never `.`/`..` collapse
   (decision 1 applies that collapse uniformly, at every component
   including the final one, in both modes). `parent` dereferences a
   symlink at every component up through the second-to-last, and at the
   final component does NOT dereference a symlink (matches `rm` semantics
   — a trailing symlink is unlinked, not followed); `full` additionally
   dereferences a symlink at the final component (matches a file write's
   semantics — the OS follows a trailing symlink before writing).
   `scripts/executor-guard.sh:291` uses `parent` mode. Any future
   write-path caller MUST use `full` mode — named here as a contract this
   plan hands forward; no write-path caller exists in this plan's scope.
   **Trailing-slash override (resolves N2):** if the input path ends in
   `/`, the call is forced to `full` mode regardless of the mode argument
   passed — the kernel dereferences a trailing symlink whenever a slash
   follows it (`ls -ld /var` vs `ls -ld /var/`); without this override,
   `parent` mode would leave `rm -r /tmp/link/` unresolved and ALLOW an
   escape through the symlink's target.
4. **`.cwd` extraction (resolves NF7, N7; F4 correction).** The guard reads
   `.cwd` from the PreToolUse payload to resolve relative segments before
   the walk. Per the hooks documentation, `cwd` is "Always present;
   changes when Claude executes `cd` commands or enters a worktree" — it
   is NOT the dispatch's starting directory; it tracks the session's
   current directory across tool calls and updates whenever a standalone
   `cd` Bash call runs. Documented, unsolved limit, narrower than
   previously stated: only a `cd` CHAINED INSIDE THE SAME COMMAND as the
   path (`split_command` evaluates chained segments independently, and
   the `cd` has not executed yet when this hook fires on that command) is
   not guaranteed correctly resolved. A `cd` issued as its own, prior tool
   call IS reflected. Record this limit in the header comment, not solved
   here.
   **Probe setup (resolves F4's second half):** P16/P17's PT2-live runs
   dispatch `cd <scratchpad>` as its own, UNCHAINED Bash call first (this
   updates the session `.cwd` per the semantics above), then dispatch the
   `rm -r ...` command as a separate, subsequent Bash call, whose payload
   `.cwd` is the already-updated scratchpad path. PT1's direct probes skip
   this choreography and pass `.cwd` as an explicit function argument.
   **Probe coverage (resolves N7):** the probe table below and PT2's
   DONE-WHEN each carry a relative-path pair — P16, a relative token that
   stays inside a temp `.cwd` (control, ALLOW), and P17, a relative token
   that walks `..` out of a temp `.cwd` into the repo (escape, DENY) — so
   this code path is no longer probe-free.
   **P16 setup (resolves G2):** `<scratchpad>/subdir` is created (`mkdir`)
   before the PT1/PT2 run that probes P16 — decision 7's existence check
   (below) applies to every component including the final one, so an
   ALLOW on P16 requires `subdir` to actually exist; without creating it
   first, a correct build DENIES P16 via decision 7 and the row cannot
   read ALLOW.
5. **Proof standard (resolves NF3).** Direct payload probes against the
   scripts, run and recorded by hand (the shape both gate rulings used),
   are the ONLY accepted proof of confinement for this plan's DONE-WHENs.
   `evals/README.md`'s own rule (`setup.files` row) materializes fixtures
   in a fresh temp dir and forbids them touching this repo — a repo-path
   escape is structurally unreachable there, so a fixture can supplement
   but never substitute for a direct probe. Any later plan that reuses
   this file's functions inherits this same proof standard by reference,
   not by re-deriving it.
   **Scope of the confinement claim (addresses N4's overclaim; narrowed by
   G3 — OWNER DECISION):** this standard proves PATH-TOKEN confinement —
   confinement of the path argument's text — GIVEN the command reaches
   `:291`'s check at all. It does not claim the check is unavoidable:
   `rm -r <repo> &`, `(rm -r <repo>)`, and `{ rm -r <repo>; }` each skip
   the check entirely today (`split_command` handles `&&`/`||`/`;`/`|`
   but not a single `&` or a grouping construct) and are live-confirmed
   ALLOWED regardless of anything this plan changes. That gap is
   pre-existing, orthogonal to `is_temp_path`/`normalize_path`, and the
   owner has decided it becomes its own plan, `docs/plans/executor-guard-splitter.md`
   (command-splitting coverage), which ships BEFORE this plan — not
   solved, widened, or otherwise touched here. Decision 8 additionally
   denies any path token containing an unexpanded shell metacharacter,
   closing the gap where the real destination is unknowable to a
   text-level guard, given the check is reached — "confinement" here does
   not assume visibility into shell expansion the guard doesn't have.
   This is distinct from decision 4's chained-`cd` limit, which stays an
   open, recorded limit. `docs/plans/executor-fast-read.md` inherits this
   narrowed proof standard by reference, not by re-deriving it.
6. **Rationale correction (resolves NF8).** Fix the header comment's claim
   that lead/judge's `rm` denial fires "before any path is examined."
   State instead: `:291` does examine paths; lead/judge's blanket
   write-denial is unconditional and simply never reaches that check.
7. **Return contract and fail-closed sentinel (resolves N3).**
   `normalize_path` returns 0 with the resolved absolute path on stdout on
   success. It returns non-zero and prints nothing on any of: hop-budget
   exhaustion (decision 1's cap), a detected symlink cycle, a path
   component that does not exist, a `readlink` failure, a permission
   (EACCES) failure reading or stat-ing a component, or an unexpanded
   shell metacharacter in the raw token (decision 8). The call site
   (`:291`) treats a non-zero return as NOT-temporary — DENY — and never
   calls `is_temp_path` on a partial or absent result. This closes the
   gap the ruling names: a hop-budget-exhausted PARTIAL prefix that
   happens to sit under `/private/tmp` must not be treated as a match,
   because the walk never reached the real terminal path — a partial
   success is not a success.
   **Existence-check scope (resolves G2):** the "component that does not
   exist" failure applies to EVERY component of the walk, including the
   FINAL component, in BOTH `parent` and `full` modes. Decision 3's mode
   split governs symlink DEREFERENCE at the final component only — never
   whether the final component's existence is checked. A relative token
   that resolves to a nonexistent final path (e.g. P16 before `subdir` is
   created) is therefore DENIED regardless of mode, the same as a
   nonexistent intermediate component.
   **EACCES detection is best-effort (resolves G6):** in Bash 3.2,
   `[ -L path ]` and `[ -e path ]` both return false identically for "not
   a symlink" and "parent directory not searchable" — there is no
   3.2-portable test that distinguishes the two. An unreadable component
   may therefore be silently under-resolved rather than triggering the
   EACCES failure this contract names; this is a stated best-effort
   limit, not a solved case. The failure direction is safe: the same
   permission failure that defeats detection here also blocks the
   underlying `rm` from ever reaching that path, so under-detection does
   not create an exploitable escape.
   **Post-release amendment — nonexistent/glob-bearing final component
   (regression fix, commit `186b1ba`; narrowed on purpose).** A
   nonexistent or glob-bearing (`*`, `?`, or `[`) FINAL component is
   acceptable ONLY when ALL of:
   1. Every intermediate component resolved successfully — structural,
      not a new check: an intermediate that does not exist, or cannot be
      resolved, still returns non-zero above before the walk ever reaches
      the final component.
   2. The resolved parent prefix — the final component's parent, as
      already resolved by the walk, joined with a trailing `/` — passes
      `is_temp_path`'s anchored test.
   3. The raw input path carries no trailing slash. A trailing slash
      forces `full` mode (this decision's trailing-slash override,
      above) — that case keeps the existing strict behavior; a dangling
      final symlink under a trailing slash still denies.
   When all three hold, `normalize_path` returns the resolved parent
   joined with the LITERAL final component — never dereferenced, never
   glob-expanded — and the caller's own `is_temp_path` call on that
   string decides, exactly as any other success. When any fails,
   decision 7's original fail-closed return stands. A glob metacharacter
   in ANY INTERMEDIATE component still denies outright, independent of
   whether that literal component happens to exist on disk — an
   intermediate glob that DID exist as a real directory would otherwise
   be walked into as ordinary text, and that is exactly the shape (P10)
   that lets a later `..` climb out once the shell actually expands it;
   this is checked explicitly, not left to the coincidence of a
   literally-glob-named path being absent.
   **Consequence for P9 (not a reopened bypass):** P9's dangling relative
   symlink resolves, in `parent` mode, to a nonexistent final component
   (`reltarget` itself — the symlink is never dereferenced at the final
   position in `parent` mode; `[ -e ]` still fails because it follows the
   symlink chain to test the TARGET, which is absent) whose resolved
   parent is confined. All three conditions above hold, so P9 now ALLOWs.
   This is not an escape: the returned path is the literal, unexpanded
   `<scratchpad-subpath>/reltarget` — physically inside the scratchpad —
   and `rm -r` in `parent` mode unlinks the symlink itself rather than
   following it, so the underlying operation is ordinary temp cleanup,
   the same class this amendment exists to allow. P9's row below is
   revised accordingly; no other row's expectation changes.
   **Pre-existing defect found and fixed while implementing this
   amendment (not itself a decision, recorded here since it lives beside
   decision 7's code):** `_path_guard_split`'s prior body used `for part
   in $s` on an unquoted `$s` — bash performs pathname (glob) expansion
   on each word of an unquoted list expansion, so a component consisting
   of a bare `*`/`?`/`[...]` was silently expanded against the CALLER'S
   CWD instead of preserved literally. This was invisible before this
   amendment (any resulting path still failed the existence check either
   way, so the end result was DENY regardless of the corruption), but
   this amendment's ALLOW path depends on the final component staying
   byte-for-byte literal, so the defect became load-bearing and was
   fixed as part of this change (pure parameter-expansion slicing,
   `scripts/path-guard-lib.sh`'s `_path_guard_split`) rather than left
   for a later plan.
8. **OWNER DECISION — unexpanded shell metacharacters deny outright
   (resolves N4; trigger set widened by F2, widened again by G1, never
   weakened).** Before any component walk, `normalize_path` scans the RAW
   path token, as the guard receives it pre-expansion (after decision
   12's quote-stripping), for a literal `$`, a backtick, the two-character
   sequence `$(`, a literal `{` (brace expansion — F2: `/private/tmp/{x,..}`
   carries no `$`/backtick, normalizes to itself unchanged, and would
   ALLOW without this addition, while the shell expands it to
   `/private/tmp/x /private/tmp/..` and deletes `/private`), OR a token
   whose FIRST character is `~` (tilde/home-directory expansion — G1,
   same shape and rationale as `{`: `rm -r ~` with a temp `.cwd` carries
   no `$`/backtick/`{`, resolves against `.cwd` to `<scratchpad>/~`, which
   the unchanged, unanchored `scratchpad` component match in
   `is_temp_path` ALLOWs, while the shell expands `~`/`~user`/`~+`/`~-` to
   the caller's home directory (or `OLDPWD`/`PWD`) before `rm` ever sees
   it — `rm -r ~` is DENIED today and this plan must not turn it into an
   ALLOW). If any is present, `normalize_path` returns non-zero per
   decision 7's contract — DENY — with no further normalization
   attempted. Rationale: the guard
   inspects the command as text before the shell expands anything, so the
   real path is unknowable. The dangerous shape is a path that looks
   temporary at the front and then continues with unexpanded text —
   `rm -rf /tmp/$X` is allowed today and would stay allowed after
   normalization alone. A path with no temporary-looking prefix is
   already denied, so this only affects deletes whose safety depends on
   text the guard cannot see. An agent that hits the denial spells the
   path out or reports back. This is a decision, not a recorded limit —
   the owner considered leaving it as a documented residual limit beside
   the chained-`cd` limit (decision 4) and rejected that option in favor
   of denial.
9. **Load path and failure behavior (resolves N5).**
   `scripts/executor-guard.sh` sources the library as `source
   "$(dirname "${BASH_SOURCE[0]}")/path-guard-lib.sh"` — the repo's own
   idiom, already used at `scripts/setup-watchdog.sh:9` — so the load
   resolves correctly regardless of the hook's invocation cwd
   (`hooks/hooks.json:9` invokes the guard via
   `${CLAUDE_PLUGIN_ROOT}/scripts/executor-guard.sh`; cwd at hook time is
   the user's project, not this repo). `scripts/executor-guard.sh` sets
   only `set -uo pipefail` (no `-e`), so a failed `source` (file missing,
   unreadable, or a syntax error) does not itself abort the script.
   Instead, `normalize_path`/`is_temp_path` are left undefined; the call
   at `:291` (`is_temp_path "$p" || all_temp=0`) then fails with bash's
   "command not found" (exit 127), which is falsy, tripping
   `all_temp=0` and denying the recursive delete. The existing loop
   structure fails closed on a broken source without needing `-e` —
   deliberately noisy over silently weaker, matching gate-01's own
   assessment (`gate-01:42`): "a broken `source` denies every recursive
   delete — noisy, never weaker."
10. **Sourceability check, concrete form (resolves N6; F7 correction).**
    Replace the exit-code-only check with two automatable assertions: (a)
    `printf 'MARKER\n' | bash -c 'source scripts/path-guard-lib.sh; read
    -r l; test "$l" = MARKER'` exits 0 — proves the library did not
    consume stdin; (b) after sourcing, `declare -F` lists `normalize_path`
    and `is_temp_path`, PLUS optionally any internal helper named with a
    `_path_guard_` prefix (an internal helper the component walk
    plausibly needs is permitted) — no OTHER function name is permitted.
    `grep -n '^[^[:space:]#]'` against the file (non-indented,
    non-comment, non-blank lines — this repo's function bodies are
    2-space-indented, so column-0 lines are top-level by convention) is a
    BEST-EFFORT check only, by this repo's own indentation convention —
    it does not catch a bare `set`/`exit` deliberately indented to dodge
    it; reviewer inspection (PT1's DONE-WHEN) is the backstop for that.
11. **Anchored temp-prefix matching (resolves F5).** `is_temp_path()`'s
    three temp-prefix cases anchor at the START of the string, not as a
    substring: `"/tmp/"*`, `"/private/tmp/"*`, `"/private/var/folders/"*`
    (previously `*"/tmp/"*`, `*"/private/tmp/"*`, `*"/var/folders/"*`).
    The `scratchpad` component match is UNCHANGED — still a path-component
    match, not anchored, since a scratchpad directory can validly sit
    deeper in a temp tree. This narrows "temporary" to exactly the
    settled confinement set — `/tmp`, `/private/tmp`, `/private/var/folders`,
    or any path with a `scratchpad` component — so a directory literally
    named `tmp` anywhere else (e.g. `<repo>/tmp/x`) no longer qualifies as
    temporary (F5: `is_temp_path` matched it as a substring today). The
    unresolved `/var/folders/` form is dropped from the anchor set, not
    merely re-anchored: decision 3's caller (`:291`) only ever calls
    `is_temp_path` on `normalize_path`'s OUTPUT, which has already
    resolved the `/var` symlink hop, so a bare unresolved `/var/folders/...`
    string never reaches this function in practice.
12. **Quote stripping before testing (resolves G4).** As the FIRST step of
    `normalize_path`, before decision 8's metacharacter scan and before
    the component walk, a single matching pair of surrounding quotes — a
    leading and trailing `'`, or a leading and trailing `"`, and only if
    both are present and match — is stripped from the raw path token.
    `'/private/tmp/foo'` is tested as `/private/tmp/foo`; an unquoted
    token is unaffected; an unmatched or interior quote character is left
    alone (best-effort, not a shell parser — matches decision 10's own
    best-effort framing). Without this, decision 11's anchoring newly
    DENIES a quoted temp path that was ALLOWed unquoted: `quote_walk`'s
    literal token retains the quote characters (`scripts/executor-guard.sh:150,163`),
    so the anchored prefix test (which requires the string to START with
    `/tmp/` etc.) sees a leading `'` or `"` and fails — a real regression
    on a common invocation shape, since every existing probe row is
    unquoted. A build that omits this stripping denies every quoted
    temp-path `rm -r` call that used to be ALLOWed.

## Task list

**PT1 — Extract `scripts/path-guard-lib.sh`** [executor-smart BUILD,
gated by review-agent — GATE-INFRA]
- Files: new `scripts/path-guard-lib.sh`; `scripts/executor-guard.sh`
  (remove inline `is_temp_path()`, add the `source` line per decision 9).
- Depends on: none.
- Move `is_temp_path()`, anchoring its three temp-prefix cases per
  decision 11 (the `scratchpad` component match is unchanged). Add
  `normalize_path <path> <cwd> <mode:parent|full>` per decisions 1, 3, 4,
  7, 8, 12 (quote-stripping runs first, inside `normalize_path`, before
  decision 8's metacharacter scan).
- **Platform constraint (resolves N8):** target Bash 3.2
  (`bash --version` on this platform → 3.2.57) — no `mapfile`/
  `readarray`, no associative arrays, no `${var,,}`/`${var^^}` case
  conversion, no `&>>`. `bash -n` only parses syntax; it will not catch a
  Bash-4-only construct that is syntactically valid in 3.2 but undefined
  or wrong at runtime — review-agent must confirm 3.2-only usage by
  inspection, not rely on `bash -n` for this.
- DONE-WHEN:
  - `bash -n` passes on both files;
  - decision 10's marker-pipe check exits 0 and the static
    top-level-functions / no-bare-`set`-or-`exit` check passes;
  - direct probes against `normalize_path`/`is_temp_path` prove every row
    of the probe table (below), P1-P28 — all 28 rows carry a "PT1 direct"
    verification, including P8 (PT1-only, since no write-path hook exists
    in this plan's scope to re-run it live).

**PT2 — Wire `scripts/executor-guard.sh:291` + fix the rationale**
[executor-smart BUILD, gated by review-agent — GATE-INFRA]
- Files: `scripts/executor-guard.sh`.
- Depends on: PT1.
- At the recursive-delete check, extract `.cwd` from the payload (decision
  4) and call `normalize_path "$p" "$cwd" parent` on every path token
  before matching with `is_temp_path`. Per decision 7: if `normalize_path`
  returns non-zero for any token, treat that token as NOT-temporary
  (`all_temp=0`) without calling `is_temp_path` on it. Add the chained-`cd`
  limit as a header comment. Correct the header rationale per decision 6.
- DONE-WHEN: every probe table row tagged "PT2 live" runs end-to-end
  against the live script (dispatched with `agent_type: executor-fast`)
  and returns its expected result — that is P1-P7 and P9-P28 (P8 has no
  live write-path call site in this plan's scope, so it stays a PT1-only
  direct-function probe); header states the corrected rationale and the
  chained-cd limit; review-agent verdict CLEAR.

**PT3 — Release** [release skill, all six phases — GATE-INFRA surface:
`scripts/`]
- Files: none directly.
- Depends on: PT1, PT2 merged to the candidate branch.
- READY re-runs the full probe table live (not `bash -n` alone) as the
  objective shell gate, per decision 5.
- DONE-WHEN: PR open citing a RULE verdict naming the PR's head commit;
  user merges; SEAL posts tag + CI result.

## Probe table

Every row is dispatched (PT2/PT3) or called directly (PT1) against
`normalize_path`/`is_temp_path`/`scripts/executor-guard.sh`. `<repo>` =
this repo's absolute path; `<scratchpad>` = a scratchpad dir under
`/private/tmp/claude-*`; `<repo-rel>` = `Users/<user>/maddog-skills` —
the repo's path with the leading `/` stripped, used only immediately
after a `..` hop so the row's shape stays one composed path string
rather than two concatenated absolute paths (resolves F8). Agent
identity is `executor-fast` for every live-hook row — lead/judge never
reach `:291` (see "Why this exists"), so re-probing under those
identities would not exercise this defect. "Discriminates" states what a
plausible wrong build does differently on that exact row; a row with no
such build is named as a control, not a discriminator.

| ID | Shape | Resolves | Agent identity | Verified at | Expected | Discriminates |
|---|---|---|---|---|---|---|
| P1 | `rm -r /tmp/../<repo>` | original defect | executor-fast | PT1 direct + PT2 live | DENY | denies via decision 7 (nonexistent component — G5): `/tmp/..` resolves to `/private`, so the composed path is `/private/Users/...`, which does not exist; a wrong build with no normalization instead sees the raw string still contains the `/tmp/` substring pre-collapse and ALLOWs. |
| P2 | same target via a symlink planted inside `<scratchpad>` | original defect | executor-fast | PT1 direct + PT2 live | DENY | no mid-path symlink dereference: wrong build treats the symlink as opaque, sees only the `scratchpad` component, and ALLOWs. |
| P3 | `rm -r <scratchpad>/../<repo-rel>` | original defect | executor-fast | PT1 direct + PT2 live | DENY | denies via decision 7 (nonexistent component — G5): the composed path lands under `<scratchpad>`'s parent joined with `Users/...`, which does not exist; a wrong build with no normalization instead relies on the raw string still containing the `scratchpad` component and ALLOWs. |
| P4 | `rm -r <repo>` (no `..`) | original defect (control) | executor-fast | PT1 direct + PT2 live | DENY | control, no discriminator — any build that ever ALLOWs the bare repo path has a broken `is_temp_path`, not a normalization defect. |
| P5 | intermediate (non-trailing) symlink mid-path pointing into `<repo>` | NF1 | executor-fast | PT1 direct + PT2 live | DENY | wrong build resolves only lexically (never dereferences the mid-path symlink) and ALLOWs because the raw text still looks temp. |
| P6 | lexical `..` collapse crossing a symlink boundary | NF1 | executor-fast | PT1 direct + PT2 live | DENY | wrong build pre-collapses `..` against the raw, unresolved path (decision 1's forbidden reading) and stays inside the apparent temp dir → ALLOWs; correct build resolves the symlink first, then collapses against the resolved prefix, and escapes. |
| P7 | `rm -r` of a repo symlink pointing at a temp dir, `parent` mode | NF4 | executor-fast | PT1 direct + PT2 live | DENY (symlink itself, not target) | wrong build dereferences the final-component symlink in `parent` mode (violates decision 3) and resolves to the temp target → ALLOWs. |
| P8 | `full`-mode call of the same symlink, direct against `normalize_path` (no write hook exists in scope) | NF4 | n/a — direct function call | PT1 direct only | resolves to the real temp target | wrong build refuses to dereference the final component even in `full` mode and returns the unresolved repo-symlink path. |
| P9 | `rm -r /tmp/rel-link`, `/tmp/rel-link` a symlink with a RELATIVE target `../<repo-rel>` | N1 (fail-closed control, F6); expected value revised by the post-release amendment | executor-fast | PT1 direct + PT2 live | ALLOW (was DENY pre-amendment) | not a discriminator for N1/F6 (unchanged: a correct build and an N1-wrong build both land on the same nonexistent final component either way). Post-amendment: the resolved parent (the symlink's own directory) is confined and the raw path carries no trailing slash, so decision 7's amendment ALLOWs the literal, undereferenced symlink path — ordinary temp cleanup, not an escape (see decision 7's "Consequence for P9" note). A wrong build that dereferences the final symlink in `parent` mode (violates decision 3, same defect P7 catches) would instead resolve the RELATIVE target and, depending on N1 correctness, land somewhere else entirely. |
| P10 | `rm -r /tmp/*/../../Users/<user>/maddog-skills` (glob into `/tmp`, then lexical `..` climbs across the `/tmp`→`/private/tmp` symlink boundary) — ruling-named shape | N1 / NF1 | executor-fast | PT1 direct + PT2 live | DENY | denies via decision 7 (nonexistent component — G5): the correct resolution lands on a path that does not exist under `/private`; a wrong build lexically pre-collapses `..` before the shell's glob-expanded segment is resolved through the symlink and ALLOWs instead. |
| P11 | `rm -r /tmp/link/` (trailing slash), `link` → repo dir — ruling-named shape | N2 | executor-fast | PT1 direct + PT2 live | DENY | wrong build has no trailing-slash override, stays in `parent` mode, leaves the final symlink undereferenced, and ALLOWs (looks temp lexically). |
| P12 | `rm -r /tmp/cycle-a/x`, `cycle-a` → `cycle-b` → `cycle-a` (cycle at an INTERMEDIATE component — F3: a final-position cycle is never dereferenced under `parent` mode and cannot exercise this) | N3 | executor-fast | PT1 direct + PT2 live | DENY | wrong build with no hop-budget/cycle bound loops indefinitely instead of denying; a build that bounds hops but returns success on a partial prefix under `/private/tmp` wrongly ALLOWs — the exact gap decision 7's sentinel closes. |
| P13 | `rm -rf /tmp/$X` — ruling-named shape | N4 (owner decision) | executor-fast | PT1 direct + PT2 live | DENY | wrong build has no decision-8 metachar scan; the raw token still looks temp lexically pre-expansion and ALLOWs. |
| P14 | `` rm -rf /tmp/$(cat /tmp/p) `` — ruling-named shape | N4 (owner decision) | executor-fast | PT1 direct + PT2 live | DENY | same as P13, for the `$(` trigger. |
| P15 | `` rm -rf /tmp/`cat /tmp/p` `` (backtick form) | N4 (owner decision) | executor-fast | PT1 direct + PT2 live | DENY | same as P13, for the backtick trigger. |
| P16 | payload `.cwd` = `<scratchpad>` (arranged per decision 4's probe setup); `rm -r subdir` (relative, no `..`, stays inside `<scratchpad>`) | N7 / NF7 | executor-fast | PT1 direct (explicit cwd arg) + PT2 live | ALLOW | wrong build never extracts/resolves against `.cwd` and either denies a legitimate temp-relative delete (false-positive DENY) or resolves the relative token against the wrong base entirely. |
| P17 | payload `.cwd` = `<scratchpad>` (arranged per decision 4's probe setup); `rm -r ../../Users/<user>/maddog-skills` (relative `..` walk out of `<scratchpad>` into `<repo>`) | N7 / NF7 | executor-fast | PT1 direct (explicit cwd arg) + PT2 live | DENY | denies via decision 7 (nonexistent component — G5): two `..` hops from a six-deep scratchpad land short of `<repo>`, on a path that does not exist; a wrong build instead resolves `.cwd` but treats the relative token as opaque (no `..` collapse against it) and ALLOWs since the raw token never matches a temp substring. |
| P18 | `rm -r /tmp/..` — F1 | F1 | executor-fast | PT1 direct + PT2 live | DENY | wrong build reads decision 3's mode split as skipping `.`/`..` collapse at the final component, stops at `/private/tmp`, and ALLOWs; correct build collapses the final `..` to `/private`, which decision 11's anchored matcher denies. |
| P19 | `rm -r /var/folders/..` — F1 | F1 | executor-fast | PT1 direct + PT2 live | DENY | same as P18, after the `/var`→`/private/var` symlink hop: wrong build stops at `/private/var/folders` and ALLOWs; correct build collapses to `/private/var` and denies. |
| P20 | `rm -r /private/tmp/{x,..}` — F2 | F2 | executor-fast | PT1 direct + PT2 live | DENY | wrong build's decision-8 scan omits `{`; the literal token carries no `$`/backtick, normalizes to itself, and ALLOWs, while the shell would expand the brace and delete `/private`. |
| P21 | `rm -r <repo>/tmp/x` (a directory literally named `tmp` inside the repo, CREATED before the live PT2 run so decision 7's existence check cannot confound this row — G5) — F5 | F5 | executor-fast | PT1 direct + PT2 live | DENY | wrong build's `is_temp_path` matches `/tmp/` as an unanchored substring anywhere in the string and ALLOWs; the anchored matcher (decision 11) requires the string to START with a temp prefix (or carry a `scratchpad` component) and denies. |
| P22 | `rm -r ~` (bare tilde) — G1 | G1 (owner decision) | executor-fast | PT1 direct + PT2 live | DENY | wrong build's decision-8 scan has no leading-`~` trigger; `.cwd` resolution yields `<scratchpad>/~`, which the unchanged, unanchored `scratchpad` component match ALLOWs, while the shell expands `~` to the caller's home directory. |
| P23 | `rm -r '<a-temp-path>'` (P16's `subdir`, single-quoted; `subdir` CREATED first — same precondition as P16) — G4 | G4 | executor-fast | PT1 direct + PT2 live | ALLOW | wrong build skips decision 12's quote-stripping; the literal token retains its surrounding quote marks, fails decision 11's anchored prefix test (which requires the string to START with a temp prefix), and DENIES a legitimate quoted temp-path delete. |
| P24 | `rm -rf /tmp/already-gone-<unique>` (directory does not exist; regression repro) | post-release amendment | executor-fast | PT1 direct + PT2 live | ALLOW | wrong build keeps decision 7's pre-amendment uniform existence check and DENIES; correct build's resolved parent (`/tmp`) passes `is_temp_path` and ALLOWs the literal nonexistent path. |
| P25 | `rm -rf <scratchpad>/globtest/*` (glob as FINAL component; `globtest` contains real files so the glob is not itself a stand-in for "nonexistent") — regression repro | post-release amendment | executor-fast | PT1 direct + PT2 live | ALLOW | wrong build either keeps the pre-amendment strict check (DENY) or, if `_path_guard_split` still glob-expands the final component against its own CWD (the pre-existing defect fixed alongside this amendment), corrupts the walk and does not resolve to the literal `.../globtest/*` string at all — either way it fails to ALLOW on the correct literal path. |
| P26 | `rm -r <scratchpad>/*/leaf` — a directory LITERALLY named `*` is created under `<scratchpad>` containing `leaf`, so this is the strong form: the intermediate glob component actually exists on disk | post-release amendment | executor-fast | PT1 direct + PT2 live | DENY | wrong build has no explicit intermediate-glob check and relies only on existence; since the literal `*`-named directory and `leaf` both exist, a wrong build walks straight through and ALLOWs — the exact P10-shaped escape (an intermediate glob that expands to something real, then climbs out) this explicit check exists to close. |
| P27 | `rm -r <scratchpad>/nonexistent-dir-xyz/leaf` (intermediate component does not exist; no glob involved) | post-release amendment (regression-adjacent control) | executor-fast | PT1 direct + PT2 live | DENY | control, no discriminator specific to this amendment — confirms the amendment's relaxation is scoped to the FINAL component only; any build that ALLOWs a nonexistent INTERMEDIATE component has broken decision 7 far more broadly than this amendment intends. |
| P28 | `rm -r /Users/<user>/does-not-exist-outside-temp-test-xyz` (nonexistent final component, resolved parent is NOT a temp location) | post-release amendment | executor-fast | PT1 direct + PT2 live | DENY | wrong build tests `is_temp_path` on the wrong string (e.g. always true, or omits the parent-confinement check entirely) and ALLOWs a nonexistent path anywhere on the filesystem; correct build's `is_temp_path` on the resolved parent (`/Users/<user>`) fails the anchored test and denies. |

28 rows total (P1-P28); P8 is the only PT1-only row — no write-path hook
exists in this plan's scope to re-run it live. P9's expected value is
ALLOW (revised by the post-release amendment; see decision 7 and P9's
row for why this is not a reopened bypass) — every other row's expected
value is unchanged from round 3.

## Release sequence

Per `.claude/skills/release/SKILL.md`: `scripts/` is GATE-INFRA, so the
INTERNAL/DOCS-only shortcut does not apply — full six phases.

1. **DECLARE**: sync to `origin/main`; delta class is a fix to shipped
   GATE-INFRA — user rules the version bump; version + CHANGELOG commit.
2. **READY**: `bash -n` on both files; the full probe table (above) run
   live; repo-wide grep sweep for any other caller of the removed inline
   `is_temp_path()` definition; CHANGELOG check.
3. **BEHAVIOR**: not description-routing-relevant (no agent frontmatter
   touched) — record as not applicable rather than UNVERIFIED.
4. **RULE** (executor-judge, fix-less): dispatch one adversarial
   release-review; evidence = candidate diff, READY results, the probe
   table. Verdict CLEAR or BLOCKED naming head SHA.
5. **SHIP**: push candidate branch; open/update PR citing the RULE
   verdict and every READY result. STOP — never merge; user merges.
6. **SEAL**: tag `vX.Y.Z`; `claude plugin tag --push`; confirm CI green;
   post SEAL comment on the merged PR.

## NOTES

- This plan does not create any Write-scoping hook — that stays in
  `docs/plans/executor-fast-read.md`, which sources
  `scripts/path-guard-lib.sh` and must call `normalize_path` in `full`
  mode for its write-path check (decision 3).
- `is_temp_path()`'s matching logic changes in exactly one respect —
  decision 11 anchors the three temp-prefix cases at string start; the
  `scratchpad` component match is unchanged. What it is called with also
  changes (`normalize_path`'s resolved, already quote-stripped output,
  never a raw token).
- Judgment call: N1 and N2 are folded into decisions 1 and 3 as
  amendments rather than given their own decision numbers, since each is
  a refinement of the algorithm/mode decision it clears, not an
  independent design choice. N3, N4 (owner), N5, N6 are new numbered
  decisions (7-10) since none has an existing decision to attach to.
  F5 is a new numbered decision (11) for the same reason; F1-F4, F6-F8
  are folded as corrections into the decisions/probes they clear, per
  round 2's own framing of F1/F2 as amendments to existing decisions.
  G4 (quote stripping) is a new numbered decision (12) for the same
  reason as F5/N3-N6: no existing decision covers pre-scan token
  cleanup. G1 (owner), G2, G3 (owner), G5, G6 are folded as amendments
  into decisions 8, 7, 5, and the probe table respectively, per the same
  framing.
</content>
