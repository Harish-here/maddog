# maddog for Codex

This repository ships a Claude plugin and a Codex adaptation. Keep the shared
role and workflow contracts in `agents/` and `skills/` runtime-neutral; place
Codex mechanics only in `.codex/`, `.agents/`, and this file.

## Use in Codex

- Codex loads the project skills from `.agents/skills/` and custom subagents
  from `.codex/agents/`.
- Use a skill by name (for example, `$advisor-mode`). Its Codex entrypoint
  points to the shared contract and supplies any required runtime adaptation.
- Delegate with the named Codex subagent from `.codex/agents/`. Preserve the
  role's authority boundary, sandbox mode, and output contract.
- Codex subagents inherit the parent session's approval policy. Do not claim
  that approvals are unavailable; request or report them according to the
  active session policy.

## Invariants

- `executor-fast-read`, `executor-judge`, and `executor-lead` run read-only.
  They must never edit or execute state-changing commands.
- Product planning and QA agents may write only their stated
  `docs/product/**` artifacts. They must not edit application code unless
  their role explicitly owns implementation.
- The shared `agents/` and `skills/` prose must not name Codex-only APIs.
  Runtime-specific details belong in the Codex adapters.

## Repository Maintenance

There is no compiled artifact or conventional test suite. Validate changed
skill frontmatter and agent TOML, then review the relevant contracts for
runtime-specific wording and preserved authority boundaries.
