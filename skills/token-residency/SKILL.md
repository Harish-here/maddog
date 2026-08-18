---
name: token-residency
description: >
  Classify any artifact agents will load — skill bodies, briefs,
  blueprints, memory files, ledgers, dispatch prompts and returns —
  by CONTEXT RESIDENCY, then author it under that class's template,
  budget, and laws. Use BEFORE authoring such an artifact or
  specifying a dispatch's OUTPUT FORMAT. This skill prices and
  structures; it never gates or reviews. Do NOT use to review or
  judge existing text — a review whose deliverable is the verdict is
  review-agent, and gated authoring of load-bearing text is
  author-agent.
---

One axis prices what a multi-agent system authors for a context: how
long the tokens stay resident, and in whose context. Name the class
first; template, budget, and prohibitions follow. Full doctrine and
evidence: references/model.md, references/evidence.md.

| Class | Residency | Author with |
|---|---|---|
| HOT | loaded every session by standing machinery (CLAUDE.md, memory index, frontmatter descriptions) | references/hot.md |
| WARM | loaded per dispatch or reference (skill bodies, briefs, specs, research tables, living state files) | references/warm.md |
| COLD | write-once, verbatim, never rewritten (filed rulings, post-mortems, transcripts) | references/cold.md |
| CHANNEL | resident in the orchestrator all session (dispatch prompts, returns, the session ledger) | references/channel.md |

HUMAN is an AUDIENCE OVERLAY, not a class: where a person is the
primary audience, readability governs form; the class still prices
substance — file the bulk, present the digest. A surface whose
purpose is agent loading never takes the overlay; a dual-read
artifact (a README agents also consult) stays overlaid per
precedence (2). Where the overlay applies, agent-reader laws — no
narrative history, IDs over prose — are SUSPENDED, not merely
softened: a human doc's narrative can be its load-bearing substance.

PRECEDENCE: (1) shipped law and documented invariants beat class
laws; (2) dual-audience artifacts split surfaces before blending
laws — never cut a human doc to a WARM ceiling; (3) an artifact may
carry a NAMED CONTRACT that replaces class-generic law — a contract
lives beside the law it extends and ships only where that law ships.

PROCEDURE:
1. In scope? The unit must enter a context — class attaches to the
   unit, never the whole file.
2. Name the class by who loads it, how often, for how long; overlay
   if a person is the primary audience; named-contract artifacts
   follow their contract.
3. Load the class's reference; author under its template and laws.
4. On class change, re-price: inline content becomes a pointer.
5. SHIP RULE (a ship-time step, the mover's, not the author's): a
   shipped file may cite only what
   ships with it — replace unconditional session-scoped citations
   with self-contained statements or in-repo pointers; a citation
   guarded by an existence check is the sanctioned fallback, not a
   violation. Any compact rendering keeps the carve-out or drops the
   whole step.
