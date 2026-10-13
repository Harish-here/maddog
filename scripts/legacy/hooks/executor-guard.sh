#!/usr/bin/env bash
# executor-guard.sh — PreToolUse Bash guard, scoped to executor-fast, executor-smart,
# executor-lead, and executor-judge. Two layers of enforcement, both structural (not
# instruction-based):
#
#  1. IRREVERSIBLE-COMMAND DENIAL (all four agents): lib/rules-irreversible.sh. A short list of
#     irreversible/destructive Bash commands is bounced back to the caller, who must STOP and
#     return blocked. A SHAPE refusal (a command the guard cannot parse: a leading `(` or `{`, a
#     wrapper missing its argument, an internal error) is not an irreversible-action denial: its
#     context says so and tells the caller to rewrite as simpler commands and retry instead of
#     stopping (see deny() below and lib/messages.sh).
#
#  2. FILE-WRITE DENIAL (executor-lead and executor-judge only): lib/rules-readonly.sh. Both hold
#     Bash for read-only inspection but must never write, create, move or delete a file via Bash;
#     executor-smart is deliberately not covered (it holds Write/Edit).
#
# Layout: this file is the hook; everything it consults is sourced from ../lib (hook-io.sh
# input and deny JSON, agents.sh name rules, messages.sh every text, command-lists.sh every
# command-name set, parse.sh and heredoc.sh the command reader, path-guard.sh path confinement).
#
# Wiring: plugin-level hooks/hooks.json (session-wide, matcher "Bash") fires this script for every
# agent and the main conversation. Because that wiring is not agent-scoped, scoping is enforced
# IN-SCRIPT via the payload's .agent_type: the checks run only for the four agents above (bare or
# plugin-namespaced, e.g. "maddog:executor-judge"). Every other case, a different agent_type or
# none (the main conversation), ALLOWS immediately with no output.
#
# IMPORTANT: Claude Code hooks FAIL OPEN. If this file is missing, not executable, times out, or
# emits malformed JSON, the tool call proceeds as if no hook existed. This script is therefore a
# GUARD, not a security CONTROL: it catches the common irreversible/write patterns, it does not
# guarantee safety against a determined or unusual command.
#
# Protocol: read the PreToolUse JSON payload from stdin, inspect .tool_input.command, then either
# print nothing and exit 0 (ALLOW), or print a hookSpecificOutput deny JSON and exit 0 (DENY; exit
# 2 would also block but gives the model no reason, so always use the JSON form). Any failure to
# parse input ALLOWS the call. Exceptions, which deny instead:
#   - jq missing: denies a payload whose raw text names a guarded agent_type (hook_start).
#   - a lib that fails to load: denies the same payloads (the inline fallback below).
#   - once the caller is known to be executor-lead or executor-judge, an unexpected non-zero exit
#     (an internal guard bug): the fail-closed backstop below.

set -uo pipefail

HOOK_NAME="${BASH_SOURCE[0]##*/}"
GUARDED_AGENTS='executor-fast|executor-smart|executor-lead|executor-judge'
LIB="$(dirname "${BASH_SOURCE[0]}")/../lib"

# A lib that is missing, unreadable or has a syntax error must not let a guarded agent through.
# This fallback uses nothing from the libs: a raw-input match on the guarded agent types, static JSON.
if ! { source "$LIB/hook-io.sh" && source "$LIB/agents.sh" && source "$LIB/messages.sh" \
  && source "$LIB/command-lists.sh" && source "$LIB/parse.sh" && source "$LIB/heredoc.sh" \
  && source "$LIB/rules-irreversible.sh" && source "$LIB/rules-readonly.sh" \
  && source "$LIB/path-guard.sh"; }; then
  fallback_input="$(cat 2>/dev/null)"
  fallback_re='"agent_type"[[:space:]]*:[[:space:]]*"([^"]*:)?('"$GUARDED_AGENTS"')"'
  if [[ "$fallback_input" =~ $fallback_re ]]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"A maddog guard library failed to load, so this call was denied rather than allowed unchecked. Repair or reinstall the plugin, then retry.","additionalContext":"Blocked by '"$HOOK_NAME"': a guard library failed to load. STOP and return blocked to your caller - do not attempt the call."}}'
  fi
  exit 0
fi

# Denial context depends on the refusal kind. shape: the guard could not parse the command; the
# context says rewrite and retry, for every agent. Anything else (irreversible action, file
# write): STOP and return blocked. deny_writes and is_judge are set by the scope check below and
# read at call time.
deny() {
  local reason="$1" kind="${2:-}" ctx
  if [ "$kind" = "shape" ]; then
    ctx="$SHAPE_CONTEXT"
  else
    ctx="$(msg_blocked_context "${deny_writes:-0}" "${is_judge:-0}")"
  fi
  emit_deny escaped "$reason" "$ctx"
  exit 0
}

hook_start "$HOOK_NAME" "$GUARDED_AGENTS"

# --- scope. deny_writes=1 layers the file-write denial on top of the shared irreversible-command
#     checks for lead and judge only. ---
agent_type="$(field .agent_type)"
deny_writes=0
is_judge=0
if agent_is "$agent_type" executor-fast executor-smart; then
  :
elif agent_is "$agent_type" executor-lead; then
  deny_writes=1
elif agent_is "$agent_type" executor-judge; then
  deny_writes=1
  is_judge=1
else
  exit 0
fi

# --- fail-closed backstop (lead/judge only) ---
# Past this point, any unexpected non-zero exit (an unbound variable under `set -u`, a bad
# substitution, ...) would reach Claude Code as a "non-blocking" hook error and the Bash call would
# run UNCHECKED. For the two read-only executors, turn that into a deny instead. Every intended
# path exits 0 (allow, or deny() which exits 0 after printing), so a non-zero status here can only
# be an internal failure. The JSON is built without jq (jq itself may be what failed); it carries
# the shape-refusal context, as the command is unreadable to the guard, not banned.
if [ "$deny_writes" -eq 1 ]; then
  fail_closed() {
    local rc=$?
    [ "$rc" -eq 0 ] && return 0
    emit_deny static "$MSG_INTERNAL_ERROR_REASON" "$SHAPE_CONTEXT"
    exit 0
  }
  trap fail_closed EXIT
fi

cmd="$(field .tool_input.command)"
[ -z "$cmd" ] && exit 0

# .cwd resolves a relative path in the recursive-delete check (see rules-irreversible.sh).
cwd="$(field .cwd)"

# --- drop heredoc bodies fed to non-shell programs before splitting ---
cmd="$(skip_heredoc_bodies "$cmd")"

# --- split into pipeline/chain segments so matches after ;, &&, ||, | are caught ---
segments_raw="$(split_command "$cmd")"

while IFS= read -r segment; do
  segment="${segment#"${segment%%[![:space:]]*}"}"
  segment="${segment%"${segment##*[![:space:]]}"}"
  [ -z "$segment" ] && continue

  tokenize_segment "$segment"
  [ "${#tokens[@]}" -eq 0 ] && continue

  check_segment_shape
  check_irreversible
  if [ "$deny_writes" -eq 1 ]; then
    check_readonly_writes
  fi
done <<< "$segments_raw"

exit 0
