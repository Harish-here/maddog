# The Ledger — law and contract

Read with absent.md when the user leaves. SKILL.md holds when the
ledger opens; this file holds how it is written and closed.

## Law

- WHEN: append only at a decision event — a decision closes (user or
  in-boundary), an authorization is granted or denied, a binding or
  degradation is recorded, a deviation is accepted. Decisions closed by
  one event (one ruling triaged, one user batch, one return accepted)
  share one entry. A decision that opens gets one line in the ledger's
  single OPEN section. Dispatch, return, acceptance, verification:
  process, never entries.
- WHAT: one entry = one decision event — the closed decision(s), who
  closed them, a one-line rationale and a one-line what-would-reopen-it
  each (the decider's basis, never the citation's content restated),
  citations (file:line, artifact path, ruling ID). The entry alone must
  let a later session stand by the decision. Per-item dispositions
  belong in the artifact they rework, each named to the finding it
  answers — the entry carries that artifact's revision pointer, never
  the item list. An obligation created by a decision rides in its
  entry; a free-standing reminder is an OPEN line or it is nothing.
  Entries are advisor-authored even when a hand applies the write.
- CLOSING an open item: append its closing entry first, then delete the
  OPEN line — history lives in entries; OPEN is an index. A discharged
  reminder just loses its line, no entry. An "empty" ledger at CLOSE
  means no entries, never a pruned OPEN section.
- PROHIBITIONS: never rewrite a filed entry; never restate filed
  content — rulings, models, transcripts enter as pointers, exactly as
  ACCEPTANCE files them; never cite a path the returning user or a
  fresh session cannot open; never record that a law was followed —
  CLOSE is discharged by the surfacing batch and the memory write,
  never by an entry asserting compliance.

## Contract (repo companion to the Token-Residency Model, rev 4)

Extends the Law above. Home: skills/advisor-mode/references/. The
ledger is session-scoped orchestrator state; this contract governs it
in place of any class-generic token law. Provenance: distilled from an
adversarial design review of a withdrawn ledger redesign.

- PRECEDENCE: this contract only excludes lines; it never admits a
  line the Law prohibits. On any conflict the Law section wins.
  (Lesson: a session once restated a filed ruling's content in a
  ledger rationale — the Law's "never restate filed content" already
  forbade it, and this contract would not have blessed it either.)
- JURISDICTION: fields and lines the Law REQUIRES — rationale,
  what-would-reopen, OPEN lines — are outside the admission test
  entirely: mandated, therefore never emptied or excluded by economy.
  The test governs discretionary content only.
- THE TEST, prohibition-shaped: a discretionary line is dead weight
  and never written when every reader surface that will carry it can
  derive it. The three reader surfaces, with holdings:
  - R1 — a future advisor reading the FULL ledger; holds the
    governing skill and the repo.
  - R2 — the returning user reading the SURFACING BATCH only, a view
    carrying closed decisions, obligations created, and rulings
    required; ledger-body detail never reaches R2, so R2 admits
    nothing into the body.
  - R3 — a fresh post-death session reading the durable ledger and
    resume record; holds the durable paths and the repo, never the
    session scratchpad. A line admitted for R3 may cite only paths R3
    can open — a citation the reader cannot open is not a citation
    (absent.md's law, imported as this contract's constraint).
- BINDING RECORD: the statement made to the user at session open
  always NAMES each routed class's hand. Kept is exempt. Hands are
  never derivable, the skill deliberately names none. An undegraded bind fits ONE line
  carrying all pairs, each gate-critical invariant as verified (the
  adversarial hand's absence of Write/Edit), and the reopen condition;
  DEGRADED, UNBOUND, and shared-hand tier-collapse each take their own
  line naming the consequence. This format SUPPLEMENTS the shipped
  element list (hand, satisfied invariants, degradations); no element
  of that list may be dropped. When a ledger opens, the statement is
  copied in unchanged as its first entry.
- ROUTING PRECONDITION: the routing gate keys on the statement NAMING
  every routed class's hand (kept is exempt, see SKILL.md Bind), not
  on its mere existence — a prohibition at the consumer, never an
  obligation on the author.
- EXCHANGE TEST: every line added to instruction text that agents
  load is tested at its class's load frequency — a frontmatter
  description pays every session, a skill body every invocation, a
  per-dispatch reference every load, and a reference can load many
  times per session — and bought only where the recurring saving
  exceeds the recurring
  cost. Exempt only what this contract or the Law mandates —
  exemption by SOURCE, never by declared motive; a needed line that
  saves nothing earns its place by becoming mandated (a decision),
  never by an author's label.

Known residuals, self-contained:
- Rationale fields: the Law's "never the citation's content
  restated" can collide with an honest norm-derived rationale; this
  contract does not resolve it — an open question for the next
  advisor-mode amendment.
- The bloat instance that motivated this contract was user-witnessed;
  its cited artifact was never verified — undetermined whether that
  ledger was rewritten or the citation was stale.
