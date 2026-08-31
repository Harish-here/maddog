#!/usr/bin/env bash
# executor-fast-read-write-guard.sh — PreToolUse Write guard, scoped to
# executor-fast-read ONLY — this hand holds Write but no Bash/Edit (decision 21).
#
# Purpose: executor-fast-read (decision 5, amended) holds Write but no
# Bash/Edit — it may file a bulk result under a temp/scratchpad location
# (decision 6) and nowhere else. Per decision 21, this hook is that hand's
# SOLE containment mechanism: the hand has no shell, so there is no
# Bash-side guard layer (executor-guard.sh) behind it to fall back on.
#
# BROAD confinement (decision 6, NOT session-scoped): any path under
# /tmp, /private/tmp, or /var/folders, OR any path with a "scratchpad"
# path component anywhere — including a DIFFERENT session's scratchpad,
# or a bare scratchpad/ directory with no session id. All matching is
# done via scripts/path-guard-lib.sh, sourced below — this script never
# reimplements path-normalization or confinement logic (decision 18).
#
# Wiring: hooks/hooks.json, PreToolUse, matcher "Write" (session-wide, all
# agents and the main conversation) — scoped IN-SCRIPT via the payload's
# .agent_type, exactly like executor-guard.sh's own agent_type case block.
# Every agent_type other than executor-fast-read (bare or plugin-namespaced
# ":executor-fast-read") ALLOWS immediately with no output (fail-open,
# by design — this script polices exactly one hand).
#
# IMPORTANT: Claude Code hooks FAIL OPEN. A missing file, non-executable
# permission, timeout, or malformed JSON output ALLOWS the write. This is
# a GUARD, not a security CONTROL, per the same posture executor-guard.sh
# documents for itself.

set -uo pipefail

# path-guard-lib.sh provides normalize_path/is_temp_path — loaded via a
# path relative to this script's own location, same load-path idiom
# executor-guard.sh uses, so it resolves regardless of the hook's
# invocation cwd (hooks/hooks.json invokes this script via
# ${CLAUDE_PLUGIN_ROOT}/scripts/executor-fast-read-write-guard.sh; cwd at
# hook time is the user's project, not this repo). This script sets only
# `set -uo pipefail` (no -e), so a failed source (file missing, unreadable,
# or a syntax error) does not itself abort the script — instead
# normalize_path/is_temp_path are left undefined, and the call sites below
# fail with bash's "command not found" (exit 127, falsy), tripping the
# deny path: a broken source denies every write for this hand — noisy,
# never weaker.
source "$(dirname "${BASH_SOURCE[0]}")/path-guard-lib.sh"

deny() {
  local reason="$1"
  local ctx="Blocked by executor-fast-read-write-guard.sh: this hand may write only to a temp/scratchpad location (any path under /tmp, /private/tmp, or /var/folders, or any path with a scratchpad path component). STOP and return STATUS: blocked to your caller with this reason — do not retry a different path without narrowing scope."
  local reason_json ctx_json
  reason_json="$(printf '%s' "$reason" | jq -Rs .)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs .)"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  exit 0
}

# --- read stdin once, tolerate absent/malformed input by allowing ---
input="$(cat 2>/dev/null)"
[ -z "$input" ] && exit 0

command -v jq >/dev/null 2>&1 || exit 0

# --- scope: only run for executor-fast-read (or plugin-namespaced form) ---
agent_type="$(printf '%s' "$input" | jq -r '.agent_type // empty' 2>/dev/null)"
case "$agent_type" in
  executor-fast-read|*:executor-fast-read) : ;;
  *) exit 0 ;;
esac

# Write tool payload carries the target path at .tool_input.file_path. An
# absent/empty value cannot be inspected — fail open, same posture
# executor-guard.sh takes on an absent .tool_input.command.
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
[ -z "$path" ] && exit 0

cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"

# `full` mode: matches a file write, which follows a trailing symlink at
# the final component (path-guard-lib.sh's own mode contract).
resolved="$(normalize_path "$path" "$cwd" full)" || {
  deny "Write target could not be normalized to a confined path (unexpanded shell metacharacter, nonexistent intermediate component, symlink cycle, or readlink failure) — denied closed per decision 21, this hand's sole containment mechanism."
}

if ! is_temp_path "$resolved"; then
  deny "Write target resolves outside every accepted temp/scratchpad location (/tmp, /private/tmp, /var/folders, or any path with a scratchpad path component) — this hand may write only there."
fi

exit 0
