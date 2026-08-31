# Gate 01: Executor Guard Normalization (Round 1 Design Review)

*Filed 2026-08-31*

MODE: DESIGN-REVIEW (round 1 of 3).

## VERDICT

**BLOCKED** — the normalization spec is silent on three cases that occur on the first hop of every path on this platform (relative symlink targets, trailing slashes, resolution failure), its sourceability DONE-WHEN cannot fail, and the `.cwd` path it adds has no probe.

## CARRIED FINDINGS

| # | State | Evidence |
|---|---|---|
| NF1 | RESOLVED (shape) | Decision 1 (`plan:37-46`) specifies the per-component walk from root, `..` against the resolved prefix only, hop budget; probes 5+6 added (`plan:139-140`). Underspecified — see N1-N3. |
| NF2 | RESOLVED (task) | PT1 creates `scripts/path-guard-lib.sh` (`plan:88-95`). Confirmed the blocker was real: `executor-guard.sh:222` reads stdin at top level, body runs to `:499`. DONE-WHEN defective — N5, N6. |
| NF3 | RESOLVED | Decision 5 (`plan:72-80`) makes direct probes the sole proof; `evals/README.md:66` confirms fixtures run in a fresh temp dir and "never touch this repo". Overclaims scope — N4. |
| NF4 | RESOLVED | Decision 3 (`plan:55-63`) splits `parent`/`full`; probes 7+8 give both directions (`plan:141-145`). Gap at trailing slash — N2. |
| NF7 | **STILL OPEN** | The limit is recorded (decision 4, `plan:64-71`), but NF7 also required DONE-WHEN to *assert* `.cwd` extraction. Probes 1-8 contain no relative path; PT2's DONE-WHEN (`plan:117-122`) lists only absolute cases. See N7. |
| NF8 | RESOLVED | `plan:27-33` + decision 6 state the corrected rationale; matches `executor-guard.sh:291` (examines paths) and `:419-421` (unconditional `rm` deny). NF8's second half (the T8/T9 citation) belongs to the other plan. |

## NEW FINDINGS

1. **LOAD-BEARING — relative symlink targets unspecified** (`plan:41-43`). "Resolve it (one `readlink` hop) and continue walking its target's components" does not say against what. Evidence: `readlink /var` → `private/var`, `readlink /tmp` → `private/tmp` — every root-level symlink on this machine returns a *relative* target. An implementation that restarts from root resolves `/a/b/link -> ../secret` to `/secret`, not `/a/secret`. Clears: state that an absolute target replaces the resolved prefix and a relative target resolves against the symlink's parent; add a relative-target probe.
2. **LOAD-BEARING — trailing slash defeats `parent` mode** (`plan:55-60`, `plan:141-143`). "Every component except the final one" is undefined when the path ends in `/`. The kernel dereferences a trailing symlink when a slash follows — evidence: `ls -ld /var` shows the link, `ls -ld /var/` shows the directory. `rm -r /tmp/link/` is ALLOWED today (probed) and stays ALLOWED under `parent` mode. Clears: a trailing slash forces `full` mode; add it as a probe.
3. **LOAD-BEARING — no failure contract** (`plan:37-46`). Nothing states the return channel, nor what is returned on hop-budget exhaustion, a symlink cycle, a nonexistent component, `readlink` failure, or EACCES. Both callers currently fail closed only by accident (`is_temp_path ""` → false). A budget-exhausted *partial* prefix under `/private/tmp` would ALLOW. Clears: specify the return contract and a fail-closed sentinel; probe a cycle.
4. **LOAD-BEARING — decision 5 overclaims "confinement"** (`plan:72-80`). Probed live: `rm -rf /tmp/$X` and `rm -rf /tmp/$(cat /tmp/p)` are ALLOWED, and `parent`-mode normalization leaves the unexpanded final component intact, so both stay ALLOWED after the fix. The probe set cannot fail on this class. Clears: record shell expansion/command substitution as a residual limit beside the chained-`cd` one, or deny an unexpanded `$`/backtick in a path token.
5. **LOAD-BEARING — the `source` path is unspecified** (`plan:90-92`). `hooks/hooks.json:9` invokes the guard as `${CLAUDE_PLUGIN_ROOT}/scripts/executor-guard.sh`; cwd at hook time is the user's project, so a bare `source scripts/path-guard-lib.sh` fails. Clears: specify `source "$(dirname "${BASH_SOURCE[0]}")/path-guard-lib.sh"` (the repo's own idiom, `scripts/setup-watchdog.sh:9`) and state the behavior when the source fails.
6. **LOAD-BEARING — PT1's sourceability DONE-WHEN cannot fail** (`plan:96-98`). `bash -c 'source scripts/path-guard-lib.sh'` exits 0 whether or not the lib consumed stdin, and "has no side effect" is not a testable predicate. Clears: `printf 'MARKER\n' | bash -c 'source …; read -r l; test "$l" = MARKER'`, plus an assertion that the lib defines only the two functions and runs no `set`/`exit`.
7. **LOAD-BEARING — the `.cwd` code path has zero coverage** (`plan:133-145`, `plan:117-122`). Decision 4 adds payload `.cwd` extraction and relative-path resolution; no probe in the accepted proof passes a relative path. Clears: add a relative-path probe to the probe set and to PT2's DONE-WHEN.
8. **MINOR — bash 3.2 is the platform shell** (`bash --version` → 3.2.57, arm64-apple-darwin25). `bash -n` parses `mapfile`/`readarray` fine and fails only at runtime, so PT1's syntax gate will not catch a bash-4-ism in the component-splitting loop. Clears: name the 3.2 constraint in PT1.

## DELEGATION LOG

executor-fast — run `rm`-semantics probes for BSD trailing-slash symlink behavior in a fresh `/private/tmp` dir — returned blocked: `executor-guard.sh` denied the probe's own `rm -r` (variable-form paths fail closed). No verdict was delegated.

## NOTES

- Premise verified first-hand against the live script: `rm -r /tmp/../<repo>` and `rm -r scratchpad/../agents` ALLOWED; plain and quoted repo paths DENIED. Also newly ALLOWED and outside the plan's probe set: `/tmp/*/../../Users/…` (normalization does close this one), `/tmp/$X`, `/tmp/$(…)`, `/tmp/link/`.
- **Suspected, not demonstrated:** that BSD `rm -r symlink/` deletes the *target directory's contents*. I proved only the kernel-level trailing-slash dereference. N2's spec gap stands either way.
- **Could not construct a false ALLOW from N1** — the relative-target divergences I tried all landed fail-closed. N1 is filed on spec completeness, not on a demonstrated bypass.
- **Partial merge is safe**, contingent on N5: PT1 alone leaves `:291` calling `is_temp_path` on the raw token exactly as today. A broken `source` denies every recursive delete — noisy, never weaker.
- **No gap with `docs/plans/executor-fast-read.md`.** It already declares the merge dependency (`:9-14`), sources the lib in `full` mode (`:266-273`), inherits the proof standard by reference, and instructs re-verification of shifted line numbers at T5 edit time (`:287-296`). No duplicated path logic remains there.
- Nothing in the working tree was modified.
