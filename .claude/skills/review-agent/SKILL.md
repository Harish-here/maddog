---
name: review-agent
description: >
  Use when an agent definition, routing description, or always-resident skill
  text needs a design review before it ships — new agent files, rewrites to
  an existing agent's body, or any change to a frontmatter description.
---

1. Assemble the evidence set: the target file(s); every file in `agents/`;
   every `skills/*/SKILL.md` plus its `references/`; this skill's own
   `references/agent-template.md`; `README.md`; `CLAUDE.md`;
   `.claude-plugin/*.json`; `install.sh`; and the binding design artifact
   (spec, decision ledger, or approved proposal) for this change. If none
   exists, say so in the dispatch — the checklist downgrades its spec-fidelity
   dimension to NOT EXECUTED rather than trusting the file's own claims about
   itself.
2. Dispatch ONE top-tier reviewer at a design gate — prefer this plugin's own
   gate-verdict agent if the family is installed, otherwise any top-tier
   general reviewer — with a premortem stance, the evidence list, and
   `references/checklist.md` as the review contract and `references/agent-template.md`
   as its structural reference. Do not name any agent's internal mode taxonomy
   in the dispatch.
3. Triage findings yourself. Fold accepted fixes via a dispatched executor.
   Convert any finding worth keeping permanently into an eval fixture
   (prohibitions survive evals better than obligations).

Nothing here is force-loaded; the checklist is referenced by path in the
dispatch, not inlined.
