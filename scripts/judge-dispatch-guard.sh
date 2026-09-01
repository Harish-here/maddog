#!/usr/bin/env bash
# judge-dispatch-guard.sh — PreToolUse guard restricting executor-judge's
# subagent dispatches to executor-fast-read and researcher only.
#
# Purpose: executor-judge's own file already says it may rent only
# executor-fast-read or researcher as hands, and never a hand that can make a
# change (it is fix-less by design — findings route back to the caller, it
# never repairs). That limit lives only as a sentence in the agent's own
# description today. This hook is the first attempt at making it structural.
#
# STATUS OF THE PAYLOAD SHAPE — CONFIRMED as of 2026-08-27 against captured
# payloads. A subagent dispatch always has .tool_name == "Agent". The target
# subagent is at .tool_input.subagent_type (plugin-namespaced, e.g.
# "maddog:executor-fast-read"). The calling subagent is at .agent_type, populated
# whenever a subagent makes the call (e.g. "general-purpose"), alongside
# .agent_id; .agent_type is absent entirely when the MAIN conversation
# dispatches, and that case must always allow.
#
# Like scripts/executor-guard.sh, this hook FAILS OPEN on genuine inability
# to inspect the payload: missing jq, empty stdin, malformed JSON, a
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
# Scope: executor-judge only. executor-lead also dispatches subagents and is
# deliberately left unrestricted here — that is a separate, already-decided
# design choice, not an oversight.
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
# Any failure to parse input, or absence of jq, ALLOWS the call — never
# block on our own inability to inspect the payload. A logging failure must
# never change the allow/deny outcome either.

set -uo pipefail

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
  local target="$1"
  local reason ctx reason_json ctx_json
  reason="Blocked by judge-dispatch-guard.sh: executor-judge attempted to dispatch '${target}'. executor-judge may only rent executor-fast-read or researcher as hands — renting any hand to make a change is not permitted for executor-judge at all."
  ctx="Blocked by judge-dispatch-guard.sh: this executor is fix-less by design and may only dispatch executor-fast-read or researcher, never a hand that changes anything. STOP and return STATUS: blocked to your caller with this reason — do not attempt the dispatch."
  reason_json="$(printf '%s' "$reason" | jq -Rs . 2>/dev/null)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs . 2>/dev/null)"
  if [ -n "$reason_json" ] && [ -n "$ctx_json" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  fi
  exit 0
}

# --- the no-subagent-type bypass: an Agent dispatch that names nothing
#     still runs an agent — the default general-purpose one, with every
#     tool including Write/Edit. Deny it as what it is, not as a gap. ---
deny_no_target() {
  local reason ctx reason_json ctx_json
  reason="Blocked by judge-dispatch-guard.sh: executor-judge attempted an Agent dispatch with no subagent_type named. Per the Agent tool contract, an absent, empty, or null subagent_type runs the default general-purpose agent, which holds every tool including Write and Edit. executor-judge may only rent executor-fast-read or researcher as hands."
  ctx="Blocked by judge-dispatch-guard.sh: this executor is fix-less by design and may only dispatch executor-fast-read or researcher, never a hand that changes anything. Naming no subagent_type is not an exemption — it dispatches the unrestricted default agent. STOP and return STATUS: blocked to your caller with this reason — do not attempt the dispatch."
  reason_json="$(printf '%s' "$reason" | jq -Rs . 2>/dev/null)"
  ctx_json="$(printf '%s' "$ctx" | jq -Rs . 2>/dev/null)"
  if [ -n "$reason_json" ] && [ -n "$ctx_json" ]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s,"additionalContext":%s}}\n' "$reason_json" "$ctx_json"
  fi
  exit 0
}

# --- read stdin once ---
input="$(cat 2>/dev/null)"

[ -z "$input" ] && exit 0

command -v jq >/dev/null 2>&1 || exit 0

# --- defensive: only ever act on a subagent dispatch tool call ---
tool_name="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)"
[ "$tool_name" = "Agent" ] || exit 0

# --- scope: only act for executor-judge (bare or plugin-namespaced) ---
agent_type="$(printf '%s' "$input" | jq -r '.agent_type // empty' 2>/dev/null)"
case "$agent_type" in
  executor-judge|*:executor-judge) : ;;
  *) exit 0 ;;
esac

# --- the target subagent. An absent key, an empty string, and JSON null
#     all collapse to "" via `// empty` — and for executor-judge dispatching
#     "Agent", all three mean the same thing: the default general-purpose
#     agent, holding every tool. That is a DENY below, not a fail-open. ---
target="$(printf '%s' "$input" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null)"

log_probe "tool_name=${tool_name} agent_type=${agent_type} target=${target:-none} raw_payload=$(printf '%s' "$input" | tr '\n' ' ')"

[ -z "$target" ] && deny_no_target

case "$target" in
  executor-fast-read|*:executor-fast-read) exit 0 ;;
  researcher|*:researcher) exit 0 ;;
esac

deny "$target"
