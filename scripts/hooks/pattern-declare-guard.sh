#!/usr/bin/env bash
# pattern-declare-guard.sh — PreToolUse guard for executor-fast and executor-fast-read.
#
# Purpose: both agents must write a `PATTERNS:` line in their first message,
# before their first tool call. Instruction text alone does not make that
# happen every time, so this hook refuses a first call that has no such line.
#
# Rule, first tool call only:
#   - `PATTERNS:` in the subagent's own assistant text -> allow. The text counts
#     anywhere in the agent's own text, with any markup around it. The
#     scorer's check 1 (tests/harness/core/agent_score.py) applies the same rule.
#   - absent -> deny once, per agent_id, with a reason telling it to write the
#     line and repeat the call.
#   - anything we cannot read or inspect -> allow. This guard never denies twice
#     and never blocks on its own inability to look.
# Whether the first call MATCHES what the line declared is not checked here;
# the tests in tests/agents/ check that.
#
# Where the evidence is: the subagent's transcript is
#   dirname(transcript_path)/<session_id>/subagents/agent-<agent_id>.jsonl
# and at the first PreToolUse its text entry is already on disk.
#
# Wiring: plugin-level hooks/hooks.json, matcher on the read/write/search/shell
# tools. That wiring is session-wide, so scope is enforced here: only calls
# whose payload agent_type is executor-fast or executor-fast-read (bare or
# plugin-namespaced) are inspected. The main conversation has no agent_id and
# is always allowed.
#
# Protocol: read the PreToolUse JSON payload on stdin; print nothing and exit 0
# to ALLOW, or print a hookSpecificOutput deny JSON and exit 0 to DENY (the JSON
# form gives the model the reason; exit 2 would not). Hooks fail open: an unreadable
# payload ALLOWS. A missing jq, or a lib that fails to load, denies only a payload whose
# raw text names one of the two agent types; every other caller ALLOWS.
#
# State: one empty marker file per agent_id under ${TMPDIR:-/tmp}/maddog-pattern-declare/.
# The marker is created on the agent's first call, whatever the decision, so a
# second call never reaches the check.

set -uo pipefail

HOOK_NAME="${BASH_SOURCE[0]##*/}"
GUARDED_AGENTS='executor-fast|executor-fast-read'
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
  msg_git_option msg_unreadable msg_publish msg_shell msg_write_cmd msg_interpreter
  msg_git_write _msg_tag_allowed msg_tag_flag msg_tag_name
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

deny() {
  emit_deny static "$MSG_PATTERN_REASON" "$MSG_PATTERN_CONTEXT"
  exit 0
}

hook_start "$HOOK_NAME" "$GUARDED_AGENTS"

agent_is "$(field .agent_type)" executor-fast executor-fast-read || exit 0

agent_id="$(field .agent_id)"
session_id="$(field .session_id)"
transcript="$(field .transcript_path)"
[ -n "$agent_id" ] && [ -n "$session_id" ] && [ -n "$transcript" ] || exit 0
# Both ids become path parts below: refuse anything but plain id characters.
case "$agent_id$session_id" in *[!A-Za-z0-9_-]*) exit 0 ;; esac

marker_dir="${TMPDIR:-/tmp}/maddog-pattern-declare"
marker="$marker_dir/$agent_id"
mkdir -p "$marker_dir" 2>/dev/null || exit 0
# Create the marker atomically: noclobber makes the redirect fail if the file exists. Of
# several calls racing for one agent_id's first turn, exactly one creates it and goes on to
# check; the rest (and every later call) find it and allow. A failure to create allows too.
( set -C; : > "$marker" ) 2>/dev/null || exit 0

sub="$(dirname "$transcript")/$session_id/subagents/agent-$agent_id.jsonl"
[ -r "$sub" ] || exit 0

# Only the agent's own assistant text counts: the dispatch prompt may quote "PATTERNS:".
text="$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text' "$sub" 2>/dev/null)" || exit 0
# One rule, shared with the scorer (tests/harness/core/agent_score.py, check 1): the text
# PATTERNS: anywhere in the agent's own text. Case matters; markup around it does not.
case "$text" in
  *PATTERNS:*) exit 0 ;;
esac
deny
