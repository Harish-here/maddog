# command-check.sh - run every check over a command line, including the command lines inside it.
# Sourced, never run. Needs deny() and the deny_writes flag from the calling hook, parse.sh,
# rules-irreversible.sh, rules-readonly.sh, messages.sh. Bash 3.2.

# Command substitutions nest (`$(a $(b $(c)))`); past this depth lead and judge are denied and
# the rest stop looking, rather than recursing without bound.
SUBST_MAX_DEPTH=8

# check_segment <segment>
# The checks for one pipeline/chain segment, in order: the reserved words that open it and the
# prefixes that run another command (assignments, env, rtk) are peeled, so every check below
# reads the command that runs; then the shape check, the irreversible-command checks (all
# agents) and the file-write checks (lead and judge, deny_writes=1).
check_segment() {
  local segment="$1"
  segment="${segment#"${segment%%[![:space:]]*}"}"
  segment="${segment%"${segment##*[![:space:]]}"}"
  [ -z "$segment" ] && return 0

  tokenize_segment "$segment"
  [ "${#tokens[@]}" -eq 0 ] && return 0

  strip_leading_keywords
  [ "${#tokens[@]}" -eq 0 ] && return 0
  strip_leading_prefixes
  [ "${#tokens[@]}" -eq 0 ] && return 0

  # fast and smart keep the old reading of a `(` that follows a reserved word (`then (cd x)`)
  if [ "$deny_writes" -eq 1 ] || [ "$KW_STRIPPED" -eq 0 ]; then
    check_segment_shape
  fi
  check_irreversible
  if [ "$deny_writes" -eq 1 ]; then
    check_readonly_writes
  fi
  return 0
}

# check_command_text <text> [depth] [mode]
# Checks a command line: every substitution inside it is cut out first (extract_substitutions)
# and the rest is split into segments and checked; then each cut-out command is checked the same
# way, nested ones too. mode "arith" is the inside of `$((...))`: arithmetic is not a command,
# so only the substitutions nested in it are checked. An opener the parser cannot close denies
# lead and judge; the others go on without looking inside it.
check_command_text() {
  local text="$1" depth="${2:-0}" mode="${3:-cmd}" top segments_raw segment item
  local -a inner_list=()
  extract_substitutions "$text"
  top="$SUBST_TOP"
  if [ "${#SUBST_LIST[@]}" -gt 0 ]; then
    inner_list=("${SUBST_LIST[@]}")
  fi
  if [ "$SUBST_UNBALANCED" -eq 1 ] && [ "$deny_writes" -eq 1 ]; then
    deny "$MSG_SUBST_UNBALANCED" shape
  fi

  if [ "$mode" = "cmd" ]; then
    segments_raw="$(split_command "$top")"
    while IFS= read -r segment; do
      check_segment "$segment"
    done <<< "$segments_raw"
  fi

  if [ "${#inner_list[@]}" -gt 0 ]; then
    if [ "$depth" -ge "$SUBST_MAX_DEPTH" ]; then
      if [ "$deny_writes" -eq 1 ]; then
        deny "$MSG_SUBST_TOO_DEEP" shape
      fi
      return 0
    fi
    for item in "${inner_list[@]}"; do
      case "$item" in
        A:*) check_command_text "${item#A:}" $((depth + 1)) arith ;;
        *) check_command_text "${item#C:}" $((depth + 1)) cmd ;;
      esac
    done
  fi
  return 0
}
