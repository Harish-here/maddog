---
name: advisor-mode
description: Classify a session's work by judgment shape, delegate it within authority boundaries, and accept returned work. Use when beginning a session that will delegate work.
---

Read and follow the shared [Advisor contract](../../../skills/advisor-mode/SKILL.md), ignoring its Claude-only frontmatter.

For every named hand, create a Codex subagent using the matching definition in
`.codex/agents/`. State the task boundary, authority, required evidence, and
acceptance bar in the delegation. Use sequential delegations where later work
depends on an earlier result; run only independent read work in parallel.
