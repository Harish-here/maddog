# parse.sh - turn a command line into segments and tokens: the quote-aware walk, the chain
# split, the command-substitution extractor, the command-word unquoter, the reserved-word, env and
# wrapper strippers, the git subcommand finder and the shape check. Sourced, never run.
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
# Single quotes are literal, except $'...' (ANSI-C quoting), where a backslash escapes the next
# character and so a `\'` does not close the quote.
# Best-effort: does not handle backslash-escaped metacharacters outside
# quotes, or backslash-escaped quotes inside double quotes, beyond a simple
# lookback — adequate for a guard, not a shell parser.
quote_walk() {
  local mode="$1" cmd="$2"
  local -a out=()
  local buf="" mbuf="" c in_single=0 in_double=0 ansi=0
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
      # inside $'...' (ansi=1) a backslash escapes the next character, `\'` included
      if [ "$c" = "'" ] && { [ "$ansi" -eq 0 ] || [ "$esc" -eq 0 ]; }; then
        in_single=0
        ansi=0
      fi
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
          # an unescaped `$` right before the quote makes it ANSI-C quoting, $'...'
          case "$buf" in
            *'$') [ "$buf_last_esc" -eq 0 ] && ansi=1 ;;
          esac
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

# --- the command word, as the shell reads it ---------------------------
# unquote_word <word>
# Sets UNQUOTED to the word with every quote mark and backslash removed, so `\git`, `"git"` and
# `g""it` all read `git`. A guarded binary spelled with quotes is the same binary: every check
# that names a command compares this form, never the raw token. Text the shell would still expand
# (`$G`, a backtick) stays visible in it.
unquote_word() {
  local w="$1" out="" body dec i n c nx sq=0 dq=0 ap="\$'"
  case "$w" in
    *"$ap"*)
      # a word with $'...' (ANSI-C quoting) outside quotes is read one character at a time,
      # tracking quotes, so the body is decoded the way the shell reads it (`\x67` and all):
      # $'git' and $'\x67it' are git, while a `$'` inside single or double quotes is plain text
      i=0
      n=${#w}
      while [ "$i" -lt "$n" ]; do
        c="${w:i:1}"
        nx="${w:i+1:1}"
        if [ "$sq" -eq 1 ]; then
          [ "$c" = "'" ] && sq=0 || out+="$c"
        elif [ "$c" = "\\" ]; then
          out+="$nx"
          i=$((i + 2))
          continue
        elif [ "$c" = "'" ]; then
          sq=1
        elif [ "$c" = '"' ]; then
          dq=$((1 - dq))
        elif [ "$c" = '$' ] && [ "$nx" = "'" ] && [ "$dq" -eq 0 ]; then
          i=$((i + 2))
          body=""
          while [ "$i" -lt "$n" ]; do
            c="${w:i:1}"
            if [ "$c" = "\\" ]; then
              body+="${w:i:2}"
              i=$((i + 2))
              continue
            fi
            [ "$c" = "'" ] && break
            body+="$c"
            i=$((i + 1))
          done
          dec=""
          printf -v dec '%b' "$body"
          out+="$dec"
        else
          out+="$c"
        fi
        i=$((i + 1))
      done
      UNQUOTED="$out"
      return 0
      ;;
  esac
  w="${w//\'/}"
  w="${w//\"/}"
  w="${w//\\/}"
  UNQUOTED="$w"
}

# unquote_tokens
# Sets the global array UTOKENS to unquote_word of every token, in step with tokens. The
# irreversible-command checks compare these, so `git push "-f"` and `git reset "--hard"` read
# like the unquoted spelling.
unquote_tokens() {
  local t
  UTOKENS=()
  for t in "${tokens[@]}"; do
    unquote_word "$t"
    UTOKENS+=("$UNQUOTED")
  done
}

# find_git_subcommand
# tokens[0] is git. Steps over git's global options (the lists in command-lists.sh) to the
# subcommand and sets, in the caller's globals:
#   GIT_SUB          the subcommand, unquoted; empty when none follows
#   GIT_SUB_I        its index in tokens
#   GIT_ALIAS_OPT    1 when a `-c` or `--config-env` sets an `alias.*` key
#   GIT_OPT_UNKNOWN  the first option in none of the lists, empty when there is none. It is
#                    stepped over as a valueless flag; a caller that must fail closed (lead and
#                    judge) refuses it, the rest accept the guess.
find_git_subcommand() {
  local i=1 n=${#tokens[@]} t name val
  GIT_SUB=""
  GIT_SUB_I=0
  GIT_OPT_UNKNOWN=""
  GIT_ALIAS_OPT=0
  while [ "$i" -lt "$n" ]; do
    unquote_word "${tokens[$i]}"
    t="$UNQUOTED"
    case "$t" in
      -*) : ;;
      *)
        GIT_SUB="$t"
        GIT_SUB_I=$i
        return 0
        ;;
    esac
    name="${t%%=*}"
    # `-c alias.x=!cmd` / `--config-env=alias.x=VAR` define a command git then runs for `x`
    val=""
    case "$t" in
      -c) val="${tokens[$((i + 1))]:-}" ;;
      --config-env=*) val="${t#--config-env=}" ;;
      --config-env) val="${tokens[$((i + 1))]:-}" ;;
    esac
    if [ -n "$val" ]; then
      unquote_word "$val"
      case "$UNQUOTED" in
        [aA][lL][iI][aA][sS].*) GIT_ALIAS_OPT=1 ;;
      esac
    fi
    if in_set "$t" "${GIT_OPTS_SHORT_VALUE[@]}"; then
      i=$((i + 2))
    elif [ "$name" != "$t" ] && { in_set "$name" "${GIT_OPTS_VALUE[@]}" || in_set "$name" "${GIT_OPTS_FLAG[@]}"; }; then
      i=$((i + 1))
    elif in_set "$t" "${GIT_OPTS_VALUE[@]}"; then
      i=$((i + 2))
    elif in_set "$t" "${GIT_OPTS_FLAG[@]}"; then
      i=$((i + 1))
    else
      [ -z "$GIT_OPT_UNKNOWN" ] && GIT_OPT_UNKNOWN="$t"
      i=$((i + 1))
    fi
  done
  return 0
}

# --- command substitution -----------------------------------------------
# A command substitution runs a command this guard would otherwise never see. The text inside
# `$(...)`, a backtick pair and a process substitution `<(...)` / `>(...)` is cut out and checked
# as a command line of its own (check_command_text, command-check.sh); what is left behind keeps
# a placeholder (`$(_)`, `` `_` ``, `<(_)`) so the outer segment still reads as one command with
# an argument. Single-quoted text is not expanded, so it is never cut; double-quoted text is.
# `$((...))` is arithmetic, not a command: only a substitution nested inside it is cut out.

# find_substitution_end <text> <index> <opener>
# <index> is the first character after an opener, <opener> is `(` or a backtick. Walks forward
# with a stack of what is open (parentheses, double quotes, single quotes, $'...', backticks) and sets
# SUBST_END to the index of the character that closes the opener, or -1 when none does.
# Not a shell parser: a `)` that ends a case pattern inside a substitution closes it early.
find_substitution_end() {
  local text="$1" j="$2" st="$3" len=${#1} c top dj=-1
  SUBST_END=-1
  while [ "$j" -lt "$len" ]; do
    c="${text:j:1}"
    top="${st: -1}"
    if [ "$top" = "'" ]; then
      [ "$c" = "'" ] && st="${st%?}"
      j=$((j + 1))
      continue
    fi
    if [ "$c" = "\\" ]; then
      j=$((j + 2))
      continue
    fi
    # $'...' (ANSI-C): a backslash escapes inside it (skipped just above), so only a bare quote
    # closes it
    if [ "$top" = "A" ]; then
      [ "$c" = "'" ] && st="${st%?}"
      j=$((j + 1))
      continue
    fi
    if [ "$c" = '$' ]; then
      dj=$((j + 1))
    elif [ "$c" = "'" ] && [ "$top" != '"' ] && [ "$dj" -eq "$j" ]; then
      st="${st}A"
      j=$((j + 1))
      continue
    fi
    case "$top" in
      '"')
        case "$c" in
          '"') st="${st%?}" ;;
          '`') st="${st}\`" ;;
          '$') [ "${text:j+1:1}" = "(" ] && st="${st}(" && j=$((j + 1)) ;;
        esac
        ;;
      '`')
        case "$c" in
          '`') st="${st%?}" ;;
          '"') st="${st}\"" ;;
          "'") st="${st}'" ;;
          '$') [ "${text:j+1:1}" = "(" ] && st="${st}(" && j=$((j + 1)) ;;
        esac
        ;;
      '(')
        case "$c" in
          ')') st="${st%?}" ;;
          '(') st="${st}(" ;;
          '"') st="${st}\"" ;;
          "'") st="${st}'" ;;
          '`') st="${st}\`" ;;
        esac
        ;;
    esac
    if [ -z "$st" ]; then
      SUBST_END=$j
      return 0
    fi
    j=$((j + 1))
  done
  return 1
}

# extract_substitutions <text> [arith]
# <arith> is 1 for the inside of `$((...))`, where a single quote is not a quote.
# Sets, in the caller's globals:
#   SUBST_TOP         the text with each substitution's inside replaced by a placeholder
#   SUBST_LIST        one entry per substitution, outermost only (the recursion finds nested
#                     ones): `C:<inner text>` for a command, `A:<inner text>` for arithmetic
#   SUBST_UNBALANCED  1 when an opener has no closer; the rest of the text is then left as is
#   SUBST_UNREADABLE  1 when the text holds $'...' or $"..." quoting outside any quotes
extract_substitutions() {
  local text="$1" arith="${2:-0}" len=${#1} i=0 c nx out="" in_single=0 in_double=0 prev=" "
  local brace_depth=0 bracket_depth=0
  local inner body rest line outer_end
  SUBST_LIST=()
  SUBST_UNBALANCED=0
  SUBST_UNREADABLE=0
  while [ "$i" -lt "$len" ]; do
    c="${text:i:1}"
    nx="${text:i+1:1}"
    if [ "$in_single" -ne 0 ]; then
      if [ "$in_single" -eq 2 ] && [ "$c" = "\\" ]; then
        out+="${text:i:2}"
        i=$((i + 2))
        continue
      fi
      out+="$c"
      [ "$c" = "'" ] && in_single=0
      prev="'"
      i=$((i + 1))
      continue
    fi
    if [ "$c" = "\\" ]; then
      out+="${text:i:2}"
      prev="x"
      i=$((i + 2))
      continue
    fi
    # inside $((...)) a single quote is an ordinary character: bash still expands what follows
    if [ "$c" = "'" ] && [ "$in_double" -eq 0 ] && [ "$arith" -eq 0 ]; then
      in_single=1
      [ "$prev" = '$' ] && in_single=2 # $'...': a backslash escapes the next character
      out+="$c"
      prev="'"
      i=$((i + 1))
      continue
    fi
    if [ "$c" = '"' ]; then
      in_double=$((1 - in_double))
      out+="$c"
      prev="$c"
      i=$((i + 1))
      continue
    fi
    # depth inside `${...}` and `$[...]`, where a `#` is not a comment and a substitution still
    # runs; only counted outside double quotes, where the text is read as a whole anyway
    if [ "$in_double" -eq 0 ]; then
      case "$c" in
        '{') if [ "$prev" = '$' ] || [ "$brace_depth" -gt 0 ]; then brace_depth=$((brace_depth + 1)); fi ;;
        '}') if [ "$brace_depth" -gt 0 ]; then brace_depth=$((brace_depth - 1)); fi ;;
        '[') if [ "$prev" = '$' ] || [ "$bracket_depth" -gt 0 ]; then bracket_depth=$((bracket_depth + 1)); fi ;;
        ']') if [ "$bracket_depth" -gt 0 ]; then bracket_depth=$((bracket_depth - 1)); fi ;;
      esac
    fi
    # a comment (`#` starting a word) runs to the end of the line and expands nothing, except
    # inside `${...}` and `$[...]`, where it is an ordinary character
    if [ "$c" = "#" ] && [ "$in_double" -eq 0 ] && [ "$brace_depth" -eq 0 ] && [ "$bracket_depth" -eq 0 ]; then
      case "$prev" in
        ' '|$'\t'|$'\n'|';'|'&'|'|'|'(')
          rest="${text:i}"
          line="${rest%%$'\n'*}"
          out+="$line"
          i=$((i + ${#line}))
          continue
          ;;
      esac
    fi
    # `$'...'` (ANSI-C) and `$"..."` (locale) quoting, outside any quotes: SUBST_UNREADABLE=1
    # makes lead and judge refuse the command (in double quotes `$"` is a `$` and a closing quote)
    if [ "$c" = '$' ] && [ "$in_double" -eq 0 ] && { [ "$nx" = "'" ] || [ "$nx" = '"' ]; }; then
      SUBST_UNREADABLE=1
    fi
    if [ "$c" = '$' ] && [ "$nx" = "(" ]; then
      if ! find_substitution_end "$text" $((i + 2)) "("; then
        SUBST_UNBALANCED=1
        out+="${text:i}"
        break
      fi
      outer_end=$SUBST_END
      inner="${text:i+2:$((outer_end - i - 2))}"
      body=""
      # `$((a+b))`: the inside starts with a `(` that closes at its very end
      if [ "${inner:0:1}" = "(" ] && find_substitution_end "$inner" 1 "(" && [ "$SUBST_END" -eq $((${#inner} - 1)) ]; then
        body="${inner:1:${#inner}-2}"
        SUBST_LIST+=("A:$body")
        out+='$((_))'
      else
        SUBST_LIST+=("C:$inner")
        out+='$(_)'
      fi
      i=$((outer_end + 1))
      prev=")"
      continue
    fi
    if [ "$in_double" -eq 0 ] && { [ "$c" = "<" ] || [ "$c" = ">" ]; } && [ "$nx" = "(" ]; then
      if ! find_substitution_end "$text" $((i + 2)) "("; then
        SUBST_UNBALANCED=1
        out+="${text:i}"
        break
      fi
      SUBST_LIST+=("C:${text:i+2:$((SUBST_END - i - 2))}")
      out+="${c}(_)"
      i=$((SUBST_END + 1))
      prev=")"
      continue
    fi
    if [ "$c" = '`' ]; then
      if ! find_substitution_end "$text" $((i + 1)) '`'; then
        SUBST_UNBALANCED=1
        out+="${text:i}"
        break
      fi
      inner="${text:i+1:$((SUBST_END - i - 1))}"
      inner="${inner//\\\`/\`}"
      SUBST_LIST+=("C:$inner")
      out+='`_`'
      i=$((SUBST_END + 1))
      prev="\`"
      continue
    fi
    out+="$c"
    prev="$c"
    i=$((i + 1))
  done
  SUBST_TOP="$out"
}

# --- wrapper/prefix stripping (lead/judge file-write classification) ---
# Mutates the caller's GLOBAL `tokens`/`tokens_masked` arrays in place
# (Bash 3.2: no nameref) so a wrapper cannot launder a write-form or
# interpreter invocation past the classification that follows. Peels, in a
# loop (wrappers can chain, e.g. `nice nohup timeout 5 env FOO=1 python3
# -c 1`), leading `VAR=val` assignments and then one wrapper from the case
# below (the names are WRAPPERS in command-lists.sh). A flag or argument form
# outside a wrapper's enumerated set calls deny() directly and exits the whole
# script from inside this function. The wrapper name is read unquoted (`\env`, `"timeout"`).
# rtk and env are wrappers every agent gets: check_segment also calls strip_leading_prefixes
# before the irreversible-command checks, so `rtk git push -f` and `env -i git push -f` are
# judged as `git push -f`.
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
  local progressed=1 t w
  while [ "$progressed" -eq 1 ] && [ "${#tokens[@]}" -gt 0 ]; do
    progressed=0
    if [[ "${tokens[0]}" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
      tokens=("${tokens[@]:1}")
      tokens_masked=("${tokens_masked[@]:1}")
      progressed=1
      continue
    fi
    unquote_word "${tokens[0]}"
    w="${UNQUOTED##*/}"
    in_set "$w" "${WRAPPERS[@]}" || break
    case "$w" in
      rtk)
        strip_rtk
        progressed=1
        ;;
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

# strip_rtk
# tokens[0] is rtk. Drops it and, when it names a subcommand that runs the rest as a command
# (proxy, err, test, summary), that too, so `rtk proxy bash x`, `rtk err bash -c x` and `rtk git
# push -f` leave `bash x`, `bash -c x` and `git push -f`. `rtk run <string>` runs the string with
# sh -c: it is left in RTK_RUN_TEXT for check_segment to check as a command line, and the tokens
# are emptied. An option before the command (`rtk -v git ...`) is not understood: lead and judge
# (deny_writes=1) are refused it, the others have it skipped as a valueless flag. Mutates the
# global tokens/tokens_masked.
strip_rtk() {
  local pass t
  tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
  pass=0
  while [ "$pass" -lt 2 ]; do
    pass=$((pass + 1))
    while [ "${#tokens[@]}" -gt 0 ]; do
      unquote_word "${tokens[0]}"
      [ "${UNQUOTED:0:1}" = "-" ] || break
      if [ "${deny_writes:-0}" -eq 1 ]; then
        deny "$(msg_wrapper_flag rtk "${tokens[0]}")"
      fi
      tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
    done
    [ "${#tokens[@]}" -gt 0 ] || return 0
    unquote_word "${tokens[0]}"
    case "$UNQUOTED" in
      proxy|err|test|summary)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        ;;
      run)
        if [ "${deny_writes:-0}" -eq 1 ]; then
          deny "$(msg_unreadable "rtk run")" shape
        fi
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        if [ "${#tokens[@]}" -eq 1 ]; then
          t="${tokens[0]}"
          if [ "${#t}" -ge 2 ] && { [ "${t:0:1}" = "'" ] || [ "${t:0:1}" = '"' ]; } && [ "${t: -1}" = "${t:0:1}" ]; then
            t="${t:1:${#t}-2}"
          fi
          RTK_RUN_TEXT="$t"
        else
          RTK_RUN_TEXT="${tokens[*]+${tokens[*]}}"
        fi
        tokens=(); tokens_masked=()
        return 0
        ;;
      *) return 0 ;;
    esac
  done
}

# strip_leading_keywords
# Every agent. Drops the reserved words that open or close a compound command from the front of
# the segment (SHELL_KEYWORDS), so `then bash x` and `! bash x` are judged as `bash x`. Only
# unquoted words count: `"if" x` runs a program called if. Mutates the global tokens/tokens_masked.
#   for, select  the header runs up to its `do`; what follows `do` in the same segment
#                (`for x do echo hi >f`) is a command and is kept. A header with no `do` is words,
#                not commands, and the segment is emptied.
#   case         CASE_OPEN counts the open cases, so a pattern is recognised only inside one. The
#                header is dropped up to its first pattern's `)`, and a later segment's leading
#                pattern is too (`b) cmd`, `*)cmd`: a space after the `)` is optional); the
#                command after the pattern is kept. A pattern that starts with `(` is dropped
#                only where it is certain to be one: right after `in`, or, for fast and smart,
#                at CASE_EXPECT (the segment after `in` or after a `;;`). For lead and judge any
#                other `(` stays, and the shape check refuses it.
# Sets KW_STRIPPED=1 when it dropped anything.
strip_leading_keywords() {
  local m k found head pat tail pat_ok="$CASE_EXPECT" certain=0 done_pat=0
  KW_STRIPPED=0
  CASE_EXPECT=0
  while [ "${#tokens[@]}" -gt 0 ]; do
    m="${tokens_masked[0]}"
    if [ "$m" = "${tokens[0]}" ] && in_set "$m" "${SHELL_KEYWORDS[@]}"; then
      [ "$m" = "esac" ] && [ "$CASE_OPEN" -gt 0 ] && CASE_OPEN=$((CASE_OPEN - 1))
      tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
      KW_STRIPPED=1
      continue
    fi
    if [ "${deny_writes:-0}" -eq 1 ] && [ "$m" = "${tokens[0]}" ]; then
      # constructs lead and judge are refused: the guard cannot read them with certainty
      case "$m" in
        case|select|coproc) deny "$(msg_unreadable "$m")" shape ;;
        for)
          for k in "${tokens_masked[@]}"; do
            case "$k" in
              '(('*) deny "$(msg_unreadable "a (( )) arithmetic loop header")" shape ;;
            esac
          done
          ;;
      esac
    fi
    if [ "$m" = "${tokens[0]}" ] && { [ "$m" = "for" ] || [ "$m" = "select" ]; }; then
      KW_STRIPPED=1
      found=-1
      k=1
      while [ "$k" -lt "${#tokens_masked[@]}" ]; do
        if [ "${tokens_masked[$k]}" = "do" ] && [ "${tokens[$k]}" = "do" ]; then
          found=$k
          break
        fi
        k=$((k + 1))
      done
      if [ "$found" -ge 0 ]; then
        tokens=("${tokens[@]:$((found + 1))}"); tokens_masked=("${tokens_masked[@]:$((found + 1))}")
        continue
      fi
      tokens=(); tokens_masked=()
      break
    fi
    if [ "$m" = "${tokens[0]}" ] && [ "$m" = "case" ]; then
      KW_STRIPPED=1
      CASE_OPEN=$((CASE_OPEN + 1))
      found=-1
      k=1
      while [ "$k" -lt "${#tokens_masked[@]}" ]; do
        if [ "${tokens_masked[$k]}" = "in" ] && [ "${tokens[$k]}" = "in" ]; then
          found=$k
          break
        fi
        k=$((k + 1))
      done
      if [ "$found" -ge 0 ]; then
        tokens=("${tokens[@]:$((found + 1))}"); tokens_masked=("${tokens_masked[@]:$((found + 1))}")
        certain=1
        [ "${#tokens[@]}" -eq 0 ] && CASE_EXPECT=1
        continue
      fi
      tokens=(); tokens_masked=()
      break
    fi
    if [ "$CASE_OPEN" -gt 0 ]; then
      if [ "$m" = "in" ] && [ "${tokens[0]}" = "in" ]; then
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        certain=1
        [ "${#tokens[@]}" -eq 0 ] && CASE_EXPECT=1
        continue
      fi
      case "$m" in
        *')'*)
          if [ "$done_pat" -eq 0 ]; then
            head="${m%%')'*}"
            pat="${head#'('}"
            # a substitution (`$(_)`) or a nested paren is not a pattern
            case "$pat" in
              *'('*|*'$'*|*'`'*) break ;;
            esac
            if [ "$pat" != "$head" ] && [ "$certain" -eq 0 ] && { [ "${deny_writes:-0}" -eq 1 ] || [ "$pat_ok" -eq 0 ]; }; then
              break
            fi
            tail="${tokens[0]:$((${#head} + 1))}"
            if [ -n "$tail" ]; then
              tokens[0]="$tail"
              tokens_masked[0]="${m:$((${#head} + 1))}"
            else
              tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
            fi
            done_pat=1
            continue
          fi
          ;;
      esac
    fi
    break
  done
}

# env_split_string <string>
# env -S splits a string into a command line. Peels one layer of surrounding quotes and puts the
# words in front of the global tokens, so the string is checked as the command it will run.
env_split_string() {
  local s="$1" q tok_lit tok_masked
  local -a new=() new_masked=()
  q="${s:0:1}"
  if [ "${#s}" -ge 2 ] && { [ "$q" = "'" ] || [ "$q" = '"' ]; } && [ "${s: -1}" = "$q" ]; then
    s="${s:1:${#s}-2}"
  fi
  while IFS=$'\x1f' read -r tok_lit tok_masked; do
    new+=("$tok_lit")
    new_masked+=("$tok_masked")
  done < <(quote_walk word "$s")
  tokens=("${new[@]+"${new[@]}"}" "${tokens[@]+"${tokens[@]}"}")
  tokens_masked=("${new_masked[@]+"${new_masked[@]}"}" "${tokens_masked[@]+"${tokens_masked[@]}"}")
}

# strip_env
# tokens[0] is env. Drops env, its options with their values and its NAME=value words, so the
# command it runs is what follows (`env -i FOO=1 git push -f` leaves `git push -f`). env's flag
# surface is wide: lead and judge (deny_writes=1) are denied ANY flag, as in strip_command_wrappers.
# The others skip a flag, taking the next word as its value for -u -C -P -a (and the long
# --unset --chdir --argv0), and read the string of -S / --split-string as a command line; short
# flags may be clustered (`-iS 'git push -f'`).
strip_env() {
  local t val rest ch
  tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
  while [ "${#tokens[@]}" -gt 0 ]; do
    t="${tokens[0]}"
    if [[ "$t" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
      tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
      continue
    fi
    [ "${t:0:1}" = "-" ] || break
    if [ "${deny_writes:-0}" -eq 1 ]; then
      deny "$(msg_wrapper_flag env "$t")"
    fi
    case "$t" in
      --split-string)
        val="${tokens[1]:-}"
        tokens=("${tokens[@]:2}"); tokens_masked=("${tokens_masked[@]:2}")
        env_split_string "$val"
        ;;
      --split-string=*)
        val="${t#--split-string=}"
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        env_split_string "$val"
        ;;
      --unset|--chdir|--argv0)
        tokens=("${tokens[@]:2}"); tokens_masked=("${tokens_masked[@]:2}")
        ;;
      -[!-]*)
        # a cluster of short flags (`-i`, `-0u NAME`, `-iS 'cmd'`): the first letter that takes
        # a value (S u C P a) takes the rest of the word, or the next word when nothing is left
        rest="${t:1}"
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        while [ -n "$rest" ]; do
          ch="${rest:0:1}"
          rest="${rest:1}"
          case "$ch" in
            S)
              val="$rest"
              if [ -z "$val" ] && [ "${#tokens[@]}" -gt 0 ]; then
                val="${tokens[0]}"
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              fi
              env_split_string "$val"
              break
              ;;
            u|C|P|a)
              if [ -z "$rest" ] && [ "${#tokens[@]}" -gt 0 ]; then
                tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
              fi
              break
              ;;
          esac
        done
        ;;
      --)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        break
        ;;
      *)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        ;;
    esac
  done
}

# strip_wrapper_lenient <wrapper>
# tokens[0] is one of command exec nohup nice time timeout stdbuf. Drops it, its options (and the
# value of the ones that take one) and, for timeout, the DURATION, so the irreversible-command
# checks see the command it runs (`timeout -s KILL 5 git push -f` leaves `git push -f`). Unlike
# strip_command_wrappers it never denies: a form it misreads only means the check sees a
# different word, as it did before the peel. Used for fast and smart. Mutates tokens/tokens_masked.
strip_wrapper_lenient() {
  local w="$1" t
  tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
  while [ "${#tokens[@]}" -gt 0 ]; do
    t="${tokens[0]}"
    [ "${t:0:1}" = "-" ] || break
    case "$w:$t" in
      nice:-n|nice:--adjustment|exec:-a|time:-f|time:-o|time:--format|time:--output|\
      timeout:-s|timeout:-k|timeout:--signal|timeout:--kill-after|\
      stdbuf:-i|stdbuf:-o|stdbuf:-e|stdbuf:--input|stdbuf:--output|stdbuf:--error)
        tokens=("${tokens[@]:2}"); tokens_masked=("${tokens_masked[@]:2}")
        ;;
      *)
        tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
        ;;
    esac
  done
  if [ "$w" = "timeout" ] && [ "${#tokens[@]}" -gt 0 ]; then
    tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
  fi
}

# strip_leading_prefixes
# Every agent. Peels what runs another command without being it: leading `NAME=value`
# assignments and the wrappers `env`, `rtk`, `nice`, `timeout`, `time`, `command`, `exec`,
# `nohup` and `stdbuf`, in any order, so the irreversible-command checks see the command that
# runs (`FOO=1 git push -f`, `env -i git push -f`, `timeout 5 git push -f`). Lead and judge peel
# the wrappers with strip_command_wrappers, which denies forms it does not understand; fast and
# smart with strip_wrapper_lenient, which only peels. Sets PEELED_OTHER=1 when it dropped an
# assignment, env or a wrapper (not rtk). Mutates the global tokens/tokens_masked.
strip_leading_prefixes() {
  local progressed=1 w
  while [ "$progressed" -eq 1 ] && [ "${#tokens[@]}" -gt 0 ]; do
    progressed=0
    if [[ "${tokens[0]}" =~ ^[A-Za-z_][A-Za-z0-9_]*=.*$ ]]; then
      tokens=("${tokens[@]:1}"); tokens_masked=("${tokens_masked[@]:1}")
      PEELED_OTHER=1
      progressed=1
      continue
    fi
    unquote_word "${tokens[0]}"
    w="${UNQUOTED##*/}"
    case "$w" in
      rtk) strip_rtk; progressed=1 ;;
      env) PEELED_OTHER=1; strip_env; progressed=1 ;;
      command|exec|nohup|nice|time|timeout|stdbuf)
        PEELED_OTHER=1
        # lead and judge: the strict stripper, which denies a form it does not understand;
        # the others: a lenient peel that never refuses, it only exposes the command
        if [ "${deny_writes:-0}" -eq 1 ]; then
          strip_command_wrappers
        else
          strip_wrapper_lenient "$w"
        fi
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
