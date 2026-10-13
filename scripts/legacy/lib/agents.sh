# agents.sh - the agent-name rules. Sourced, never run.
# A name is either bare ("executor-fast") or carries a plugin prefix ("maddog:executor-fast").
# Three call sites need slightly different prefix shapes, so the shapes live here, side by side:
#   agent_is          the CALLING agent_type: any text before the last colon.
#   agent_target_in   a dispatch TARGET: at most one "<plugin>:" prefix, no colon inside it.
#   agent_raw_re      a regex over the RAW payload when jq is unavailable.

# agent_is <agent_type> <name>...  succeeds when agent_type is any of the names, bare or prefixed.
agent_is() {
  local t="$1" n
  shift
  for n in "$@"; do
    case "$t" in
      "$n"|*:"$n") return 0 ;;
    esac
  done
  return 1
}

# agent_target_in <target> <name>...  succeeds when target is one of the names, bare or with one
# "<plugin>:" prefix. grep -E on purpose: it tests each line of the target on its own.
agent_target_in() {
  local target="$1" re
  shift
  re="^([^:]+:)?($(list_join '|' "$@"))\$"
  printf '%s' "$target" | grep -Eq "$re"
}

# agent_raw_re <name>|<name>...  prints the regex that finds `"agent_type": "<name>"` in raw JSON
# text, with optional whitespace around the colon and an optional prefix before the name.
agent_raw_re() {
  printf '%s' '"agent_type"[[:space:]]*:[[:space:]]*"([^"]*:)?('"$1"')"'
}
