#!/usr/bin/env bash
# judge-dispatch-guard.sh — PreToolUse guard restricting subagent dispatches per
# caller: executor-judge → executor-fast-read, researcher; executor-smart → executor-fast, executor-fast-read.
#
# Purpose: executor-judge's own file already says it may rent only
# executor-fast-read or researcher as hands, and never a hand that can make a
# change (it is fix-less by design — findings route back to the caller, it
# never repairs). That limit would otherwise live only as a sentence in the
# agent's own description; this hook makes it structural.
#
# PAYLOAD SHAPE (confirmed against captured payloads). A subagent dispatch
# always has .tool_name == "Agent". The target
# subagent is at .tool_input.subagent_type (plugin-namespaced, e.g.
# "maddog:executor-fast-read"). The calling subagent is at .agent_type, populated
# whenever a subagent makes the call (e.g. "general-purpose"), alongside
# .agent_id; .agent_type is absent entirely when the MAIN conversation
# dispatches, and that case must always allow.
#
# Like executor-guard.sh, this hook FAILS OPEN on genuine inability
# to inspect the payload: empty stdin, malformed JSON, a
# tool_name other than "Agent", or a caller other than executor-judge all
# mean ALLOW. But once the caller IS executor-judge dispatching an "Agent"
# call, an ABSENT, empty, or null .tool_input.subagent_type is not the same
# kind of gap — per the Agent tool contract, omitting subagent_type runs the
# default general-purpose agent, which holds every tool including Write and
# Edit. That is the single most obvious bypass of this hook, so it is a DENY,
# not an ALLOW. It denies whenever the caller is executor-judge (bare or
# plugin-namespaced, e.g. "maddog:executor-judge") and the resolved target —
# absent/empty/null counting as "the default agent" — is neither
# executor-fast-read nor researcher (bare or namespaced).
#
# Scope: executor-judge and executor-smart. executor-lead is deliberately left
# unrestricted here.
#
# Diagnostic logging: OFF by default. The full payload of every dispatch
# includes the complete prompt text handed to the subagent — a shipped hook
# must never spool user prompts to disk unasked. Logging only activates when
# the environment variable MADDOG_DISPATCH_PROBE is set to a non-empty value,
# writing to ${TMPDIR:-/tmp}/maddog-dispatch-probe.log for future diagnosis.
# With the variable unset (the default), log_probe is a no-op: no file is
# opened, created, or touched.
#
# Protocol: read the PreToolUse JSON payload from stdin, then either:
#   - print nothing and exit 0 (ALLOW), or
#   - print a hookSpecificOutput deny JSON and exit 0 (DENY, exit 2 would
#     also block but gives the model no reason — always use the JSON form).
# Any failure to parse input ALLOWS the call — never block on our own
# inability to inspect the payload. Missing jq, or a lib that fails to load, denies only a
# payload whose raw text names a guarded agent_type; every other caller still ALLOWS. A
# logging failure must never change the allow/deny outcome either.

set -uo pipefail

HOOK_NAME="${BASH_SOURCE[0]##*/}"
GUARDED_AGENTS='executor-judge|executor-smart'
LIB="$(dirname "${BASH_SOURCE[0]}")/../lib"

# A lib cut off at a function or variable boundary sources without error but leaves everything
# after the cut undefined, and a missing function or list fails open for the fast executors.
# REQUIRED_FUNCS and REQUIRED_VARS list every function and every top-level variable (command
# lists, refusal texts) the sourced libs define; a missing one takes the same path as a lib that
# fails to load. tests/guard/test_missing_lib.py keeps both lists equal to what the libs define.
REQUIRED_FUNCS=(
  hook_start field emit_deny in_set list_join agent_is agent_target_in agent_raw_re
  msg_jq_missing_context msg_dispatch_reason msg_dispatch_context msg_no_target_reason
  msg_no_target_context msg_blocked_context msg_wrapper_flag msg_wrapper_missing
  msg_git_config msg_git_config_option msg_git_option msg_unreadable msg_publish msg_shell
  msg_write_cmd msg_interpreter msg_git_write _msg_tag_allowed msg_tag_flag msg_tag_name
)
REQUIRED_VARS=(
  MSG_JQ_MISSING_REASON MSG_PATTERN_REASON MSG_PATTERN_CONTEXT WHY_EXECUTOR_JUDGE
  WHY_EXECUTOR_SMART SHAPE_CONTEXT MSG_INTERNAL_ERROR_REASON MSG_SHAPE_PAREN
  MSG_SHAPE_BRACE MSG_DYNAMIC_COMMAND MSG_SUBST_UNBALANCED MSG_SUBST_TOO_DEEP
  MSG_FUNCTION_DEF MSG_HEREDOC_SUBST MSG_RM_RECURSIVE MSG_FIND_DELETE MSG_PUSH_FORCE
  MSG_PUSH_PLUS MSG_CLEAN MSG_RESET_HARD MSG_CHECKOUT_DOT MSG_RESTORE_DOT MSG_BRANCH_D
  MSG_BRANCH_DELETE_FORCE MSG_MERGE MSG_WORKTREE_REMOVE MSG_WORKTREE_PRUNE MSG_RM_FILE
  MSG_SED_INPLACE MSG_DD_OUTPUT MSG_AWK_REDIRECT MSG_GIT_RESTORE MSG_GIT_CHECKOUT_PATH
  MSG_REDIRECT
)
libs_complete() {
  local f
  for f in "${REQUIRED_FUNCS[@]}"; do
    declare -F "$f" >/dev/null || return 1
  done
  for f in "${REQUIRED_VARS[@]}"; do
    declare -p "$f" >/dev/null 2>&1 || return 1
  done
}

# A lib that is missing, unreadable, has a syntax error or is cut short must not let a guarded
# agent through.
# This fallback uses nothing from the libs: a raw-input match on the guarded agent types, static JSON.
if ! { source "$LIB/hook-io.sh" && source "$LIB/agents.sh" && source "$LIB/messages.sh"; } || ! libs_complete; then
  fallback_input="$(cat 2>/dev/null)"
  fallback_re='"agent_type"[[:space:]]*:[[:space:]]*"([^"]*:)?('"$GUARDED_AGENTS"')"'
  if [[ "$fallback_input" =~ $fallback_re ]]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"A maddog guard library failed to load, so this call was denied rather than allowed unchecked. Repair or reinstall the plugin, then retry.","additionalContext":"Blocked by '"$HOOK_NAME"': a guard library failed to load. STOP and return blocked to your caller - do not attempt the call."}}'
  fi
  exit 0
fi

caller=""; allowed_desc=""; why=""
allowed=()

PROBE_LOG="${TMPDIR:-/tmp}/maddog-dispatch-probe.log"

# --- best-effort probe logging; a write failure here must never affect the
#     allow/deny decision, so every call is wrapped and its result discarded.
#     No-op entirely unless MADDOG_DISPATCH_PROBE is set — see header. ---
log_probe() {
  [ -n "${MADDOG_DISPATCH_PROBE:-}" ] || return 0
  local line="$1"
  {
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || printf 'unknown')"
    printf '%s\t%s\n' "$ts" "$line" >> "$PROBE_LOG"
  } 2>/dev/null || true
}

deny() {
  emit_deny escaped "$(msg_dispatch_reason "$caller" "$1" "$allowed_desc")" "$(msg_dispatch_context "$why")"
  exit 0
}

# --- the no-subagent-type bypass: an Agent dispatch that names nothing
#     still runs an agent — the default general-purpose one, with every
#     tool including Write/Edit. Deny it as what it is, not as a gap. ---
deny_no_target() {
  emit_deny escaped "$(msg_no_target_reason "$caller" "$allowed_desc")" "$(msg_no_target_context "$why")"
  exit 0
}

hook_start "$HOOK_NAME" "$GUARDED_AGENTS"

# --- defensive: only ever act on a subagent dispatch tool call ---
tool_name="$(field .tool_name)"
[ "$tool_name" = "Agent" ] || exit 0

# --- scope: act for executor-judge and executor-smart (bare or namespaced);
#     every other caller, and the main conversation (no agent_type), ALLOWS.
#     `allowed` is the caller's hands, printed in the denial and used for the match. ---
agent_type="$(field .agent_type)"
if agent_is "$agent_type" executor-judge; then
  caller="executor-judge"
  allowed=(executor-fast-read researcher)
  why="$WHY_EXECUTOR_JUDGE"
elif agent_is "$agent_type" executor-smart; then
  caller="executor-smart"
  allowed=(executor-fast executor-fast-read)
  why="$WHY_EXECUTOR_SMART"
else
  exit 0
fi
allowed_desc="$(list_join ' or ' "${allowed[@]}")"

# --- the target subagent. An absent key, an empty string, and JSON null
#     all collapse to "" via `// empty` — and for executor-judge dispatching
#     "Agent", all three mean the same thing: the default general-purpose
#     agent, holding every tool. That is a DENY below, not a fail-open. ---
target="$(field .tool_input.subagent_type)"

log_probe "tool_name=${tool_name} agent_type=${agent_type} target=${target:-none} raw_payload=$(printf '%s' "$input" | tr '\n' ' ')"

[ -z "$target" ] && deny_no_target

if agent_target_in "$target" "${allowed[@]}"; then
  exit 0
fi
deny "$target"
