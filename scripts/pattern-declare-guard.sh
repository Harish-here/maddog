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
# payload ALLOWS. A missing jq denies only a payload whose raw text names one of the
# two agent types; every other caller ALLOWS.
#
# State: one empty marker file per agent_id under ${TMPDIR:-/tmp}/maddog-pattern-declare/.
# The marker is created on the agent's first call, whatever the decision, so a
# second call never reaches the check.

set -uo pipefail

deny() {
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"write PATTERNS first, then repeat the call","additionalContext":"Blocked by pattern-declare-guard.sh: your first message must hold a PATTERNS: line before your first tool call. Write it now (PATTERNS: <NAME>[, <NAME>], then one line per pattern that has a law), then repeat this call."}}'
  exit 0
}

input="$(cat 2>/dev/null)"
[ -z "$input" ] && exit 0
if ! command -v jq >/dev/null 2>&1; then
  # Without jq the payload cannot be parsed. Deny a call whose raw input names a guarded
  # agent type (static JSON, no jq); allow every other caller, e.g. the main session.
  jq_missing_re='"agent_type"[[:space:]]*:[[:space:]]*"([^"]*:)?(executor-fast|executor-fast-read)"'
  if [[ "$input" =~ $jq_missing_re ]]; then
    printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"The maddog guards require jq and it is not installed, so this call was denied rather than allowed unchecked. Install jq, then retry.","additionalContext":"Blocked by pattern-declare-guard.sh: jq is missing. STOP and return blocked to your caller, asking them to install jq - do not attempt the call."}}'
  fi
  exit 0
fi

field() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null; }

case "$(field .agent_type)" in
  executor-fast|*:executor-fast|executor-fast-read|*:executor-fast-read) : ;;
  *) exit 0 ;;
esac

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
