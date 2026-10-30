# rules-irreversible.sh - the checks every guarded agent gets: commands that cannot be undone.
# Sourced, never run. Needs deny() from the calling hook, hook-io.sh, messages.sh,
# command-lists.sh, parse.sh (unquote_tokens, find_git_subcommand) and path-guard.sh. Bash 3.2.

# These executors run at reasoning effort levels or with permission modes where they cannot
# reliably weigh one-way doors. This layer bounces a short list of irreversible commands
# (force-delete, force-push, hard reset, mass discard of uncommitted work, etc.) back to the
# caller, so the executor STOPs and returns blocked rather than attempts them.
#
# The recursive-delete check (normalize_path/is_temp_path) runs for all four agents and does
# examine the path. lead and judge's file-write denial (rules-readonly.sh) is unconditional and
# never depends on that outcome: a temp-confined `rm -r` passes this check, then hits the
# "rm deletes a file" denial regardless.
#
# Known limit (chained `cd`, not solved here): the recursive-delete check resolves a relative
# path against the PreToolUse payload's .cwd, which tracks the session's current directory and
# updates whenever a standalone `cd` Bash call runs, but NOT a `cd` chained inside the SAME
# command as the path (split_command evaluates chained segments independently, before that `cd`
# has executed). A `cd` issued as its own, prior tool call IS reflected correctly.
#
# check_irreversible
# Runs on the current segment (global tokens / tokens_masked, and cwd for relative paths) and
# calls deny() on the first irreversible command: recursive delete outside a temp location,
# find -delete, destructive git, package publish.
check_irreversible() {
  local cmd0 flag_r paths tok all_temp p resolved_p sub cflag_f cflag_dx rest bflag_delete bflag_force
  local merge_abort_continue wt_sub after ti
  # The command word, and every other word, as the shell reads it: `\git`, `"git"` and
  # `g""it` are git, `"-f"` is -f. UTOKENS is tokens unquoted, index for index.
  unquote_tokens
  cmd0="${UTOKENS[0]##*/}"
  # --- 1. recursive delete (rm -r / -R / -rf / -fr / --recursive[, --force]) ---
  # -f is NOT required to deny: `rm -r` alone deletes every matched file with
  # no confirmation in a non-interactive shell, so it is treated the same as
  # `rm -rf` here.
  if [ "$cmd0" = "rm" ]; then
    flag_r=0
    paths=()
    # flags are read unquoted; a path keeps its raw spelling, which normalize_path unquotes itself
    ti=1
    while [ "$ti" -lt "${#tokens[@]}" ]; do
      tok="${UTOKENS[$ti]}"
      case "$tok" in
        --recursive*) flag_r=1 ;;
        --force*) : ;;
        --) : ;;
        -*)
          case "$tok" in *r*|*R*) flag_r=1 ;; esac
          ;;
        *) paths+=("${tokens[$ti]}") ;;
      esac
      ti=$((ti + 1))
    done
    if [ "$flag_r" -eq 1 ]; then
      all_temp=1
      if [ "${#paths[@]}" -eq 0 ]; then
        all_temp=0
      else
        for p in "${paths[@]}"; do
          # normalize_path's non-zero return (metacharacter, nonexistent
          # component, cycle/hop-budget, readlink failure) is treated as
          # NOT-temporary directly — never call is_temp_path on a partial or
          # absent result.
          resolved_p="$(normalize_path "$p" "$cwd" parent)" || { all_temp=0; continue; }
          is_temp_path "$resolved_p" || all_temp=0
        done
      fi
      if [ "$all_temp" -eq 0 ]; then
        deny "$MSG_RM_RECURSIVE"
      fi
    fi
  fi

  # --- find -delete (permanently removes every matched file) ---
  if [ "$cmd0" = "find" ]; then
    for tok in "${UTOKENS[@]:1}"; do
      if [ "$tok" = "-delete" ]; then
        deny "$MSG_FIND_DELETE"
      fi
    done
  fi

  # --- git subcommands (shared irreversible-command rules — fast/smart/lead/judge) ---
  # The subcommand is found past git's global options (`git -C x push --force`); everything
  # after it is the subcommand's own arguments, from index $after.
  if [ "$cmd0" = "git" ]; then
    find_git_subcommand
  else
    GIT_SUB=""
  fi
  if [ -n "$GIT_SUB" ]; then
    sub="$GIT_SUB"
    after=$((GIT_SUB_I + 1))
    case "$sub" in
      push)
        for tok in "${UTOKENS[@]:$after}"; do
          case "$tok" in
            -f|--force|--force-with-lease*)
              deny "$MSG_PUSH_FORCE"
              ;;
            +*)
              deny "$MSG_PUSH_PLUS"
              ;;
          esac
        done
        ;;
      clean)
        cflag_f=0
        cflag_dx=0
        for tok in "${UTOKENS[@]:$after}"; do
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
          deny "$MSG_CLEAN"
        fi
        ;;
      reset)
        for tok in "${UTOKENS[@]:$after}"; do
          if [ "$tok" = "--hard" ]; then
            deny "$MSG_RESET_HARD"
          fi
        done
        ;;
      checkout)
        rest="${UTOKENS[*]:$after}"
        if [ "$rest" = "-- ." ] || [ "$rest" = "." ]; then
          deny "$MSG_CHECKOUT_DOT"
        fi
        ;;
      restore)
        rest="${UTOKENS[*]:$after}"
        case "$rest" in
          "."|"--staged --worktree ."|"--worktree --staged .")
            deny "$MSG_RESTORE_DOT"
            ;;
        esac
        ;;
      branch)
        bflag_delete=0
        bflag_force=0
        for tok in "${UTOKENS[@]:$after}"; do
          case "$tok" in
            -D) deny "$MSG_BRANCH_D" ;;
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
          deny "$MSG_BRANCH_DELETE_FORCE"
        fi
        ;;
      merge)
        merge_abort_continue=0
        for tok in "${UTOKENS[@]:$after}"; do
          case "$tok" in
            --abort|--continue) merge_abort_continue=1 ;;
          esac
        done
        if [ "$merge_abort_continue" -eq 0 ]; then
          deny "$MSG_MERGE"
        fi
        ;;
      worktree)
        wt_sub="${UTOKENS[$after]:-}"
        case "$wt_sub" in
          remove)
            deny "$MSG_WORKTREE_REMOVE"
            ;;
          prune)
            deny "$MSG_WORKTREE_PRUNE"
            ;;
        esac
        ;;
    esac
  fi

  # --- package publish ---
  if [ "${UTOKENS[1]:-}" = "publish" ]; then
    if in_set "$cmd0" "${PUBLISH_CMDS[@]}"; then
      deny "$(msg_publish "$cmd0")"
    fi
  fi
}
