# command-check.sh - run every check over a command line, including the command lines inside it.
# Sourced, never run. Needs deny() and the deny_writes flag from the calling hook, parse.sh,
# rules-irreversible.sh, rules-readonly.sh, messages.sh. Bash 3.2.

# What the guard does and does not promise, in one place.
#
# Threat model: for executor-lead and executor-judge (deny_writes=1) the guard is fail-closed: a
# construct it cannot read with certainty is refused (msg_unreadable in messages.sh: case,
# select, coproc, $'...' and $"..." quoting, # inside $(( )), brace expansion, a glob character
# in the command word, rtk run, a git alias set with -c, the zsh modifiers noglob, nocorrect and
# builtin, and everything the rules above already refuse). For executor-fast and executor-smart
# the irreversible-command rules catch honest mistakes, not an agent working to evade them.
#
# Known adversarial bypasses of those rules for fast and smart, left open by design:
#   - $"..." locale quoting (`$"git" push -f`, `git push $"-f"`)
#   - `rtk run -c '...'`, and partially quoted `rtk run` or `env -S` strings
#   - a # inside $(( )), which this walk reads as part of the arithmetic
#   - a `)` inside a comment, or ending a case pattern, within $(...): the substitution then
#     closes early
#   - a `(` or `{` after a reserved word or prefix, which hides the command after it
#   - brace expansion (`{git,push}` builds words that are not in the text) and globbed command
#     paths (`/usr/bin/g*t`)
#   - coproc, and git aliases defined with `git -c alias.x=!cmd`
#   - zsh-only syntax (modifiers, glob qualifiers, `=(...)`)
#   - walk time grows faster than the length of a very long command

# Command substitutions nest (`$(a $(b $(c)))`); past this depth lead and judge are denied, and
# the rest read what is left of the line flat (no more cutting out) rather than recursing without
# bound.
SUBST_MAX_DEPTH=8

# State the walk keeps across the segments of one command line (check_command_text saves and
# restores it around the lines inside substitutions):
#   CASE_OPEN    how many `case` are open, so a case pattern is only read inside one
#   CASE_EXPECT  1 when the next segment starts with a case pattern (after `in` or `;;`)
CASE_OPEN=0
CASE_EXPECT=0

# check_segment <segment> [depth]
# The checks for one pipeline/chain segment, in order: the reserved words that open it and the
# prefixes that run another command (assignments, env, rtk, the wrappers) are peeled, so every
# check below reads the command that runs; then the shape check, the irreversible-command
# checks (all agents) and the file-write checks (lead and judge, deny_writes=1). The string of
# `rtk run <string>` runs with sh -c: it is checked as a command line of its own.
check_segment() {
  local segment="$1" depth="${2:-0}"
  RTK_RUN_TEXT=""
  PEELED_OTHER=0
  segment="${segment#"${segment%%[![:space:]]*}"}"
  segment="${segment%"${segment##*[![:space:]]}"}"
  [ -z "$segment" ] && return 0

  tokenize_segment "$segment"
  [ "${#tokens[@]}" -eq 0 ] && return 0

  if [ "$deny_writes" -eq 1 ]; then
    check_unreadable_words
  fi
  strip_leading_keywords
  [ "${#tokens[@]}" -eq 0 ] && return 0
  strip_leading_prefixes
  if [ -n "$RTK_RUN_TEXT" ]; then
    check_command_text "$RTK_RUN_TEXT" $((depth + 1))
  fi
  [ "${#tokens[@]}" -eq 0 ] && return 0

  # fast and smart keep the old reading of a `(` that follows a reserved word or a prefix
  # (`then (cd x)`, `time (cd x && ls)`)
  if [ "$deny_writes" -eq 1 ] || { [ "$KW_STRIPPED" -eq 0 ] && [ "$PEELED_OTHER" -eq 0 ]; }; then
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
  local saved_open="$CASE_OPEN" saved_expect="$CASE_EXPECT" arith=0
  local -a inner_list=()
  CASE_OPEN=0
  CASE_EXPECT=0
  [ "$mode" = "arith" ] && arith=1
  extract_substitutions "$text" "$arith"
  top="$SUBST_TOP"
  if [ "${#SUBST_LIST[@]}" -gt 0 ]; then
    inner_list=("${SUBST_LIST[@]}")
  fi
  if [ "$SUBST_UNBALANCED" -eq 1 ] && [ "$deny_writes" -eq 1 ]; then
    deny "$MSG_SUBST_UNBALANCED" shape
  fi
  if [ "$deny_writes" -eq 1 ]; then
    if [ "$SUBST_UNREADABLE" -eq 1 ]; then
      deny "$(msg_unreadable "\$'...' or \$\"...\" quoting")" shape
    fi
    # a # inside $(( )) is a base prefix (16#ff) or the start of text the guard cannot place
    if [ "$mode" = "arith" ]; then
      case "$text" in
        *'#'*) deny "$(msg_unreadable "a # inside \$(( ))")" shape ;;
      esac
    fi
  fi

  if [ "$mode" = "cmd" ]; then
    segments_raw="$(split_command "$top")"
    while IFS= read -r segment; do
      segment="${segment#"${segment%%[![:space:]]*}"}"
      if [ -z "$segment" ]; then
        # an empty segment is what `;;` leaves between two commands: a pattern comes next
        [ "$CASE_OPEN" -gt 0 ] && CASE_EXPECT=1
        continue
      fi
      check_segment "$segment" "$depth"
    done <<< "$segments_raw"
  fi
  CASE_OPEN="$saved_open"
  CASE_EXPECT="$saved_expect"

  if [ "${#inner_list[@]}" -gt 0 ]; then
    if [ "$depth" -ge "$SUBST_MAX_DEPTH" ]; then
      if [ "$deny_writes" -eq 1 ]; then
        deny "$MSG_SUBST_TOO_DEEP" shape
      fi
      # fast and smart: read what is left flat, substitutions and all, as the guard did before it
      # looked inside them, so the irreversible rules still see a command nested this deep
      if [ "$mode" = "cmd" ]; then
        segments_raw="$(split_command "$text")"
        while IFS= read -r segment; do
          check_segment "$segment" "$depth"
        done <<< "$segments_raw"
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
