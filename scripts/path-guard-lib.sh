#!/usr/bin/env bash
# path-guard-lib.sh — sourceable path-normalization/confinement helpers,
# shared by scripts/executor-guard.sh's recursive-delete check (and any
# future caller, e.g. a Write-scoping hook — see docs/plans/executor-fast-read.md).
#
# Bash 3.2 target (this platform's /bin/bash: `bash --version` -> 3.2.57):
# no mapfile/readarray, no associative arrays, no ${var,,}/${var^^}, no &>>,
# no negative-offset substring expansion (${var: -1}), no nameref
# (declare -n) — array "pass by reference" is done via "${arr[@]}" expanded
# into a function's positional args, joined/rebuilt with `local IFS`.
#
# Safely sourceable: no top-level stdin read, no top-level `set`/`exit`, no
# side effect beyond defining functions (normalize_path, is_temp_path, and
# internal _path_guard_* helpers below).
#
# normalize_path <path> <cwd> <mode:parent|full>
#   Resolves <path> to an absolute, symlink- and `.`/`..`-collapsed path,
#   left-to-right, one component at a time, applying `.`/`..` only against
#   the ALREADY-RESOLVED prefix — never a lexical pre-collapse against the
#   raw, unresolved string (that reading would miss a `..` that only
#   escapes once a symlink earlier in the path is followed).
#
#   Prints the resolved absolute path on stdout and returns 0 on success.
#   Returns non-zero and prints NOTHING on any of: an unexpanded shell
#   metacharacter in the raw token (see below), a path component that does
#   not exist (checked for EVERY component, including the final one, in
#   BOTH modes — via the OS's own `-e` test, which follows a component's
#   own symlink chain itself; a dangling symlink therefore fails existence
#   even at a final component `parent` mode never manually dereferences —
#   see the EACCES note below for this test's one known limit), a
#   `readlink` failure, or hop-budget exhaustion / a detected symlink cycle
#   (capped at 40 hops). A caller MUST treat a non-zero return as
#   NOT-temporary (deny) and MUST NEVER call is_temp_path on a partial or
#   absent result — a hop-budget-exhausted partial prefix that happens to
#   sit under a temp directory is not a successful resolution.
#
#   Quote-stripping runs FIRST: a single matching pair of surrounding
#   quotes (both leading+trailing ', or both leading+trailing ") is
#   stripped from the raw token before anything else, so a caller's
#   quote-preserving tokenizer (e.g. executor-guard.sh's quote_walk) does
#   not cause a legitimate quoted temp path to fail the anchored prefix
#   test below. Best-effort, not a shell parser: an unmatched or interior
#   quote character is left alone.
#
#   The metacharacter scan runs next, on the quote-stripped (still
#   unexpanded) token, before any component walk: a literal `$`, a
#   backtick, the two-character sequence `$(` (subsumed by the `$` check),
#   a literal `{` (brace expansion) ANYWHERE in the token, OR a token whose
#   FIRST character is `~` (tilde/home-dir expansion) all deny outright,
#   with no further normalization attempted. Rationale: this guard inspects
#   the command as text before the shell expands anything, so a token that
#   looks temporary and then continues with unexpanded text has a real
#   destination this function cannot see.
#
#   mode governs symlink DEREFERENCE ONLY at the final path component —
#   never whether `.`/`..` is collapsed there, which happens uniformly at
#   every component in both modes. `parent` leaves a symlink AT the final
#   component un-dereferenced (matches `rm` — a trailing symlink is
#   unlinked, not followed); `full` additionally dereferences the final
#   component (matches a file write, which follows a trailing symlink).
#   If the raw input path ends in `/`, mode is forced to `full` regardless
#   of the argument passed — the kernel dereferences a trailing symlink
#   whenever a slash follows it, so `parent` mode would otherwise leave a
#   `rm -r some/link/` escape unresolved.
#
#   A relative <path> resolves against <cwd> before the walk starts. An
#   ABSOLUTE `readlink` target REPLACES the entire resolved-so-far prefix —
#   the walk restarts from root using the target's components. A RELATIVE
#   `readlink` target resolves against the symlink's OWN PARENT directory
#   (the resolved prefix as it stood BEFORE this component) — never root,
#   never <cwd>. This is not an edge case on this platform: `readlink /tmp`
#   returns `private/tmp`, a relative target, so nearly every `/tmp/...`
#   path takes this branch on its very first hop.
#
# is_temp_path <path>
#   True if <path> is confined to a temp location: an ANCHORED
#   (string-start) "/tmp/", "/private/tmp/", or "/private/var/folders/"
#   prefix, OR any path with a "scratchpad" path COMPONENT anywhere (this
#   one stays a component match, not anchored, since a scratchpad dir can
#   validly sit deeper in a temp tree). Intended to be called ONLY on
#   normalize_path's resolved, already quote-stripped output — never on a
#   raw token.
#
# EACCES limit (best-effort, not solved): in Bash 3.2, `[ -L path ]` and
# `[ -e path ]` both return false identically for "not a symlink" and for
# "a parent directory in the path is not searchable" — there is no
# 3.2-portable test that distinguishes the two. An unreadable component may
# therefore be silently under-resolved rather than triggering an explicit
# permission failure. The failure direction is safe: the same permission
# failure that defeats detection here also blocks the underlying `rm` from
# ever reaching that path, so under-detection does not create an
# exploitable escape.

_path_guard_strip_quotes() {
  # Strips ONE matching pair of surrounding quotes from $1 — both leading
  # and trailing ', or both leading and trailing ". Best-effort, not a
  # shell parser: an unmatched or interior quote character is left alone.
  local s="$1"
  local len=${#s}
  if [ "$len" -lt 2 ]; then
    printf '%s' "$s"
    return 0
  fi
  local first="${s:0:1}"
  local last="${s:$((len - 1)):1}"
  if { [ "$first" = "'" ] && [ "$last" = "'" ]; } || { [ "$first" = '"' ] && [ "$last" = '"' ]; }; then
    printf '%s' "${s:1:$((len - 2))}"
  else
    printf '%s' "$s"
  fi
}

_path_guard_split() {
  # Prints one non-empty '/'-delimited component of $1 per line. Bash 3.2
  # has no mapfile/readarray; callers collect this with a `while read`
  # loop over process substitution instead.
  local s="$1"
  local IFS='/'
  local part
  for part in $s; do
    [ -n "$part" ] && printf '%s\n' "$part"
  done
}

_path_guard_join() {
  # Joins all positional args with '/'. Used to render an array of
  # resolved components (called as "${resolved[@]}") back into a single
  # string — Bash 3.2 has no nameref, so an array is always passed this
  # way (expanded into args), never by name.
  local IFS='/'
  printf '%s' "$*"
}

normalize_path() {
  local raw="$1" cwd="$2" mode="$3"
  local path

  # Decision 12: quote-stripping runs first.
  path="$(_path_guard_strip_quotes "$raw")"

  # Decision 8: unexpanded shell metacharacters deny outright, scanned on
  # the quote-stripped (still unexpanded) token, before any component walk.
  case "$path" in
    *'$'*|*'`'*|*'{'*) return 1 ;;
  esac
  case "$path" in
    '~'*) return 1 ;;
  esac

  # Decision 3: trailing-slash override, checked before any splitting (a
  # trailing '/' is otherwise invisible once the path is split into
  # components).
  case "$path" in
    */) mode="full" ;;
  esac

  # Decision 4: resolve a relative path against .cwd before the walk.
  case "$path" in
    /*) : ;;
    *) path="${cwd%/}/$path" ;;
  esac

  local -a queue=()
  local qcomp
  while IFS= read -r qcomp; do
    queue+=("$qcomp")
  done < <(_path_guard_split "$path")

  local -a resolved=()
  local hops=0
  local max_hops=40
  local idx=0
  local n last_index comp candidate is_last is_symlink target rest_start tc
  local -a rest target_comps

  while [ "$idx" -lt "${#queue[@]}" ]; do
    comp="${queue[$idx]}"
    n=${#queue[@]}
    last_index=$((n - 1))

    if [ "$comp" = "." ]; then
      idx=$((idx + 1))
      continue
    fi
    if [ "$comp" = ".." ]; then
      # Decision 1: `.`/`..` collapse against the already-resolved prefix
      # only — applies at EVERY component, including the final one,
      # regardless of mode (decision 1's "final-position collapse" note).
      if [ "${#resolved[@]}" -gt 0 ]; then
        resolved=("${resolved[@]:0:$((${#resolved[@]} - 1))}")
      fi
      idx=$((idx + 1))
      continue
    fi

    if [ "${#resolved[@]}" -eq 0 ]; then
      candidate="/$comp"
    else
      candidate="/$(_path_guard_join "${resolved[@]}" "$comp")"
    fi

    # Decision 7 (existence, every component, both modes; EACCES is
    # best-effort per the header note above).
    if [ ! -e "$candidate" ]; then
      return 1
    fi

    if [ "$idx" -eq "$last_index" ]; then
      is_last=1
    else
      is_last=0
    fi
    if [ -L "$candidate" ]; then
      is_symlink=1
    else
      is_symlink=0
    fi

    if [ "$is_symlink" -eq 1 ] && ! { [ "$is_last" -eq 1 ] && [ "$mode" = "parent" ]; }; then
      # Decision 3: dereference — every component up through the
      # second-to-last always; the final component only in `full` mode
      # (or when the trailing-slash override above already forced it).
      hops=$((hops + 1))
      if [ "$hops" -gt "$max_hops" ]; then
        return 1
      fi
      target="$(readlink "$candidate" 2>/dev/null)"
      if [ -z "$target" ]; then
        return 1
      fi

      rest_start=$((idx + 1))
      rest=("${queue[@]:$rest_start}")
      target_comps=()
      while IFS= read -r tc; do
        target_comps+=("$tc")
      done < <(_path_guard_split "$target")
      # Bash 3.2 (pre-4.4): expanding "${arr[@]}" directly on a currently-
      # EMPTY array under `set -u` throws "unbound variable" — the
      # "${arr[@]+"${arr[@]}"}" idiom below expands to nothing instead of
      # erroring in that case (a slice like "${queue[@]:N}" does not hit
      # this even when it produces zero elements — only a bare "${arr[@]}"
      # on an empty array does).
      queue=("${target_comps[@]+"${target_comps[@]}"}" "${rest[@]+"${rest[@]}"}")

      case "$target" in
        /*)
          # Decision 1: absolute target replaces the ENTIRE resolved-so-far
          # prefix — restart the walk from root.
          resolved=()
          ;;
        *)
          # Decision 1: relative target resolves against the symlink's OWN
          # PARENT directory — `resolved` as it stood BEFORE this
          # component — so it is left unchanged here (never root, never
          # .cwd).
          : ;;
      esac
      idx=0
      continue
    fi

    resolved+=("$comp")
    idx=$((idx + 1))
  done

  printf '/%s\n' "$(_path_guard_join "${resolved[@]+"${resolved[@]}"}")"
  return 0
}

is_temp_path() {
  case "$1" in
    "/tmp/"*|"/private/tmp/"*|"/private/var/folders/"*) return 0 ;;
    # scratchpad matched as a path COMPONENT, not a substring: "/scratchpad",
    # "/scratchpad/...", a bare "scratchpad", or "scratchpad/..." — never
    # e.g. "/Users/me/my-scratchpad-notes", which merely contains the
    # substring.
    *"/scratchpad"|*"/scratchpad/"*|"scratchpad"|"scratchpad/"*) return 0 ;;
    *) return 1 ;;
  esac
}
