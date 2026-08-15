---
name: author-agent
description: >
  Runs the GATED AUTHORING loop for load-bearing instruction text in this
  repo: creating a new agent from the template, or overhauling existing
  agents, skills, and reference contracts. Use when the text is reused and
  load-bearing, its defects are silent in production, and the author is an
  interested party — the loop forces an independent gate between authoring
  and applying. Do NOT use for one-off or low-stakes text — edit that
  directly. Do NOT use when nothing is being authored — reviewing existing
  text alone is review-agent.
---

0. COST/VALUE LINE. Before any authoring, one sentence to the user: what
   this thread will cost (gate rounds × dispatches, roughly) and what it
   buys — and name the step-8 closing report as the thread's deliverable.
   Proceed on their green light. A new thread opened mid-loop, or a rework
   round beyond the count the line quoted, gets its own line — scope
   ratchets by decision, never by drift.

1. MODE.
   - CREATE (agent): classify the dimension FIRST from the table in
     `.claude/skills/review-agent/references/agent-template.md` — an agent
     mixing dimensions is stillborn, not fixable later. Author the
     description against the checklist's Dimension 2 slots (the checklist
     is the template's sibling, `references/checklist.md`) and the body
     against the matching overlay — for EXECUTION, laws per rules 1-5,
     examples per 6-8 and 10, artifact tooth per 9; for PERSONA, the
     overlay's element order (charter, ARTIFACT CONTRACT, WRITE BOUNDARY,
     pipeline-position slot). Before gating, run the routing partition
     against every existing description yourself: the newcomer must not
     double-match a neighbor's shape or monopolize a keyword. A new agent
     is unreachable until named: the by-name references that must learn
     it — or that forward to it — (routing tables, plugin manifest version
     bump when the shipped set changes) ride in the packet as their own
     items, ordered so a forwarding reference lands only after the file it
     names exists.
   - CREATE (skill or reference): no template contract exists for
     non-agent text, and the checklist's own Scope excludes references
     that are not force-loaded — name in the packet exactly which
     dimensions you authored against and which do not apply, so the gate
     rules against a stated contract rather than inferring one.
   - OVERHAUL: findings first. Run the review-agent gate (or a scoped
     sweep) on the existing text; author fixes only against accepted
     findings — never freestyle rewrites of text nobody indicted.

2. PACKET. All verbatim texts in one scratchpad file with item IDs
   (P1..Pn). The packet opens with the step-0 line and the user's green
   light — the gate refuses a headerless packet. Each item names its
   target file and either its anchor plus the replacement text (OVERHAUL)
   or "new file — full contents follow" (CREATE), plus the finding or
   template rule it answers. Item headers and markers are packet
   scaffolding, never file content. The packet is the single authority —
   apply dispatches read it, never chat memory.

3. GATE. Dispatch ONE top-tier judge per the review-agent procedure:
   evidence set = target files (existing ones; a CREATE item's evidence is
   the packet contents plus the family it joins), the full agent family,
   the checklist, the agent template, the packet, and any binding
   artifacts. Verdict per item: APPLY / APPLY-WITH-CUTS / REWORK, findings
   with failure scenarios, free token cuts named verbatim. The judge
   rules; it never authors replacement text.

4. REWORK LOOP. Fold the named cuts exactly — no more, no less. Rework
   each REWORK per its finding. Re-gate ONLY the changed items, with the
   SAME judge instance where it is still reachable — its earlier
   precedents bind, and it audits the cut-folding. If that instance is
   gone, dispatch a fresh judge and supply every prior ruling verbatim; a
   fresh judge with no precedents supplied is not a re-gate. Repeat until
   every item clears. The author never self-clears an item, whatever the
   round count.

5. USER APPROVAL. Final verbatim texts on screen, referenced by item ID,
   each item citing the gate verdict that cleared it — an item with no
   verdict behind it is visibly unapproved. Instruction-file targets
   (CLAUDE.md and kin) always show exact before/after — approval of a
   category is not approval of a text.

6. APPLY. Fast-tier dispatches, exact texts from the packet, no two
   concurrent dispatches writing one path, and packet-stated apply
   ordering honored. Every dispatch states verbatim: the working tree's
   uncommitted changes are the deliverable; git checkout, restore, stash,
   and clean are forbidden; DONE-WHENs describe the dispatch's own delta
   ("your edits touch only X"), never tree state.

7. VERIFY.
   (a) placement/fidelity/standard — every OVERHAUL item at its anchor,
       every CREATE item's file existing in full, whitespace-normalized
       text match against the packet, indentation and wrap per the file's
       own (or its family's) convention;
   (b) behavior probes — for any description added or changed,
       fresh-session routing probes (`claude -p`; the live session's
       registry is a stale snapshot): the happy path plus each moved
       boundary in both directions — on a CREATE the moved boundaries are
       the neighbors'. A CREATE also probes the new agent on one
       representative task. If a probe cannot run in this environment,
       the item is recorded UNVERIFIED — never silently skipped;
   (c) fixtures — where a fixture home exists (evals/<agent>.json; the
       runner's file list must learn a CREATEd agent's fixture), keeper
       findings become eval fixtures. Where no home exists, record the
       finding as named fixture-debt instead of pretending.

8. CLOSING REPORT. Per item: the verdict ID that cleared it, its
   placement result, its probe output or UNVERIFIED marker, its fixture
   or fixture-debt entry. An item missing any of the four is not closed,
   and the report says so.
