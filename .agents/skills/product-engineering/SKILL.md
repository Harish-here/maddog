---
name: product-engineering
description: Orchestrate the full PM, UX, backend, UI, implementation, and QA pipeline for one feature. Do not use for small tweaks or isolated bug fixes.
---

Read and follow the shared [product-engineering contract](../../../skills/product-engineering/SKILL.md), ignoring its Claude-only frontmatter.

Use the matching `.codex/agents/product-*.toml` agent for each stage. Replace `SendMessage` with a new, sequential subagent delegation that names the artifact directory and all prior artifact paths. Pass questions to the user yourself and resume by delegating a new stage agent with the persisted `.state.md`; do not assume a Claude-specific foreground or messaging tool exists.
