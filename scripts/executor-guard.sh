#!/usr/bin/env bash
# executor-guard.sh — PreToolUse Bash guard, wired to executor-fast ONLY.
#
# Purpose: executor-fast runs at low reasoning effort with dontAsk permission
# and no judgment budget for one-way doors. This hook bounces a short list of
# irreversible/destructive Bash commands (force-delete, force-push, hard
# reset, mass discard of uncommitted work, etc.) back to a tier that can
# actually weigh them (executor-smart or the Advisor) instead of letting
# executor-fast run them unattended.
#
# IMPORTANT: Claude Code hooks FAIL OPEN. If this file is missing, not
# executable, times out, or emits malformed JSON, the tool call proceeds as
# if no hook existed. This script is therefore a GUARD, not a security
# CONTROL — it catches the common irreversible patterns, it does not
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
  local ctx="Blocked by executor-guard.sh: executor-fast is not permitted to weigh irreversible actions. If this command is genuinely needed, escalate to a tier (executor-smart or the Advisor) that can assert the exact expected state and run it deliberately."
  local reason_json ctx_json
  reason_json="$(printf '%s' "$reason" | jq -Rs .)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs .)"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  exit 0
}

is_temp_path() {
  case "$1" in
    *"/tmp/"*|*"/private/tmp/"*|*"/var/folders/"*|*scratchpad*) return 0 ;;
    *) return 1 ;;
  esac
}

# --- read stdin once, tolerate absent/malformed input by allowing ---
input="$(cat 2>/dev/null)"
[ -z "$input" ] && exit 0

command -v jq >/dev/null 2>&1 || exit 0

cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"
[ -z "$cmd" ] && exit 0

# --- split into pipeline/chain segments so matches after ;, &&, ||, | are caught ---
segments_raw="${cmd//&&/$'\n'}"
segments_raw="${segments_raw//||/$'\n'}"
segments_raw="${segments_raw//;/$'\n'}"
segments_raw="${segments_raw//|/$'\n'}"

while IFS= read -r segment; do
  # trim leading/trailing whitespace
  segment="${segment#"${segment%%[![:space:]]*}"}"
  segment="${segment%"${segment##*[![:space:]]}"}"
  [ -z "$segment" ] && continue

  # tokenize on whitespace (best-effort; no complex quote handling needed
  # for the flag/path shapes this guard looks for)
  read -ra tokens <<< "$segment"
  [ "${#tokens[@]}" -eq 0 ] && continue

  cmd0="${tokens[0]##*/}"

  # --- 1. recursive force delete (rm -rf / -fr / -r -f / --recursive --force) ---
  if [ "$cmd0" = "rm" ]; then
    flag_r=0
    flag_f=0
    paths=()
    for tok in "${tokens[@]:1}"; do
      case "$tok" in
        --recursive*) flag_r=1 ;;
        --force*) flag_f=1 ;;
        --) : ;;
        -*)
          case "$tok" in *r*|*R*) flag_r=1 ;; esac
          case "$tok" in *f*) flag_f=1 ;; esac
          ;;
        *) paths+=("$tok") ;;
      esac
    done
    if [ "$flag_r" -eq 1 ] && [ "$flag_f" -eq 1 ]; then
      all_temp=1
      if [ "${#paths[@]}" -eq 0 ]; then
        all_temp=0
      else
        for p in "${paths[@]}"; do
          is_temp_path "$p" || all_temp=0
        done
      fi
      if [ "$all_temp" -eq 0 ]; then
        deny "Recursive force delete (rm with r/R + f flags) targets a path outside a temp location — this permanently destroys files with no undo."
      fi
    fi
  fi

  # --- git subcommands ---
  if [ "$cmd0" = "git" ] && [ "${#tokens[@]}" -ge 2 ]; then
    sub="${tokens[1]}"
    case "$sub" in
      push)
        for tok in "${tokens[@]:2}"; do
          case "$tok" in
            -f|--force|--force-with-lease*)
              deny "git push with --force/--force-with-lease/-f can overwrite and permanently discard remote commit history — irreversible."
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
        for tok in "${tokens[@]:2}"; do
          if [ "$tok" = "-D" ]; then
            deny "git branch -D force-deletes a branch and can drop unmerged commits — irreversible."
          fi
        done
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

done <<< "$segments_raw"

exit 0
