#!/usr/bin/env bash
# executor-guard.sh — PreToolUse Bash guard, scoped to executor-fast, executor-smart,
# executor-lead, and executor-judge.
#
# Purpose: two layers of enforcement, both structural (not instruction-based):
#
#  1. IRREVERSIBLE-COMMAND DENIAL (all four agents). These executors run at
#     reasoning effort levels or with permission modes where they cannot
#     reliably weigh one-way doors. This hook bounces a short list of
#     irreversible/destructive Bash commands (force-delete, force-push, hard
#     reset, mass discard of uncommitted work, etc.) back to the caller,
#     forcing the executor to STOP and return blocked rather than attempt the
#     command.
#
#  2. FILE-WRITE DENIAL (executor-lead and executor-judge only). Both agents
#     hold Bash for read-only inspection (grep, sed -n, git log/diff, jq, wc,
#     find, cat, head, tail, ls, diff, shellcheck) but must never write,
#     create, truncate, append to, move, or delete a file via Bash — that
#     invariant ("cannot fix/apply by construction") is enforced here, not by
#     instruction. executor-smart is deliberately NOT covered by this layer:
#     it holds Write/Edit and editing files is its job. This layer also
#     blanket-denies inline interpreters/scripting tools (python*, node*,
#     deno, bun, perl, ed, xargs) for lead outright, regardless of what it'd
#     do — lead's read-only toolset needs none of them, so a denial by binary
#     name costs it nothing real. executor-judge gets a narrower carve-out
#     (maintainer decision 2026-09-26, option A, tightened to a STRICT
#     ALLOWLIST 2026-09-27 after an independent release review found the
#     original inline-code blocklist incomplete): it may re-run gates
#     (agents/executor-judge.md:104, Core Law 3) through exactly these
#     forms, on python3/python2/python/node/nodejs/deno/bun, everything else
#     denies —
#       - `python <script.py>` [args...]: <script.py> must be an existing
#         regular .py file resolved inside cwd (path-guard-lib's
#         normalize_path/is-inside-cwd check, same helper the recursive-
#         delete check uses), and no token before it may start with '-'
#         (that alone closes every combined-short-flag form a python
#         command line allows, e.g. `-Ic`, `-Sc`, `-Bm`, `-W ignore -c`,
#         `-X dev -c` — none of these is "a bare script as the first
#         argument", so none of them can ever reach the file-existence
#         check at all); args after the script are its own and are not
#         inspected.
#       - `python -m pytest|unittest` [args...]: args after it may be only
#         an existing path inside cwd (file, dir, or path::nodeid — the
#         nodeid suffix past `::` is never inspected, only the path
#         component before it) or one of a narrow flag allowlist (-q, -qq,
#         -v, -vv, -x, -s, --tb=short|long|line|no|native, -k <expr>/-k=
#         <expr>, -r<chars>, --no-header, -l, --lf, --ff, -m <expr> for a
#         pytest marker expression — this -m only ever matches here, after
#         `-m pytest` already consumed python's own -m, so it can never be
#         confused with it). Everything else denies, INCLUDING -c, -p, -o,
#         --junitxml, --basetemp, --cache-clear, and `-m doctest` (doctest
#         can execute arbitrary code in any .py docstring it's pointed at;
#         no bound was found safe enough to allow — maintainer judgment
#         call, denied outright rather than guessed at).
#       - `node <script>` (.js/.mjs/.cjs), `bun <script>` or `bun run
#         <script>` (.js/.ts/.mjs/.cjs/.tsx), or `deno run <script>`
#         (.ts/.js): <script> must exist inside cwd and no token before it
#         may start with '-' — a bare package.json/deno-task script name
#         (`bun run build`, `node --run build`) has no such extension and
#         is never on disk at that name, so it fails the existence check
#         the same way a truly missing file would.
#       - `bun test`/`deno test` [paths...]: every arg after `test` must be
#         an existing path inside cwd; any flag denies.
#     A `-`/`/dev/*`/`/proc/self/fd/*` path argument, a process-substitution
#     `<(...)` argument, or a `<<` heredoc/here-string anywhere in the
#     command all deny regardless of the form above — none of those is a
#     real file on disk. `perl`, `ed`, and `xargs` stay denied outright for
#     judge too — perl's flag surface (`-e`/`-n`/`-p`/`-i`, freely
#     combinable) was judged too wide to allowlist safely, and neither `ed`
#     nor `xargs` runs a script file the way an interpreter does.
#
#     Wrapper/prefix stripping (both lead and judge): the classification
#     above (and the write-form denials just below it) runs against the
#     command with leading `VAR=val` assignments and any of `env`,
#     `command`, `exec`, `nice`, `nohup`, `time`, `timeout <duration>`, and
#     `stdbuf` (each with their own best-effort flag handling) peeled off
#     first — `env python3 -c 1`, `timeout 5 python3 -c 1`, `FOO=1 python3
#     -c 1`, etc. are classified as the `python3 -c 1` they really are, not
#     as `env`/`timeout`/an assignment falling through unclassified. A
#     shell binary (`sh`, `bash`, `zsh`, `ksh`, `dash`, `ash`) found as the
#     real command after that stripping denies outright for lead and
#     judge, with or without `-c` — this guard does not parse a shell's own
#     `-c` argument as a nested command line, so the only safe answer is to
#     deny the shell invocation itself; `sh -c "echo x > f"` and similar
#     never reach (and could not be reliably caught by) the write-form
#     checks below. Best-effort, not a shell parser: an unrecognized or
#     malformed wrapper invocation is left as its literal first word.
#
#     Rationale correction: an `rm -r` from lead/judge is NOT denied "before
#     any path is examined" — the recursive-delete check below (which calls
#     normalize_path/is_temp_path) runs for all four agents and DOES examine
#     the path first. lead/judge's file-write denial is unconditional and
#     simply never depends on that check's outcome: a temp-confined `rm -r`
#     passes the recursive-delete check, then falls through to this layer's
#     unconditional "rm deletes a file" denial regardless.
#
#     Known limit (chained `cd`, not solved here): the recursive-delete
#     check resolves a relative path against the PreToolUse payload's .cwd,
#     which tracks the session's current directory and updates whenever a
#     standalone `cd` Bash call runs — but NOT a `cd` chained inside the
#     SAME command as the path (split_command evaluates chained segments
#     independently, before that `cd` has executed). A `cd` issued as its
#     own, prior tool call IS reflected correctly.
#
# Wiring: plugin-level hooks/hooks.json (session-wide, matcher "Bash") fires
# this script for every agent and the main conversation. Because that wiring
# is not agent-scoped, the four-agent scoping is enforced IN-SCRIPT via the
# payload's .agent_type field: the guard's checks run only when agent_type is
# "executor-fast", "executor-smart", "executor-lead", "executor-judge", or
# ends in the plugin-namespaced forms (":executor-fast", ":executor-smart",
# ":executor-lead", ":executor-judge"). Every other case — a different
# agent_type, or agent_type absent (e.g. the main conversation) — ALLOWS
# (fail-open) immediately with no output.
#
# IMPORTANT: Claude Code hooks FAIL OPEN. If this file is missing, not
# executable, times out, or emits malformed JSON, the tool call proceeds as
# if no hook existed. This script is therefore a GUARD, not a security
# CONTROL — it catches the common irreversible/write patterns, it does not
# guarantee safety against a determined or unusual command.
#
# Protocol: read the PreToolUse JSON payload from stdin, inspect
# .tool_input.command, and either:
#   - print nothing and exit 0 (ALLOW), or
#   - print a hookSpecificOutput deny JSON and exit 0 (DENY, exit 2 would
#     also block but gives the model no reason — always use the JSON form).
# Any failure to parse input, or absence of jq, ALLOWS the call — never
# block on our own inability to inspect the command.

set -uo pipefail

# path-guard-lib.sh provides normalize_path/is_temp_path, shared with any
# future caller (e.g. a Write-scoping hook) instead of reimplementing path
# logic here. Loaded via a path relative to this script's own location so
# it resolves regardless of the hook's invocation cwd (hooks/hooks.json
# invokes this script via ${CLAUDE_PLUGIN_ROOT}/scripts/executor-guard.sh;
# cwd at hook time is the user's project, not this repo). This script sets
# only `set -uo pipefail` (no -e), so a failed source (file missing,
# unreadable, or a syntax error) does not itself abort the script — instead
# normalize_path/is_temp_path are left undefined, and the recursive-delete
# call site below fails with bash's "command not found" (exit 127, falsy),
# tripping all_temp=0 and denying the delete: a broken source denies every
# recursive delete — noisy, never weaker.
source "$(dirname "${BASH_SOURCE[0]}")/path-guard-lib.sh"

deny() {
  local reason="$1"
  local ctx="Blocked by executor-guard.sh: this executor is not permitted to weigh irreversible actions or write files via Bash. STOP and return blocked (VERDICT: STOP for executor-judge) to your caller with this reason — do not attempt the command."
  local reason_json ctx_json
  reason_json="$(printf '%s' "$reason" | jq -Rs .)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs .)"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  exit 0
}

# --- quote-aware walk -------------------------------------------------
# One shared character-by-character quote-tracking walk (mode-selected),
# reused everywhere in this file that needs to know whether a character
# sits inside single/double quotes — a single implementation, not one per
# call site that can drift out of sync.
#   mode="chain": splits a full command into pipeline/chain segments on
#     unquoted, unescaped &&, ||, ;, |, and a bare & (background operator;
#     excluded when it forms &> / &>> / an fd-duplication or -close form
#     like >&, 2>&1, >&- with an unescaped preceding >, or when the & itself
#     is escaped, e.g. find's own \& argument syntax) — e.g.
#     `grep -E "a|rm -rf|b"` stays ONE segment instead of re-parsing as a
#     pipeline containing a bogus `rm -rf` stage. A literal newline inside
#     the command also acts as a segment boundary, but by accident, not as
#     a case branch here: each finished segment is later fed through a
#     line-oriented reader by its caller, so a raw newline is indistinguishable
#     from that reader's own record separator — this happens regardless of
#     quote state, so a multi-line QUOTED argument is misjudged as multiple
#     commands too (a known, accepted false-positive source, not fixed here).
#     Separately, an unquoted leading `(`/`((`/`{` token in a segment (a
#     subshell, arithmetic command, or brace group) is denied fail-closed by
#     the caller rather than parsed into — this file does not attempt to see
#     inside one. Prints one segment (literal) per line.
#   mode="word": splits one segment into whitespace-separated argument
#     tokens, respecting quotes so a quoted argument containing spaces
#     (e.g. an awk/jq program) stays ONE token. In the same pass it builds
#     a MASKED companion for each token: every character consumed while
#     inside a quote (including the quote marks themselves) is replaced
#     with 'Q'. Redirect-style checks test the masked copy so a '>' that
#     exists only inside quotes (`grep '>' f`, `awk '$1 > 5'`) is never
#     mistaken for a real shell metacharacter; checks that need the real
#     text (rm/git/sed flag matching, path checks) keep using the literal
#     copy. Prints "literal<US>masked" per token, US = \x1f (0x1f, unlikely
#     to appear in a shell command), one per line.
# Best-effort: does not handle backslash-escaped metacharacters outside
# quotes, or backslash-escaped quotes inside double quotes, beyond a simple
# lookback — adequate for a guard, not a shell parser.
quote_walk() {
  local mode="$1" cmd="$2"
  local -a out=()
  local buf="" mbuf="" c in_single=0 in_double=0
  local esc=0 esc_next=0 buf_last_esc=0 split_amp=0
  local i=0 len=${#cmd}
  local US=$'\x1f'
  while [ "$i" -lt "$len" ]; do
    c="${cmd:i:1}"
    # esc = is THIS character escaped by an odd run of preceding, themselves-
    # unescaped, backslashes? Parity-tracked (not a 1-char lookback), so a
    # doubled backslash (`\\` = one literal backslash) correctly leaves the
    # character after it unescaped — e.g. `"a\\" > f` closes the quote at
    # the real closing `"` instead of treating it as escaped.
    if [ "$c" = "\\" ] && [ "$esc_next" -eq 0 ]; then
      esc=0
      esc_next=1
    else
      esc="$esc_next"
      esc_next=0
    fi
    if [ "$in_single" -eq 1 ]; then
      buf+="$c"
      mbuf+="Q"
      [ "$c" = "'" ] && in_single=0
      i=$((i + 1))
      continue
    fi
    if [ "$in_double" -eq 1 ]; then
      buf+="$c"
      mbuf+="Q"
      if [ "$c" = '"' ] && [ "$esc" -eq 0 ]; then
        in_double=0
      fi
      i=$((i + 1))
      continue
    fi
    if [ "$mode" = "word" ]; then
      case "$c" in
        ' '|$'\t')
          [ -n "$buf" ] && out+=("${buf}${US}${mbuf}")
          buf=""
          mbuf=""
          i=$((i + 1))
          continue
          ;;
      esac
    fi
    case "$c" in
      "'")
        if [ "$esc" -eq 0 ]; then
          in_single=1
          buf+="$c"
          mbuf+="Q"
        else
          buf+="$c"
          mbuf+="$c"
        fi
        ;;
      '"')
        if [ "$esc" -eq 0 ]; then
          in_double=1
          buf+="$c"
          mbuf+="Q"
        else
          buf+="$c"
          mbuf+="$c"
        fi
        ;;
      '&')
        if [ "$mode" = "chain" ] && [ "${cmd:i:2}" = "&&" ]; then
          out+=("$buf")
          buf=""
          i=$((i + 2))
          continue
        fi
        # Bare, unquoted, UNESCAPED '&' is a chain-mode segment boundary
        # (mirrors the ';' case below) UNLESS: the next char is '>' (&>/&>>
        # redirect forms), or the last character already written to buf is
        # an unescaped '>' (>&, 2>&1, 1>&2, >&- fd-duplication/close forms).
        # Gated to mode="chain" only — this arm is shared code, also
        # reached while tokenizing a segment in "word" mode, where a
        # residual '&' (inside &>/>& or escaped \&) must stay a literal
        # character, never a token boundary (a boundary here would emit an
        # out+=() line with no ${US}${mbuf} separator and silently blank
        # tokens_masked for that token).
        if [ "$mode" = "chain" ] && [ "$esc" -eq 0 ]; then
          split_amp=1
          [ "${cmd:i+1:1}" = ">" ] && split_amp=0
          if [ "$split_amp" -eq 1 ]; then
            case "$buf" in
              *'>')
                [ "$buf_last_esc" -eq 0 ] && split_amp=0
                ;;
            esac
          fi
          if [ "$split_amp" -eq 1 ]; then
            out+=("$buf")
            buf=""
            i=$((i + 1))
            continue
          fi
        fi
        buf+="$c"
        mbuf+="$c"
        ;;
      '|')
        if [ "$mode" = "chain" ]; then
          if [ "${cmd:i:2}" = "||" ]; then
            out+=("$buf")
            buf=""
            i=$((i + 2))
            continue
          fi
          out+=("$buf")
          buf=""
          i=$((i + 1))
          continue
        fi
        buf+="$c"
        mbuf+="$c"
        ;;
      ';')
        if [ "$mode" = "chain" ]; then
          out+=("$buf")
          buf=""
          i=$((i + 1))
          continue
        fi
        buf+="$c"
        mbuf+="$c"
        ;;
      *)
        buf+="$c"
        mbuf+="$c"
        ;;
    esac
    # Bookkeeping for the '&' lookbehind exclusion below: every non-continue
    # path above (quote literal-appends, the &/|/; literal-append
    # fallthroughs, and the default *) case) reaches this single point after
    # writing $c onto buf — record whether THIS just-written character was
    # itself escaped, so a later lookbehind can tell an escaped trailing '>'
    # (a literal argument character) from a genuine redirect '>' (reuses the
    # existing esc/esc_next parity, not a second parser).
    buf_last_esc="$esc"
    i=$((i + 1))
  done
  if [ "$mode" = "chain" ]; then
    out+=("$buf")
  else
    [ -n "$buf" ] && out+=("${buf}${US}${mbuf}")
  fi
  printf '%s\n' "${out[@]}"
}

split_command() {
  quote_walk chain "$1"
}

# --- executor-judge allowlist helper -----------------------------------
# Resolves $1 (a possible script/test-path argument) against $2 (the
# payload's cwd) via path-guard-lib's normalize_path (mode "full" — an
# interpreter opening this path for execution/reading follows a trailing
# symlink the same way a file read would). Prints the resolved path and
# returns 0 only when it exists AND sits at or inside the resolved cwd;
# returns 1 (nothing printed) for a nonexistent path, an escape outside
# cwd, an unexpanded shell metacharacter (normalize_path's own decision-8
# scan denies those), a stdin/fd argument (`-`, anything under /dev/*,
# /proc/self/fd/*), or an empty/absent cwd (fail closed rather than let an
# empty cwd resolve to "/", which would make every absolute path pass the
# containment check below).
_judge_resolve_in_cwd() {
  local tok="$1" cwd="$2" resolved resolved_cwd
  [ -z "$cwd" ] && return 1
  case "$tok" in
    -|/dev/*|/proc/self/fd/*) return 1 ;;
  esac
  resolved="$(normalize_path "$tok" "$cwd" full)" || return 1
  resolved_cwd="$(normalize_path "$cwd" "$cwd" full)" || return 1
  case "$resolved" in
    "$resolved_cwd"|"$resolved_cwd"/*)
      printf '%s\n' "$resolved"
      return 0
      ;;
    *) return 1 ;;
  esac
}

# --- wrapper/prefix stripping (lead/judge file-write classification) ---
# Mutates the caller's GLOBAL `tokens`/`tokens_masked` arrays in place
# (Bash 3.2: no nameref) so a wrapper cannot launder a write-form or
# interpreter invocation past the classification that follows. Peels, in a
# loop (wrappers can chain, e.g. `nice nohup timeout 5 env FOO=1 python3
# -c 1`): any number of leading `VAR=val` assignments, then one of
# env/command/exec/nice/nohup/time/timeout/stdbuf with its own flags/args.
# Best-effort, not a shell parser: an unrecognized or malformed wrapper
# invocation is left as-is, at its literal first word.
strip_command_wrappers() {
  local progressed=1 t drop_extra
  while [ "$progressed" -eq 1 ] && [ "${#tokens[@]}" -gt 0 ]; do
    progressed=0
    if [[ "${tokens[0]}" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
      tokens=("${tokens[@]:1}")
      tokens_masked=("${tokens_masked[@]:1}")
      progressed=1
      continue
    fi
    case "${tokens[0]##*/}" in
      env)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        # env's own flags and any number of VAR=val assignments before the
        # real command; -u NAME takes a following bare arg (best-effort:
        # drop one extra token for it).
        while [ "${#tokens[@]}" -gt 0 ]; do
          t="${tokens[0]}"
          if [[ "$t" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
            tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
          elif [ "${t:0:1}" = "-" ]; then
            drop_extra=0
            [ "$t" = "-u" ] && drop_extra=1
            tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
            if [ "$drop_extra" -eq 1 ] && [ "${#tokens[@]}" -gt 0 ]; then
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
            fi
          else
            break
          fi
        done
        progressed=1
        ;;
      command)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        while [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; do
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        done
        progressed=1
        ;;
      exec|nohup)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        progressed=1
        ;;
      nice)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ]; then
          case "${tokens[0]}" in
            -n)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              if [ "${#tokens[@]}" -gt 0 ]; then
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              fi
              ;;
            -[0-9]*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
          esac
        fi
        progressed=1
        ;;
      time)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]}" = "-p" ]; then
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        fi
        progressed=1
        ;;
      timeout)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        while [ "${#tokens[@]}" -gt 0 ]; do
          t="${tokens[0]}"
          case "$t" in
            -s|-k)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              if [ "${#tokens[@]}" -gt 0 ]; then
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              fi
              ;;
            --signal=*|--kill-after=*|--preserve-status|--foreground|-v|--verbose)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            *) break ;;
          esac
        done
        # the required DURATION positional
        if [ "${#tokens[@]}" -gt 0 ]; then
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        fi
        progressed=1
        ;;
      stdbuf)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        while [ "${#tokens[@]}" -gt 0 ]; do
          t="${tokens[0]}"
          case "$t" in
            -i|-o|-e)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              if [ "${#tokens[@]}" -gt 0 ]; then
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              fi
              ;;
            -i*|-o*|-e*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            *) break ;;
          esac
        done
        progressed=1
        ;;
    esac
  done
}

# --- read stdin once, tolerate absent/malformed input by allowing ---
input="$(cat 2>/dev/null)"
[ -z "$input" ] && exit 0

command -v jq >/dev/null 2>&1 || exit 0

# --- scope: only run for executor-fast/executor-smart/executor-lead/executor-judge
#     (or plugin-namespaced forms). deny_writes=1 layers the file-write denial
#     on top of the shared irreversible-command checks for lead and judge only. ---
agent_type="$(printf '%s' "$input" | jq -r '.agent_type // empty' 2>/dev/null)"
deny_writes=0
is_judge=0
case "$agent_type" in
  executor-fast|*:executor-fast) : ;;
  executor-smart|*:executor-smart) : ;;
  executor-lead|*:executor-lead) deny_writes=1 ;;
  executor-judge|*:executor-judge) deny_writes=1; is_judge=1 ;;
  *) exit 0 ;;
esac

cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -z "$cmd" ] && exit 0

# .cwd resolves a relative path token before the recursive-delete check's
# normalize_path call, below — see the chained-cd known limit in the header.
cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"

# --- split into pipeline/chain segments so matches after ;, &&, ||, | are caught ---
segments_raw="$(split_command "$cmd")"

while IFS= read -r segment; do
  # trim leading/trailing whitespace
  segment="${segment#"${segment%%[![:space:]]*}"}"
  segment="${segment%"${segment##*[![:space:]]}"}"
  [ -z "$segment" ] && continue

  # tokenize on whitespace, quote-aware (quote_walk word mode) — a quoted
  # argument containing spaces (an awk/jq program, a grep pattern) stays ONE
  # token instead of splitting apart and exposing a bare '>' that was never
  # a real shell metacharacter. tokens_masked is the parallel masked form
  # used by redirect-style checks (see quote_walk above).
  tokens=()
  tokens_masked=()
  while IFS=$'\x1f' read -r tok_lit tok_masked; do
    tokens+=("$tok_lit")
    tokens_masked+=("$tok_masked")
  done < <(quote_walk word "$segment")
  [ "${#tokens[@]}" -eq 0 ] && continue

  # --- fail-closed: unquoted leading '(' or '{' cannot be confidently
  # identified as a command (subshell, ((arithmetic)), or brace group) ---
  # Tested against tokens_masked[0] (the masked companion, not the raw
  # tokens[0]) so this is an UNQUOTED-only check: a quoted leading '(' or
  # '{' is masked to 'Q' and does not match. Deliberately blunt — this also
  # denies a harmless bare ((x++)) or (cd x && ls); the guard does not
  # attempt to parse inside a group, only to never silently skip past one.
  case "${tokens_masked[0]}" in
    '('*)
      deny "Cannot confidently identify the leading command — an unquoted '(' starts a subshell, arithmetic command, or command substitution used as the entire leading word, none of which this guard parses into. Rewrite without the wrapper."
      ;;
    '{')
      deny "Cannot confidently identify the leading command — an unquoted '{' brace group is not parsed into by this guard. Rewrite without the wrapper."
      ;;
  esac

  cmd0="${tokens[0]##*/}"

  # --- 1. recursive delete (rm -r / -R / -rf / -fr / --recursive[, --force]) ---
  # -f is NOT required to deny: `rm -r` alone deletes every matched file with
  # no confirmation in a non-interactive shell, so it is treated the same as
  # `rm -rf` here.
  if [ "$cmd0" = "rm" ]; then
    flag_r=0
    paths=()
    for tok in "${tokens[@]:1}"; do
      case "$tok" in
        --recursive*) flag_r=1 ;;
        --force*) : ;;
        --) : ;;
        -*)
          case "$tok" in *r*|*R*) flag_r=1 ;; esac
          ;;
        *) paths+=("$tok") ;;
      esac
    done
    if [ "$flag_r" -eq 1 ]; then
      all_temp=1
      if [ "${#paths[@]}" -eq 0 ]; then
        all_temp=0
      else
        for p in "${paths[@]}"; do
          # Decision 7's fail-closed contract: normalize_path's non-zero
          # return (metacharacter, nonexistent component, cycle/hop-budget,
          # readlink failure) is treated as NOT-temporary directly — never
          # call is_temp_path on a partial or absent result. A broken
          # `source` above (path-guard-lib.sh missing/unreadable/syntax
          # error) leaves normalize_path undefined, which fails the same
          # way here (bash "command not found", exit 127, falsy) — denies
          # closed, per the header note above.
          resolved_p="$(normalize_path "$p" "$cwd" parent)" || { all_temp=0; continue; }
          is_temp_path "$resolved_p" || all_temp=0
        done
      fi
      if [ "$all_temp" -eq 0 ]; then
        deny "Recursive delete (rm -r/-R, with or without -f) targets a path outside a temp location — this can permanently destroy files with no undo."
      fi
    fi
  fi

  # --- find -delete (permanently removes every matched file) ---
  if [ "$cmd0" = "find" ]; then
    for tok in "${tokens[@]:1}"; do
      if [ "$tok" = "-delete" ]; then
        deny "find with -delete permanently removes every matched file — irreversible."
      fi
    done
  fi

  # --- git subcommands (shared irreversible-command rules — fast/smart/lead/judge) ---
  if [ "$cmd0" = "git" ] && [ "${#tokens[@]}" -ge 2 ]; then
    sub="${tokens[1]}"
    case "$sub" in
      push)
        for tok in "${tokens[@]:2}"; do
          case "$tok" in
            -f|--force|--force-with-lease*)
              deny "git push with --force/--force-with-lease/-f can overwrite and permanently discard remote commit history — irreversible."
              ;;
            +*)
              deny "git push with a leading '+' refspec (e.g. +main) force-pushes and can overwrite remote commit history — irreversible."
              ;;
          esac
        done
        ;;
      clean)
        cflag_f=0
        cflag_dx=0
        for tok in "${tokens[@]:2}"; do
          case "$tok" in
            --force) cflag_f=1 ;;
            --*) : ;;
            -*)
              case "$tok" in *f*) cflag_f=1 ;; esac
              case "$tok" in *d*|*x*|*X*) cflag_dx=1 ;; esac
              ;;
          esac
        done
        if [ "$cflag_f" -eq 1 ] && [ "$cflag_dx" -eq 1 ]; then
          deny "git clean with -f combined with -d/-x permanently deletes untracked files and directories — irreversible."
        fi
        ;;
      reset)
        for tok in "${tokens[@]:2}"; do
          if [ "$tok" = "--hard" ]; then
            deny "git reset --hard permanently discards uncommitted changes and resets the working tree — irreversible."
          fi
        done
        ;;
      checkout)
        rest="${tokens[*]:2}"
        if [ "$rest" = "-- ." ] || [ "$rest" = "." ]; then
          deny "git checkout of '.' mass-discards all uncommitted working-tree changes — irreversible."
        fi
        ;;
      restore)
        rest="${tokens[*]:2}"
        case "$rest" in
          "."|"--staged --worktree ."|"--worktree --staged .")
            deny "git restore of '.' mass-discards uncommitted working-tree/staged changes — irreversible."
            ;;
        esac
        ;;
      branch)
        bflag_delete=0
        bflag_force=0
        for tok in "${tokens[@]:2}"; do
          case "$tok" in
            -D) deny "git branch -D force-deletes a branch and can drop unmerged commits — irreversible." ;;
            --delete) bflag_delete=1 ;;
            --force) bflag_force=1 ;;
            --) : ;;
            -*)
              case "$tok" in *d*|*D*) bflag_delete=1 ;; esac
              case "$tok" in *f*|*F*) bflag_force=1 ;; esac
              ;;
          esac
        done
        if [ "$bflag_delete" -eq 1 ] && [ "$bflag_force" -eq 1 ]; then
          deny "git branch --delete/-d combined with --force/-f force-deletes a branch and can drop unmerged commits — irreversible."
        fi
        ;;
      merge)
        merge_abort_continue=0
        for tok in "${tokens[@]:2}"; do
          case "$tok" in
            --abort|--continue) merge_abort_continue=1 ;;
          esac
        done
        if [ "$merge_abort_continue" -eq 0 ]; then
          deny "git merge (including --no-ff/--squash/-m forms) lands one branch's history into another — landing a merge is the user's hand alone, not this executor's, and it is a one-way door once pushed. Use --abort/--continue only to recover from a merge already in progress."
        fi
        ;;
      worktree)
        wt_sub="${tokens[2]:-}"
        case "$wt_sub" in
          remove)
            deny "git worktree remove deletes a worktree and can discard uncommitted work inside it — irreversible."
            ;;
          prune)
            deny "git worktree prune permanently deletes administrative data for worktrees git decides are stale — irreversible."
            ;;
        esac
        ;;
    esac
  fi

  # --- package publish ---
  if [ "${tokens[1]:-}" = "publish" ]; then
    case "$cmd0" in
      npm|yarn|pnpm)
        deny "$cmd0 publish pushes a package version live to the registry — cannot be cleanly unpublished."
        ;;
    esac
  fi

  # --- file-write denial (executor-lead and executor-judge only) ---
  if [ "$deny_writes" -eq 1 ]; then
    # Wrapper/prefix stripping runs FIRST, mutating tokens/tokens_masked in
    # place, so every check below (this block only — the shared
    # irreversible-command checks above stay on the original tokens/cmd0)
    # classifies the command a wrapper would otherwise launder past it.
    # cmd0 is recomputed from the now-possibly-shorter tokens[0]; an empty
    # tokens (e.g. the whole segment was just `FOO=bar`, or `env` with
    # nothing after it) sets cmd0 to empty, matching no case below.
    strip_command_wrappers
    if [ "${#tokens[@]}" -gt 0 ]; then
      cmd0="${tokens[0]##*/}"
    else
      cmd0=""
    fi

    # any rm (not just recursive-force, already covered above) deletes a file
    if [ "$cmd0" = "rm" ]; then
      deny "rm deletes a file — this executor may not write, create, move, or delete files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
    fi

    case "$cmd0" in
      sh|bash|zsh|ksh|dash|ash)
        deny "$cmd0 is a shell invocation — this guard does not parse a shell's own -c argument or script as a nested command line, so it cannot classify what runs inside it; running a shell here would launder any write-form or interpreter invocation past every check in this file. This executor may not invoke a shell via Bash."
        ;;
      cp|mv|install|touch|mkdir|truncate|tee|patch)
        deny "$cmd0 creates, overwrites, or moves a file — this executor may not write files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
        ;;
      python|python2|python3|node|nodejs|deno|bun)
        # Maintainer decision 2026-09-26 (option A), tightened 2026-09-27 to
        # a strict ALLOWLIST (see the header comment for the full shape):
        # executor-judge must be able to re-run gates (agents/executor-
        # judge.md:104, Core Law 3), but only through one of a small set of
        # positively-enumerated forms — everything else denies, including
        # every combined-short-flag or wrapped-flag form a blocklist would
        # have had to enumerate one at a time. Lead takes the else branch
        # below, unchanged blanket denial regardless of args.
        if [ "$is_judge" -eq 1 ]; then
          ok=0
          n=${#tokens[@]}
          case "$cmd0" in
            python|python2|python3)
              if [ "$n" -ge 2 ]; then
                t1="${tokens[1]}"
                case "$t1" in
                  -m)
                    if [ "$n" -ge 3 ]; then
                      case "${tokens[2]}" in
                        pytest|unittest)
                          ok=1
                          idx=3
                          while [ "$idx" -lt "$n" ]; do
                            tok="${tokens[$idx]}"
                            case "$tok" in
                              -q|-qq|-v|-vv|-x|-s|--no-header|-l|--lf|--ff) : ;;
                              --tb=short|--tb=long|--tb=line|--tb=no|--tb=native) : ;;
                              -r?*) : ;; # -r<chars> glued, e.g. -rA, -rfE
                              -k=*) : ;;
                              -k)
                                idx=$((idx + 1))
                                [ "$idx" -lt "$n" ] || { ok=0; break; }
                                ;;
                              -m)
                                # a pytest marker expression — only ever
                                # reached here, after `-m pytest`/`-m
                                # unittest` already consumed python's own
                                # -m, so never confused with it.
                                idx=$((idx + 1))
                                if [ "$idx" -ge "$n" ] || [[ "${tokens[$idx]}" == -* ]]; then
                                  ok=0; break
                                fi
                                ;;
                              -*)
                                ok=0; break
                                ;;
                              *)
                                # existing path, dir, or path::nodeid inside
                                # cwd — the nodeid suffix past `::` is never
                                # inspected, only the path before it.
                                _judge_resolve_in_cwd "${tok%%::*}" "$cwd" >/dev/null || { ok=0; break; }
                                ;;
                            esac
                            idx=$((idx + 1))
                          done
                          ;;
                        # `-m doctest`: doctest can execute arbitrary code
                        # in any .py docstring it's pointed at; no bound was
                        # found safe enough to allow it — denied outright.
                        # Every other module (pip, json.tool, http.server,
                        # ...) denies the same way, by not matching here.
                      esac
                    fi
                    ;;
                  -*) : ;; # any other leading flag rules out both forms
                  *)
                    case "$t1" in
                      *.py)
                        case "${tokens_masked[1]}" in
                          '<('*) : ;;
                          *)
                            resolved="$(_judge_resolve_in_cwd "$t1" "$cwd")" && [ -f "$resolved" ] && ok=1
                            ;;
                        esac
                        ;;
                    esac
                    ;;
                esac
              fi
              ;;
            node|nodejs)
              if [ "$n" -ge 2 ]; then
                t1="${tokens[1]}"
                case "$t1" in
                  -*) : ;;
                  *)
                    case "$t1" in
                      *.js|*.mjs|*.cjs)
                        case "${tokens_masked[1]}" in
                          '<('*) : ;;
                          *)
                            resolved="$(_judge_resolve_in_cwd "$t1" "$cwd")" && [ -f "$resolved" ] && ok=1
                            ;;
                        esac
                        ;;
                    esac
                    ;;
                esac
              fi
              ;;
            bun)
              if [ "$n" -ge 2 ]; then
                t1="${tokens[1]}"
                case "$t1" in
                  run)
                    if [ "$n" -ge 3 ]; then
                      t2="${tokens[2]}"
                      case "$t2" in
                        -*) : ;;
                        *)
                          case "$t2" in
                            *.js|*.ts|*.mjs|*.cjs|*.tsx)
                              case "${tokens_masked[2]}" in
                                '<('*) : ;;
                                *)
                                  resolved="$(_judge_resolve_in_cwd "$t2" "$cwd")" && [ -f "$resolved" ] && ok=1
                                  ;;
                              esac
                              ;;
                          esac
                          ;;
                      esac
                    fi
                    ;;
                  test)
                    ok=1
                    idx=2
                    while [ "$idx" -lt "$n" ]; do
                      tok="${tokens[$idx]}"
                      case "$tok" in
                        -*) ok=0; break ;;
                      esac
                      _judge_resolve_in_cwd "$tok" "$cwd" >/dev/null || { ok=0; break; }
                      idx=$((idx + 1))
                    done
                    ;;
                  -*) : ;;
                  *)
                    # a bare package.json script name (e.g. `bun build`) has
                    # no .js/.ts/... extension and is never on disk at that
                    # name, so it fails the extension/existence check below
                    # the same way a truly missing script would.
                    case "$t1" in
                      *.js|*.ts|*.mjs|*.cjs|*.tsx)
                        case "${tokens_masked[1]}" in
                          '<('*) : ;;
                          *)
                            resolved="$(_judge_resolve_in_cwd "$t1" "$cwd")" && [ -f "$resolved" ] && ok=1
                            ;;
                        esac
                        ;;
                    esac
                    ;;
                esac
              fi
              ;;
            deno)
              if [ "$n" -ge 3 ] && [ "${tokens[1]}" = "run" ]; then
                t2="${tokens[2]}"
                case "$t2" in
                  -*) : ;; # any permission or other flag before the script denies
                  *)
                    case "$t2" in
                      *.ts|*.js)
                        case "${tokens_masked[2]}" in
                          '<('*) : ;;
                          *)
                            resolved="$(_judge_resolve_in_cwd "$t2" "$cwd")" && [ -f "$resolved" ] && ok=1
                            ;;
                        esac
                        ;;
                    esac
                    ;;
                esac
              elif [ "$n" -ge 2 ] && [ "${tokens[1]}" = "test" ]; then
                ok=1
                idx=2
                while [ "$idx" -lt "$n" ]; do
                  tok="${tokens[$idx]}"
                  case "$tok" in
                    -*) ok=0; break ;;
                  esac
                  _judge_resolve_in_cwd "$tok" "$cwd" >/dev/null || { ok=0; break; }
                  idx=$((idx + 1))
                done
              fi
              # every other deno subcommand (fmt, eval, add, install, ...)
              # denies by never setting ok=1 above.
              ;;
          esac
          if [ "$ok" -eq 1 ]; then
            # a heredoc/here-string anywhere feeds code/data the same class
            # of way as -c/-e/stdin, regardless of which allowed form
            # matched above — checked on masked tokens so a literal '<<'
            # inside a quoted argument (never a real redirect) can't trip
            # this.
            for mtok in "${tokens_masked[@]:1}"; do
              case "$mtok" in
                *'<<'*) ok=0 ;;
              esac
            done
          fi
          if [ "$ok" -eq 0 ]; then
            deny "$cmd0 with this form is not permitted via Bash for this executor — only \`$cmd0 <script>\` (an existing script file inside cwd, right extension, no flag before it), \`python3 -m pytest|unittest\` with existing paths inside cwd and a narrow allowlisted flag set, \`bun run <script>\`/\`bun test <paths>\`, or \`deno run <script>\`/\`deno test <paths>\` is permitted — re-run an existing script or test this way instead."
          fi
          # else: allow, e.g. `python3 scripts/x.py`, `python3 -m pytest
          # tests/harness -q`, `node scripts/x.js`, `bun run x.ts`, `bun
          # test tests/`, `deno run x.ts`, `deno test tests/`.
        else
          deny "$cmd0 is an inline interpreter or scripting tool this executor may not run via Bash — Bash is read-only here (grep/sed -n/git log/git diff/jq/wc/find/cat/head/tail/ls/diff/shellcheck cover inspection); route scripted or destructive work through an executor that holds Write/Edit."
        fi
        ;;
      perl|ed|xargs)
        deny "$cmd0 is an inline interpreter or scripting tool this executor may not run via Bash — Bash is read-only here (grep/sed -n/git log/git diff/jq/wc/find/cat/head/tail/ls/diff/shellcheck cover inspection); route scripted or destructive work through an executor that holds Write/Edit."
        ;;
      sed)
        for tok in "${tokens[@]:1}"; do
          case "$tok" in
            -i*) deny "sed -i edits a file in place — this executor may not write files via Bash." ;;
          esac
        done
        ;;
      dd)
        for tok in "${tokens[@]:1}"; do
          case "$tok" in
            of=*) deny "dd of= writes/overwrites a file — this executor may not write files via Bash." ;;
          esac
        done
        ;;
      awk)
        for mtok in "${tokens_masked[@]:1}"; do
          if [[ "$mtok" == *'>'* ]]; then
            case "$mtok" in
              *'>='*) : ;; # best-effort: skip likely numeric-comparison operator
              *) deny "awk with an embedded '>' likely redirects output to a file — this executor may not write files via Bash." ;;
            esac
          fi
        done
        ;;
    esac

    if [ "$cmd0" = "git" ] && [ "${#tokens[@]}" -ge 2 ]; then
      sub="${tokens[1]}"
      case "$sub" in
        add|commit|apply|stash|rm|mv)
          deny "git $sub changes tracked/staged file state — this executor may not write files via Bash."
          ;;
        restore)
          deny "git restore overwrites working-tree/staged files from another version — this executor may not write files via Bash."
          ;;
        checkout)
          for tok in "${tokens[@]:2}"; do
            if [ "$tok" = "--" ]; then
              deny "git checkout -- restores file contents from another version, discarding working-tree edits — this executor may not write files via Bash."
            fi
          done
          ;;
      esac
    fi

    # bare/glued output redirection: >, >>, N>, N>>, &>, &>> — matched
    # anywhere in the (masked) token, not just at its start, so a redirect
    # glued straight onto the preceding argument (e.g. `pwned>out.txt`, no
    # space) is caught the same as a standalone `>out.txt` token. Tested
    # against tokens_masked, not tokens: a '>' that only exists inside
    # quotes (`grep '>' f`, `awk '$1 > 5'`, `git log --grep='fix > bug'`)
    # is masked to 'Q' and can never trip this check — only a '>' the shell
    # itself would treat as a redirect operator survives into the masked
    # form.
    # (fd duplication/close forms like 2>&1, &>&2, 2>&- are not file writes;
    # a target of /dev/null, decision 22, discards output rather than
    # persisting it to a file — exempted the same way, alongside them. The
    # target is read from the RAW token, not the masked one, and re-derived
    # from the next token when a space separates the operator from its
    # target (`2> /dev/null`), so both a glued and a spaced /dev/null are
    # recognized; one layer of surrounding quotes is stripped before the
    # comparison so `'/dev/null'` and `"/dev/null"` match too. Widened no
    # further than /dev/null.)
    redirect_i=0
    for mtok in "${tokens_masked[@]}"; do
      if [[ "$mtok" =~ [0-9]*(\>\>?|\&\>\>?)([^[:space:]]*)$ ]]; then
        rest="${BASH_REMATCH[2]}"
        raw_tok="${tokens[$redirect_i]}"
        target="${raw_tok:$((${#raw_tok} - ${#rest}))}"
        if [ -z "$target" ] && [ $((redirect_i + 1)) -lt "${#tokens[@]}" ]; then
          target="${tokens[$((redirect_i + 1))]}"
        fi
        if [[ "$target" == \"*\" && "$target" == *\" ]] || [[ "$target" == \'*\' && "$target" == *\' ]]; then
          target="${target:1:$((${#target} - 2))}"
        fi
        if [[ "$rest" =~ ^\&[0-9]+$ ]] || [ "$rest" = "&-" ] || [ "$target" = "/dev/null" ]; then
          : # fd duplication/close, or /dev/null (decision 22) — not a file write
        else
          deny "output redirection (>, >>, &>) writes to a file — this executor may not write files via Bash."
        fi
      fi
      redirect_i=$((redirect_i + 1))
    done
  fi

done <<< "$segments_raw"

exit 0
