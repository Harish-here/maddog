# heredoc.sh - drop heredoc bodies fed to a harmless reader before the command is split.
# Sourced, never run. Needs parse.sh, command-lists.sh (HEREDOC_READERS, GIT_STDIN_MESSAGE_SUBS)
# and hook-io.sh (in_set). Bash 3.2.

# --- heredoc bodies fed to a harmless reader -----------------------------
# split_command treats every newline as a segment boundary, so the body of
# `python3 - <<'EOF'` / `cat > f.json <<'EOF'` would be judged line by line as
# if each line were a command ((1+2) -> "unquoted '(' starts a subshell").
# skip_heredoc_bodies runs BEFORE the split and deletes a body (and its
# terminator line) ONLY when the reader is positively a harmless non-shell
# program. Every condition must hold; anything else keeps the body in the text
# so it is checked as commands, as if this skip did not exist (unknown ->
# check):
#   1. the command that owns the `<<` (the last command on its line, wrappers
#      peeled) is a plain literal word, no quotes, `$` or backtick, whose
#      basename is in HEREDOC_READERS. A shell, a launcher (setsid, flock,
#      busybox, at, parallel, xargs, env as a command), an interpreter that
#      runs its input as commands (awk, sed, perl, ruby) and anything
#      unidentified are not in the list, so their bodies are checked.
#      One git form is a reader too: `git commit` or `git tag` with `-F -`,
#      `-F-`, `--file=-` or `--file -` (the message comes from stdin, and git
#      does not run it as commands), when `git` is the segment's first literal
#      word (no `VAR=val` or wrapper before it), nothing sits between `git` and
#      the subcommand, and the literal-word and no-`-e` checks in
#      heredoc_consumer pass. `-e` makes git open the message in an editor, and
#      `GIT_EDITOR=sh git commit -e -F -` runs the message as a shell script; a
#      quoted, escaped or variable spelling (`"-e"`, `\-e`, `--"edit"`, `$E`,
#      `"$@"`) hides the flag from the literal text, so every such form keeps
#      the body checked.
#      heredoc_consumer names the form `git:stdin`, which no real basename can
#      equal. Bare `git` stays off the list: `git -c k=v ...` and `!` aliases
#      can run commands, so `git -C x commit -F -` and `git -c k=v commit -F -`
#      are checked.
#   2. nothing consumes the reader's output or runs after it on that line: no
#      later command, no `>(` or `<(`, and the line does not end in `|`, `&&`,
#      `||` or `\` (a pipeline continued past the body).
#   3. no earlier line holds a construct that could pipe the reader's output
#      on (while, for, until, if, case, do, then, done, fi, esac, a bracket or
#      a backtick), and no command before the reader on its own line does.
#   4. the line after the terminator does not start with `|`, `&`, `;`, `)`,
#      `}`, `<` or `>` (a closer or operator that takes the output on).
# The list is deliberately short; add a reader only if it never executes its
# input as commands.
# Lead and judge (deny_writes=1) get one more rule: a skipped body whose delimiter is NOT
# quoted or escaped (`<<EOF`, not `<<'EOF'`, `<<"EOF"` or `<<\EOF`) is expanded by the shell
# before the reader sees it, so `$(...)` or a backtick in it runs a command this guard never
# reads. Such a body makes skip_heredoc_bodies return 3 (the text is still printed), and the
# hook refuses the command; a quoted delimiter keeps the body inert and is still skipped.
# Not handled: a heredoc nested inside a body that is kept (its lines are
# checked as before), and a body written to a file and run later
# (`cat > s.sh <<EOF` ... `bash s.sh`). For fast and smart, `$(...)` inside an unquoted body
# is not examined.

# Prints the real command of one segment (wrappers peeled, basename), or "?"
# when it cannot be identified or is not a plain literal word (leading
# redirect, quotes, `$`, backtick, wrapper form the stripper rejects). Prints
# `git:stdin` for git commit / git tag reading its message from stdin (see the
# list of conditions above). Runs in a subshell at the call site, so the
# deny() override and the tokens mutation stay local.
heredoc_consumer() {
  deny() { printf '?'; exit 0; }
  local k first_word skip_next git_first=0
  tokenize_segment "$1"
  # git counts as the reader only when it is the segment's first word, read
  # BEFORE the wrapper stripper drops any `VAR=val` / env / nice / timeout
  [ "${#tokens[@]}" -gt 0 ] && [ "${tokens[0]##*/}" = "git" ] && git_first=1
  strip_command_wrappers
  if [ "${#tokens[@]}" -eq 0 ]; then
    printf '?'
    return 0
  fi
  case "${tokens_masked[0]}" in
    [0-9]*[\<\>]*|[\<\>]*) printf '?'; return 0 ;;
  esac
  case "${tokens[0]}" in
    *[!A-Za-z0-9_./+-]*) printf '?'; return 0 ;;
  esac
  if [ "${tokens[0]}" != "${tokens_masked[0]}" ]; then
    printf '?'
    return 0
  fi
  if [ "$git_first" -eq 1 ] && [ "${tokens[0]##*/}" = "git" ] && [ "${#tokens[@]}" -ge 2 ]; then
    if in_set "${tokens[1]}" "${GIT_STDIN_MESSAGE_SUBS[@]}"; then
      # Fail-closed allowlist: EVERY token of the command (git, subcommand,
      # each argument; the heredoc operator and its delimiter word are
      # exempt) must be a plain literal word. A quote, backslash, `$`,
      # backtick, glob character, brace or any other character outside
      # the set below can spell `-e` / `--edit` in a way the literal text
      # does not show ("-e", \-e, --"edit", $E, "$@"), so the body stays
      # checked. Also: no `-e`, no `--e...` (an abbreviation of --edit)
      # and no single-dash cluster holding an `e`, since git then opens an
      # editor on the message.
      k=0
      skip_next=0
      while [ "$k" -lt "${#tokens[@]}" ]; do
        if [ "$skip_next" -eq 1 ]; then
          skip_next=0
          k=$((k + 1))
          continue
        fi
        case "${tokens[$k]}" in
          "<<"|"<<-") skip_next=1; k=$((k + 1)); continue ;;
          "<<"*) k=$((k + 1)); continue ;;
        esac
        case "${tokens[$k]}" in
          *[!A-Za-z0-9_./+=:@,-]*) printf 'git'; return 0 ;;
        esac
        if [ "$k" -ge 2 ]; then
          case "${tokens[$k]}" in
            --e*) printf 'git'; return 0 ;;
            --*) : ;;
            -*e*) printf 'git'; return 0 ;;
          esac
        fi
        k=$((k + 1))
      done
      k=2
      while [ "$k" -lt "${#tokens[@]}" ]; do
        case "${tokens[$k]}" in
          -F-|--file=-) printf 'git:stdin'; return 0 ;;
          -F|--file)
            if [ "${tokens[$((k + 1))]:-}" = "-" ]; then
              printf 'git:stdin'
              return 0
            fi
            ;;
        esac
        k=$((k + 1))
      done
    fi
  fi
  printf '%s' "${tokens[0]##*/}"
}

# Succeeds when the text holds a bracket, a backtick or a shell construct
# keyword anywhere (quoted or not: fail toward checking).
heredoc_opens_construct() {
  local w=" $1 "
  case "$w" in
    *'('*|*'{'*|*'`'*|*')'*|*'}'*) return 0 ;;
  esac
  w="${w//[;|&]/ }"
  w="${w//$'\t'/ }"
  case "$w" in
    *" while "*|*" for "*|*" until "*|*" select "*|*" if "*|*" case "*) return 0 ;;
    *" do "*|*" then "*|*" else "*|*" elif "*|*" done "*|*" fi "*|*" esac "*) return 0 ;;
  esac
  return 1
}

# Returns 3 when lead or judge (deny_writes=1) has an unquoted-delimiter body holding `$(` or a
# backtick that was skipped; the text is printed all the same. Returns 0 otherwise.
skip_heredoc_bodies() {
  local text="$1"
  case "$text" in
    *'<<'*) : ;;
    *) printf '%s' "$text"; return 0 ;;
  esac
  local line seg segs consumer check cmp l m rest dash i j n k t tl pre has_here owner_seen
  local active=0 active_delim="" active_dash=0 active_skip=0 active_quoted=1 pend=0
  local qn=0 qi=0 q_skip=1 unquoted_subst=0 raw_rest body_acc="" trail
  local -a out=() held=() lits=() mks=() q_delim=() q_dash=() q_quoted=()
  while IFS= read -r line; do
    if [ "$pend" -eq 1 ]; then
      # the line right after a skipped body's last terminator: if it carries
      # the reader's output onward, put the body and terminator back
      pend=0
      t="${line#"${line%%[![:space:]]*}"}"
      case "$t" in
        '|'*|'&'*|';'*|')'*|'}'*|'<'*|'>'*)
          if [ "${#held[@]}" -gt 0 ]; then
            for k in "${held[@]}"; do out+=("$k"); done
          fi
          ;;
      esac
      held=()
    fi
    if [ "$active" -eq 1 ]; then
      cmp="$line"
      [ "$active_dash" -eq 1 ] && cmp="${line#"${line%%[!$'\t']*}"}"
      if [ "$cmp" = "$active_delim" ]; then
        case "$body_acc" in
          *'$('*|*'`'*) unquoted_subst=1 ;;
        esac
        body_acc=""
        # terminator: held with a skipped body, kept with a checked one
        if [ "$active_skip" -eq 1 ]; then
          held+=("$line")
        else
          out+=("$line")
        fi
        active=0
        if [ "$qi" -lt "$qn" ]; then
          active=1
          active_delim="${q_delim[$qi]}"
          active_dash="${q_dash[$qi]}"
          active_quoted="${q_quoted[$qi]}"
          active_skip="$q_skip"
          qi=$((qi + 1))
        elif [ "$active_skip" -eq 1 ]; then
          pend=1
        fi
      elif [ "$active_skip" -eq 1 ]; then
        if [ "$active_quoted" -eq 0 ] && [ "${deny_writes:-0}" -eq 1 ]; then
          # a backslash-newline is removed from an unquoted body, so `$\` + `(cmd)` is `$(cmd)`:
          # lines are joined before they are scanned
          trail="${line%"${line##*[!\\]}"}"
          if [ $((${#trail} % 2)) -eq 1 ]; then
            body_acc+="${line%\\}"
          else
            body_acc+="$line"
            case "$body_acc" in
              *'$('*|*'`'*) unquoted_subst=1 ;;
            esac
            body_acc=""
          fi
        fi
        held+=("$line")
      else
        out+=("$line")
      fi
      continue
    fi
    out+=("$line")
    case "$line" in *'<<'*) : ;; *) continue ;; esac
    # header line: find every heredoc operator and the command that owns it
    check=0
    qn=0
    qi=0
    q_delim=()
    q_dash=()
    pre=""
    owner_seen=0
    tl="${line%"${line##*[![:space:]]}"}"
    case "$tl" in
      *'|'|*'&&'|*'\') check=1 ;; # pipeline or command continued past the body
    esac
    case "$line" in
      *'>('*|*'<('*) check=1 ;; # process substitution can hand the output to a shell
    esac
    segs="$(split_command "$line")"
    while IFS= read -r seg; do
      seg="${seg#"${seg%%[![:space:]]*}"}"
      seg="${seg%"${seg##*[![:space:]]}"}"
      [ -z "$seg" ] && continue
      # a command after the one owning a heredoc may consume its output
      [ "$owner_seen" -eq 1 ] && check=1
      lits=()
      mks=()
      while IFS=$'\x1f' read -r l m; do
        lits+=("$l")
        mks+=("$m")
      done < <(quote_walk word "$seg")
      n=${#lits[@]}
      has_here=0
      j=0
      while [ "$j" -lt "$n" ]; do
        m="${mks[$j]}"
        l="${lits[$j]}"
        i=0
        while [ "$i" -lt "${#m}" ]; do
          if [ "${m:i:2}" = "<<" ]; then
            if [ "${m:i+2:1}" = "<" ]; then # <<< here-string, not a heredoc
              i=$((i + 3))
              continue
            fi
            has_here=1
            rest="${l:i+2}"
            dash=0
            if [ "${rest:0:1}" = "-" ]; then
              dash=1
              rest="${rest:1}"
            fi
            if [ -z "$rest" ] && [ $((j + 1)) -lt "$n" ]; then
              rest="${lits[$((j + 1))]}"
            fi
            raw_rest="$rest"
            rest="${rest//\'/}"
            rest="${rest//\"/}"
            rest="${rest//\\/}"
            if [ -z "$rest" ]; then
              check=1 # delimiter not recoverable: do not skip anything
            else
              q_delim[$qn]="$rest"
              q_dash[$qn]="$dash"
              # any quote or backslash in the delimiter word keeps the body from expanding
              q_quoted[$qn]=0
              [ "$raw_rest" != "$rest" ] && q_quoted[$qn]=1
              qn=$((qn + 1))
            fi
            break
          fi
          i=$((i + 1))
        done
        j=$((j + 1))
      done
      if [ "$has_here" -eq 1 ]; then
        owner_seen=1
        consumer="$(heredoc_consumer "$seg")"
        case "$HEREDOC_READERS" in
          *" $consumer "*) : ;;
          *) check=1 ;;
        esac
      else
        pre="$pre $seg"
      fi
    done <<< "$segs"
    # a construct opened before the reader (earlier line, or earlier on this
    # one) may pipe its output on
    if [ "$check" -eq 0 ] && [ "$qn" -gt 0 ]; then
      if heredoc_opens_construct "$pre"; then
        check=1
      fi
      k=0
      n=$((${#out[@]} - 1)) # the last entry is this header line
      while [ "$check" -eq 0 ] && [ "$k" -lt "$n" ]; do
        if heredoc_opens_construct "${out[$k]}"; then
          check=1
        fi
        k=$((k + 1))
      done
    fi
    # every queued body shares the line's verdict
    q_skip=1
    [ "$check" -eq 1 ] && q_skip=0
    if [ "$qn" -gt 0 ]; then
      active=1
      active_delim="${q_delim[0]}"
      active_dash="${q_dash[0]}"
      active_quoted="${q_quoted[0]}"
      active_skip="$q_skip"
      qi=1
    fi
  done <<< "$text"
  # a skipped body that never reached its terminator is put back
  if [ "$active" -eq 1 ] && [ "${#held[@]}" -gt 0 ]; then
    for k in "${held[@]}"; do out+=("$k"); done
  fi
  printf '%s\n' "${out[@]}"
  [ "$unquoted_subst" -eq 1 ] && return 3
  return 0
}
