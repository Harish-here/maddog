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
#     deno, bun, perl, ed, xargs) for lead/judge outright, regardless of
#     what they'd do — neither agent's read-only toolset needs one, so a
#     denial by binary name costs them nothing real.
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

deny() {
  local reason="$1"
  local ctx="Blocked by executor-guard.sh: this executor is not permitted to weigh irreversible actions or write files via Bash. STOP and return STATUS: blocked to your caller with this reason — do not attempt the command."
  local reason_json ctx_json
  reason_json="$(printf '%s' "$reason" | jq -Rs .)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs .)"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  exit 0
}

is_temp_path() {
  case "$1" in
    *"/tmp/"*|*"/private/tmp/"*|*"/var/folders/"*) return 0 ;;
    # scratchpad matched as a path COMPONENT, not a substring: "/scratchpad",
    # "/scratchpad/...", a bare "scratchpad", or "scratchpad/..." — never e.g.
    # "/Users/me/my-scratchpad-notes", which merely contains the substring.
    *"/scratchpad"|*"/scratchpad/"*|"scratchpad"|"scratchpad/"*) return 0 ;;
    *) return 1 ;;
  esac
}

# --- quote-aware walk -------------------------------------------------
# One shared character-by-character quote-tracking walk (mode-selected),
# reused everywhere in this file that needs to know whether a character
# sits inside single/double quotes — a single implementation, not one per
# call site that can drift out of sync.
#   mode="chain": splits a full command into pipeline/chain segments on
#     unquoted &&, ||, ;, and | — e.g. `grep -E "a|rm -rf|b"` stays ONE
#     segment instead of re-parsing as a pipeline containing a bogus
#     `rm -rf` stage. Prints one segment (literal) per line.
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
  local buf="" mbuf="" c prev="" in_single=0 in_double=0
  local i=0 len=${#cmd}
  local US=$'\x1f'
  while [ "$i" -lt "$len" ]; do
    c="${cmd:i:1}"
    if [ "$in_single" -eq 1 ]; then
      buf+="$c"
      mbuf+="Q"
      [ "$c" = "'" ] && in_single=0
      prev="$c"
      i=$((i + 1))
      continue
    fi
    if [ "$in_double" -eq 1 ]; then
      buf+="$c"
      mbuf+="Q"
      if [ "$c" = '"' ] && [ "$prev" != "\\" ]; then
        in_double=0
      fi
      prev="$c"
      i=$((i + 1))
      continue
    fi
    if [ "$mode" = "word" ]; then
      case "$c" in
        ' '|$'\t')
          [ -n "$buf" ] && out+=("${buf}${US}${mbuf}")
          buf=""
          mbuf=""
          prev="$c"
          i=$((i + 1))
          continue
          ;;
      esac
    fi
    case "$c" in
      "'")
        in_single=1
        buf+="$c"
        mbuf+="Q"
        ;;
      '"')
        in_double=1
        buf+="$c"
        mbuf+="Q"
        ;;
      '&')
        if [ "$mode" = "chain" ] && [ "${cmd:i:2}" = "&&" ]; then
          out+=("$buf")
          buf=""
          i=$((i + 2))
          prev="$c"
          continue
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
            prev="$c"
            continue
          fi
          out+=("$buf")
          buf=""
          i=$((i + 1))
          prev="$c"
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
          prev="$c"
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
    prev="$c"
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
          is_temp_path "$p" || all_temp=0
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
    # any rm (not just recursive-force, already covered above) deletes a file
    if [ "$cmd0" = "rm" ]; then
      deny "rm deletes a file — this executor may not write, create, move, or delete files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
    fi

    case "$cmd0" in
      cp|mv|install|touch|mkdir|truncate|tee|patch)
        deny "$cmd0 creates, overwrites, or moves a file — this executor may not write files via Bash (Bash is read-only here); route the change through an executor that holds Write/Edit."
        ;;
      python|python2|python3|node|nodejs|deno|bun|perl|ed|xargs)
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
    # (fd duplication/close forms like 2>&1, &>&2, 2>&- are not file writes)
    for mtok in "${tokens_masked[@]}"; do
      if [[ "$mtok" =~ [0-9]*(\>\>?|\&\>\>?)([^[:space:]]*)$ ]]; then
        rest="${BASH_REMATCH[2]}"
        if [[ "$rest" =~ ^\&[0-9]+$ ]] || [ "$rest" = "&-" ]; then
          : # fd duplication/close — not a file write
        else
          deny "output redirection (>, >>, &>) writes to a file — this executor may not write files via Bash."
        fi
      fi
    done
  fi

done <<< "$segments_raw"

exit 0
