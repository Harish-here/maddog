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
#     deno, bun, perl, ed, xargs) for BOTH lead and judge outright, regardless
#     of args or form — neither agent's read-only toolset needs any of them,
#     so a denial by binary name costs neither agent anything real.
#
#     History: executor-judge briefly carried a narrower carve-out
#     (maintainer decision 2026-09-26, option A; tightened to a strict
#     ALLOWLIST 2026-09-27) so it could re-run gates itself
#     (agents/executor-judge.md:104, Core Law 3) through a small set of
#     positively-enumerated python/node/bun/deno forms. A second independent
#     release review (round 2, on commit 1e3ecec) found the allowlist still
#     leaking on two axes — `VAR=val` prefixes were stripped and discarded
#     before classification (so e.g. `PYTEST_ADDOPTS=--junitxml=README.md
#     python3 -m pytest tests -q` reached the allowlist looking like a bare
#     `python3 -m pytest tests -q`), and several wrapper forms (`env -S`,
#     `env -P`, `nice -n5`, `nice --adjustment=5`, `exec -a`) were only
#     partially parsed by the stripper and then fell through unclassified.
#     Maintainer decision (option B, 2026-09-27): remove the allowlist
#     rather than keep patching it. Judge now denies every interpreter in
#     every form, exactly like lead — including python/python2/python3/
#     node/nodejs/deno/bun/perl/ed/xargs. Known, accepted limitation, not
#     solved here: judge can no longer re-run a gate itself via Bash; that
#     capability is deferred to a future dedicated gate-runner script (not
#     yet written) rather than reopening an inline-interpreter allowlist.
#
#     Wrapper/prefix stripping (both lead and judge): the classification
#     above (and the write-form denials just below it) runs against the
#     command with leading `VAR=val` assignments and any of `env`,
#     `command`, `exec`, `nice`, `nohup`, `time`, `timeout <duration>`, and
#     `stdbuf` peeled off first — `env python3 -c 1`, `timeout 5 python3 -c
#     1`, `FOO=1 python3 -c 1`, etc. are classified as the `python3 -c 1`
#     they really are, not as `env`/`timeout`/an assignment falling through
#     unclassified. A shell binary (`sh`, `bash`, `zsh`, `ksh`, `dash`,
#     `ash`) found as the real command after that stripping denies outright
#     for lead and judge, with or without `-c` — this guard does not parse a
#     shell's own `-c` argument as a nested command line, so the only safe
#     answer is to deny the shell invocation itself; `sh -c "echo x > f"`
#     and similar never reach (and could not be reliably caught by) the
#     write-form checks below.
#
#     Not a shell parser, but not silently permissive either (release
#     review round 2, F2): each wrapper only fully understands a specific,
#     enumerated set of its own flags (`nice`: `-n N` or a glued `-N` only;
#     `env`: `VAR=val` assignments only, no flag at all; `exec`/`nohup`: no
#     flag at all; `time`: `-p` only; `timeout`/`stdbuf`: a fixed enumerated
#     flag set). A flag or argument form outside what a given wrapper's
#     branch enumerates — `env -S '...'`, `env -P /usr/bin ...`, `nice -n5 ...`,
#     `nice --adjustment=5 ...`, `exec -a foo ...`, an unrecognized `time`
#     flag, etc. — DENIES immediately, inside the stripper, instead of
#     falling through with that flag misread as the real command (which is
#     how `env -S 'sh -c "echo x > f"'`, `nice --adjustment=5 python3 -c 1`,
#     and `exec -a foo python3 -c 1` previously reached ALLOW: the stripper
#     dropped some tokens, stopped, and left an unrecognized leftover flag
#     as `tokens[0]`, matching no denial case). When unsure, deny.
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

# --- wrapper/prefix stripping (lead/judge file-write classification) ---
# Mutates the caller's GLOBAL `tokens`/`tokens_masked` arrays in place
# (Bash 3.2: no nameref) so a wrapper cannot launder a write-form or
# interpreter invocation past the classification that follows. Peels, in a
# loop (wrappers can chain, e.g. `nice nohup timeout 5 env FOO=1 python3
# -c 1`): any number of leading `VAR=val` assignments, then one of
# env/command/exec/nice/nohup/time/timeout/stdbuf with its own flags/args.
# Not a shell parser: each wrapper branch only fully understands a specific,
# enumerated flag set for that wrapper (see the header comment); a flag or
# argument form outside that set calls deny() directly and exits the whole
# script from inside this function, rather than leaving an unrecognized
# leftover token to fall through and be misread as the real command.
strip_command_wrappers() {
  local progressed=1 t
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
        # env's only fully-understood leading form is VAR=val assignments.
        # ANY flag (env's flag surface is wide and easy to misparse: -S
        # splits a whole new command line out of a string, -P/-i/-u/-C/-0
        # change PATH/environment/argv0/cwd in ways this guard does not
        # re-derive) denies immediately rather than risk laundering
        # whatever env ends up running past this classification.
        while [ "${#tokens[@]}" -gt 0 ]; do
          t="${tokens[0]}"
          if [[ "$t" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
            tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
          elif [ "${t:0:1}" = "-" ]; then
            deny "env with a flag ($t) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command env ends up running."
          else
            break
          fi
        done
        progressed=1
        ;;
      command)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        # command's only flags (-p, -v, -V) take no argument, so dropping
        # any leading '-' token is a complete understanding, not a guess.
        while [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; do
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        done
        progressed=1
        ;;
      exec)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; then
          deny "exec with a flag (${tokens[0]}) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command exec ends up running."
        fi
        progressed=1
        ;;
      nohup)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; then
          deny "nohup with a flag (${tokens[0]}) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command nohup ends up running."
        fi
        progressed=1
        ;;
      nice)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        while [ "${#tokens[@]}" -gt 0 ]; do
          t="${tokens[0]}"
          case "$t" in
            -n)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              if [ "${#tokens[@]}" -gt 0 ]; then
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              else
                deny "nice -n is missing its adjustment argument — this guard's wrapper stripper cannot classify what runs next."
              fi
              ;;
            -[0-9]*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "nice with a flag ($t) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command nice ends up running."
              ;;
            *) break ;;
          esac
        done
        progressed=1
        ;;
      time)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]}" = "-p" ]; then
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        elif [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; then
          deny "time with a flag (${tokens[0]}) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command time ends up running."
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
              else
                deny "timeout $t is missing its argument — this guard's wrapper stripper cannot classify what runs next."
              fi
              ;;
            --signal=*|--kill-after=*|--preserve-status|--foreground|-v|--verbose)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "timeout with a flag ($t) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command timeout ends up running."
              ;;
            *) break ;;
          esac
        done
        # the required DURATION positional
        if [ "${#tokens[@]}" -gt 0 ]; then
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        else
          deny "timeout is missing its DURATION argument — this guard's wrapper stripper cannot classify what runs next."
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
              else
                deny "stdbuf $t is missing its argument — this guard's wrapper stripper cannot classify what runs next."
              fi
              ;;
            -i*|-o*|-e*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "stdbuf with a flag ($t) is not fully understood by this guard's wrapper stripper — denying rather than risk misclassifying the command stdbuf ends up running."
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
case "$agent_type" in
  executor-fast|*:executor-fast) : ;;
  executor-smart|*:executor-smart) : ;;
  executor-lead|*:executor-lead) deny_writes=1 ;;
  executor-judge|*:executor-judge) deny_writes=1 ;;
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
      python|python2|python3|node|nodejs|deno|bun|perl|ed|xargs)
        # Option B (maintainer decision, 2026-09-27, release review round 2
        # on commit 1e3ecec): both lead and judge blanket-deny every
        # interpreter/scripting tool outright, regardless of args or form —
        # see the header comment for why the judge allowlist this replaced
        # was removed rather than patched further.
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
