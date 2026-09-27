# Trial findings — 2026-09-27

SDK: claude-agent-sdk 0.2.160  (Task 2 pins exactly this version)

| # | Condition | Result | Evidence (one line from out.txt) |
|---|---|---|---|
| 1 | Only this plugin loads, no user settings | PASS (see note) | `INIT other plugins present: [{'name': 'agents-md', 'path': 'builtin', 'source': 'agents-md@builtin'}, {'name': 'telemetry', 'path': 'builtin', 'source': 'telemetry@builtin'}]` — non-empty, but both entries are CLI builtins (`source: *@builtin`), not declared by the maddog plugin manifest and not a user-configured plugin; no `superpowers` or other user plugin appears, so the user's settings did not load. |
| 2 | advisor-mode slash command and executor agents present | PASS | `INIT slash has advisor-mode: True`; `INIT agents: ['maddog:executor-fast', 'maddog:executor-fast-read', 'maddog:executor-judge', 'maddog:executor-lead', 'maddog:executor-smart', ...]` |
| 3 | PreToolUse deny stops the helper before it runs | PASS | `TOOL_USE Agent {'subagent_type': 'maddog:executor-fast-read', ...} parent: None` followed by `TOOL_RESULT is_error: True PreToolUse:Agent hook error: maddog-test: stopped here by the test harness`; no later `TOOL_USE` line in session A carries a non-empty `parent`. |
| 4 | Grep and Glob calls visible in the stream | PASS in spirit (see note) | `TOOL_USE ToolSearch {'query': 'select:Grep,Glob', 'max_results': 5} parent: None` then `TOOL_RESULT is_error: None No matching deferred tools found`; the model fell back to `TOOL_USE Bash {'command': "grep -r 'def' . 2>/dev/null | head -20", ...}` and `TOOL_USE Bash {'command': "find . -name '*.txt' -type f", ...}`. No `TOOL_USE Grep` or `TOOL_USE Glob` line appears anywhere in session C. |
| 5 | Sessions end cleanly | PASS | `RESULT success turns: 2` (session A+B); `RESULT success turns: 4` (session C) |
| 6 | Sessions authenticate with no settings loaded | PASS | ANTHROPIC_API_KEY set: no — both sessions returned `RESULT success` with no authentication or login error. |

Handoff tool name(s) seen: `Agent` (no `Task` tool use observed in this trial).
subagent_type format: a plain string field on the tool-use input, e.g. `subagent_type: 'maddog:executor-fast-read'` (plugin name, colon, agent name).
Option or import names that differed from the plan: none. All imports (`ClaudeSDKClient`, `ClaudeAgentOptions`, `HookMatcher`, `AssistantMessage`, `UserMessage`, `SystemMessage`, `ResultMessage`, `ToolUseBlock`, `ToolResultBlock`) and all options used (`model`, `cwd`, `plugins`, `setting_sources`, `permission_mode`, `max_turns`, `hooks`) exist unchanged in `claude_agent_sdk` 0.2.160 (checked against `tests/.venv/lib/python3.13/site-packages/claude_agent_sdk/types.py`); the trial script ran verbatim as written in the plan.

## Maintainer rulings (2026-09-27)

- Condition 4 passes in spirit. Grep and Glob do not exist in Claude Code CLI 2.1.283 (the SDK's bundled CLI; its init tool list has neither). Searches go through Bash (`grep`, `find`), are visible in the stream, and are recorded as `command` events.
- Condition 1 accepted. The CLI-bundled `agents-md@builtin` and `telemetry@builtin` plugins load regardless of settings. Isolation means no user plugins, settings, or hooks; none loaded.
- ToolSearch is a live tool in these sessions. No scoring change: the plan's code is built as written, and the Task 10 live run shows whether a ToolSearch call before the handoff spends the advisor's one allowed call.
