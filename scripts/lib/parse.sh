# parse.sh - turn a command line into segments and tokens: the quote-aware walk, the chain
# split, the wrapper stripper and the shape check. Sourced, never run.
# Needs deny() from the calling hook, plus hook-io.sh (in_set), messages.sh and
# command-lists.sh. Bash 3.2.

# --- quote-aware walk -------------------------------------------------
# One shared character-by-character quote-tracking walk (mode-selected), so
# every caller agrees on whether a character sits inside single/double quotes.
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
    # Bookkeeping for the '&' lookbehind exclusion above: every non-continue
    # path reaches this point after writing $c onto buf. Record whether THIS
    # character was itself escaped, so a later lookbehind can tell an escaped
    # trailing '>' (a literal argument character) from a genuine redirect '>'
    # (reuses the esc/esc_next parity, not a second parser).
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
# -c 1`), leading `VAR=val` assignments and then one wrapper from the case
# below (the names are WRAPPERS in command-lists.sh). A flag or argument form
# outside a wrapper's enumerated set calls deny() directly and exits the whole
# script from inside this function.
#
# The classification that follows runs against the command with the wrappers
# peeled, so `env python3 -c 1` and `timeout 5 python3 -c 1` are classified as
# the `python3 -c 1` they are.
#
# Not a shell parser, but not silently permissive either: each wrapper fully
# understands only an enumerated set of its own flags. A flag or argument form
# outside that set (`env -S '...'`, `nice --adjustment=5 ...`, `exec -a foo ...`)
# DENIES immediately instead of falling through with that flag misread as the
# real command and matching no denial case. When unsure, deny.
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
    in_set "${tokens[0]##*/}" "${WRAPPERS[@]}" || break
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
            deny "$(msg_wrapper_flag env "$t")"
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
          deny "$(msg_wrapper_flag exec "${tokens[0]}")"
        fi
        progressed=1
        ;;
      nohup)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]:0:1}" = "-" ]; then
          deny "$(msg_wrapper_flag nohup "${tokens[0]}")"
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
                deny "$(msg_wrapper_missing "nice -n is missing its adjustment argument")" shape
              fi
              ;;
            -[0-9]*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "$(msg_wrapper_flag nice "$t")"
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
          deny "$(msg_wrapper_flag time "${tokens[0]}")"
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
                deny "$(msg_wrapper_missing "timeout $t is missing its argument")" shape
              fi
              ;;
            --signal=*|--kill-after=*|--preserve-status|--foreground|-v|--verbose)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "$(msg_wrapper_flag timeout "$t")"
              ;;
            *) break ;;
          esac
        done
        # the required DURATION positional
        if [ "${#tokens[@]}" -gt 0 ]; then
          tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        else
          deny "$(msg_wrapper_missing "timeout is missing its DURATION argument")" shape
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
                deny "$(msg_wrapper_missing "stdbuf $t is missing its argument")" shape
              fi
              ;;
            -i*|-o*|-e*)
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              ;;
            -*)
              deny "$(msg_wrapper_flag stdbuf "$t")"
              ;;
            *) break ;;
          esac
        done
        progressed=1
        ;;
    esac
  done
}

# tokenize_segment <segment>
# Fills the global `tokens` and `tokens_masked` arrays from one segment, quote-aware (word
# mode of quote_walk): a quoted argument with spaces (an awk/jq program, a grep pattern) stays
# ONE token instead of splitting apart and exposing a bare '>' that was never a shell
# metacharacter. tokens_masked is the parallel masked form the redirect-style checks use.
tokenize_segment() {
  local tok_lit tok_masked
  tokens=()
  tokens_masked=()
  while IFS=$'\x1f' read -r tok_lit tok_masked; do
    tokens+=("$tok_lit")
    tokens_masked+=("$tok_masked")
  done < <(quote_walk word "$1")
}

# check_segment_shape
# Fail-closed on an unquoted leading '(' or '{': a subshell, an ((arithmetic)) command or a
# brace group cannot be confidently identified as a command. Tested against tokens_masked[0]
# (not tokens[0]) so a quoted leading '(' or '{', masked to 'Q', does not match. Deliberately
# blunt: it also denies a harmless bare ((x++)) or (cd x && ls); the guard does not parse
# inside a group, only never silently skips past one.
check_segment_shape() {
  case "${tokens_masked[0]}" in
    '('*)
      deny "$MSG_SHAPE_PAREN" shape
      ;;
    '{')
      deny "$MSG_SHAPE_BRACE" shape
      ;;
  esac
}
