# hook-io.sh - what all three hooks share: read the payload, require jq, read a field, deny,
# plus the two list helpers (in_set, list_join).
# Sourced, never run. Needs agents.sh (agent_raw_re) and messages.sh. Defines functions only.

# hook_start <hook-file-name> <guarded-agent-regex-alternation>
# Reads stdin once into $input. Empty input allows. Without jq the payload cannot be parsed:
# a payload whose raw text names a guarded agent type is denied with static JSON, every other
# caller (the main session, an unguarded agent) is allowed.
hook_start() {
  local hook="$1" guarded="$2" re
  input="$(cat 2>/dev/null)"
  [ -z "$input" ] && exit 0
  if ! command -v jq >/dev/null 2>&1; then
    re="$(agent_raw_re "$guarded")"
    if [[ "$input" =~ $re ]]; then
      emit_deny static "$MSG_JQ_MISSING_REASON" "$(msg_jq_missing_context "$hook")"
    fi
    exit 0
  fi
}

# field <jq-path>  prints one field of the payload, empty when absent or null.
field() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null; }

# emit_deny <static|escaped> <reason> <context>
# Prints the one deny JSON every hook uses; the caller exits afterwards.
#   escaped  reason and context go through jq, so any text is safe. If jq cannot encode either,
#            nothing is printed (the call is allowed): the guard never blocks on its own failure.
#   static   the text is spliced in as is and must hold no double quote and no backslash. Used
#            where jq may be missing or may be what failed.
emit_deny() {
  local enc="$1" reason="$2" ctx="$3" reason_json ctx_json
  case "$enc" in
    static)
      printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s","additionalContext":"%s"}}\n' "$reason" "$ctx"
      ;;
    *)
      reason_json="$(printf '%s' "$reason" | jq -Rs . 2>/dev/null)"
      ctx_json="$(printf '%s' "$ctx" | jq -Rs . 2>/dev/null)"
      if [ -n "$reason_json" ] && [ -n "$ctx_json" ]; then
        printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
      fi
      ;;
  esac
  return 0
}

# --- small helpers over the lists in command-lists.sh ---

# Succeeds when the first argument equals any later argument.
in_set() {
  local needle="$1" w
  shift
  for w in "$@"; do
    [ "$needle" = "$w" ] && return 0
  done
  return 1
}

# list_join <separator> <item>...  prints the items joined by the separator.
list_join() {
  local sep="$1" out="" first=1 w
  shift
  for w in "$@"; do
    if [ "$first" -eq 1 ]; then
      out="$w"
      first=0
    else
      out="${out}${sep}${w}"
    fi
  done
  printf '%s' "$out"
}
