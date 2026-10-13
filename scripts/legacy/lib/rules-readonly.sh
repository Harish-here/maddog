# rules-readonly.sh - the checks only executor-lead and executor-judge get: no file writes via Bash.
# Sourced, never run. Needs deny() from the calling hook, parse.sh (strip_command_wrappers),
# hook-io.sh, messages.sh and command-lists.sh. Bash 3.2.

# executor-lead and executor-judge hold Bash for read-only inspection (READONLY_CMDS) but must
# never write, create, truncate, append to, move or delete a file via Bash: the invariant
# "cannot fix or apply by construction" is enforced here, not by instruction. executor-smart is
# deliberately NOT covered: it holds Write/Edit and editing files is its job. Known, accepted
# limitation: judge cannot re-run a gate itself via Bash, because a positive allowlist of
# interpreter forms kept leaking (a stripped `VAR=val` prefix, wrapper flags only partly
# parsed), so none is kept.
#
# check_readonly_writes
# Runs on the current segment for lead and judge only and calls deny() on a file write via Bash.
check_readonly_writes() {
  local cmd0 tok mtok sub tag_mode tag_pos tag_skip redirect_i rest raw_tok target
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
    deny "$MSG_RM_FILE"
  fi

  # A shell is denied itself, with or without -c: this guard does not parse a shell's own -c
  # argument as a nested command line, so `sh -c "echo x > f"` could not be reliably caught by
  # the write-form checks and the only safe answer is to deny the shell.
  if in_set "$cmd0" "${SHELLS[@]}"; then
    deny "$(msg_shell "$cmd0")"
  fi
  if in_set "$cmd0" "${WRITE_CMDS[@]}"; then
    deny "$(msg_write_cmd "$cmd0")"
  fi
  # Both lead and judge deny every interpreter/scripting tool outright, regardless of args or
  # form: neither read-only toolset needs any of them, so a denial by binary name costs neither
  # agent anything real.
  if in_set "$cmd0" "${INTERPRETERS[@]}"; then
    deny "$(msg_interpreter "$cmd0")"
  fi

  case "$cmd0" in
    sed)
      for tok in "${tokens[@]:1}"; do
        case "$tok" in
          -i*) deny "$MSG_SED_INPLACE" ;;
        esac
      done
      ;;
    dd)
      for tok in "${tokens[@]:1}"; do
        case "$tok" in
          of=*) deny "$MSG_DD_OUTPUT" ;;
        esac
      done
      ;;
    awk)
      for mtok in "${tokens_masked[@]:1}"; do
        if [[ "$mtok" == *'>'* ]]; then
          case "$mtok" in
            *'>='*) : ;; # best-effort: skip likely numeric-comparison operator
            *) deny "$MSG_AWK_REDIRECT" ;;
          esac
        fi
      done
      ;;
  esac

  if [ "$cmd0" = "git" ] && [ "${#tokens[@]}" -ge 2 ]; then
    sub="${tokens[1]}"
    if in_set "$sub" "${GIT_WRITE_SUBS[@]}"; then
      deny "$(msg_git_write "$sub")"
    fi
    case "$sub" in
      restore)
        deny "$MSG_GIT_RESTORE"
        ;;
      tag)
        # Only the read-only forms pass: a listing (-l/--list, -n, or a
        # filter such as --contains/--points-at/--merged/--no-merged) or
        # -v/--verify. A positional argument names a NEW tag unless a
        # list/verify mode makes it a pattern or a tag to check
        # (`--sort` alone does not: `git tag --sort=x v1` creates v1).
        # The allowed forms are GIT_TAG_READ_FORMS (command-lists.sh), printed in the
        # denial. Any other flag (-a -s -u -m -F -f -d -e --force --delete ...,
        # or one this guard does not know) denies: fail closed.
        tag_mode=0
        tag_pos=0
        tag_skip=0
        for tok in "${tokens[@]:2}"; do
          if [ "$tag_skip" -eq 1 ]; then
            tag_skip=0
            continue
          fi
          case "$tok" in
            -l|--list|-v|--verify|-n|-n[0-9]*) tag_mode=1 ;;
            --contains=*|--no-contains=*|--merged=*|--no-merged=*|--points-at=*) tag_mode=1 ;;
            --contains|--no-contains|--merged|--no-merged) tag_mode=1 ;;
            --points-at) tag_mode=1; tag_skip=1 ;;
            --sort=*|--format=*) : ;;
            --sort|--format) tag_skip=1 ;;
            -*)
              deny "$(msg_tag_flag "$tok")"
              ;;
            *) tag_pos=1 ;;
          esac
        done
        if [ "$tag_pos" -eq 1 ] && [ "$tag_mode" -eq 0 ]; then
          deny "$(msg_tag_name)"
        fi
        ;;
      checkout)
        for tok in "${tokens[@]:2}"; do
          if [ "$tok" = "--" ]; then
            deny "$MSG_GIT_CHECKOUT_PATH"
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
  # is masked to 'Q' and can never trip this check.
  # Exempt, as not file writes: fd duplication/close forms (2>&1, &>&2,
  # 2>&-) and a target of /dev/null, which discards output rather than
  # persisting it. The target is read from the RAW token, not the masked
  # one, and re-derived from the next token when a space separates the
  # operator from its target (`2> /dev/null`); one layer of surrounding
  # quotes is stripped before the comparison so `'/dev/null'` and
  # `"/dev/null"` match too. Widened no further than /dev/null.
  redirect_i=0
  # strip_command_wrappers above can leave tokens/tokens_masked EMPTY (a
  # segment that was only `FOO=bar`, `env`, `timeout 5`, ...). Bash 3.2
  # (macOS /bin/bash) raises "unbound variable" under `set -u` when a bare
  # "${arr[@]}" expands an empty array — the ${arr[@]+...} form expands to
  # nothing instead (same idiom as path-guard.sh).
  for mtok in "${tokens_masked[@]+"${tokens_masked[@]}"}"; do
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
        deny "$MSG_REDIRECT"
      fi
    fi
    redirect_i=$((redirect_i + 1))
  done
}
