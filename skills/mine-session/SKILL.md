---
name: mine-session
argument-hint: [arm | distill]
description: >
  Extracts reusable collaboration patterns from a working session. Invoke
  with "arm" at the START of any session likely to involve iteration,
  correction, or unfamiliar ground — capture then runs as you work.
  Invoke with "distill" at session end to mine. Use when a session
  produced — or is expected to produce — surprise: corrections, rework,
  near-misses, an invented procedure, wasted effort. Do NOT use as a
  session summarizer or changelog — answer that directly, or hand it to a
  summarizing skill if one is installed; this extracts the way of
  working, never the work's content. Do NOT use to evaluate people —
  feedback on a person is theirs to ask for directly; this mines the
  collaboration only.
---

A session emits two products: the deliverable, and the way of working that
produced it. The first is captured by the repo; the second decays to zero
when the session ends unless it is externalized. This skill externalizes
it. Learning lives only where expectation and outcome diverged — mine
surprise, not activity.

SCOPE FENCE — four boundaries, none negotiable:
- Main thread only. Detours and tangents from the session's purpose are
  not weighed, however interesting.
- Process only. The work's content belongs to the project; only the way
  of working is extracted. A pattern that restates domain knowledge is
  not a pattern.
- Evidence without exposure. Every pattern cites the event it came from,
  but never quotes secrets, credentials, or sensitive content.
- Collaboration, not collaborators. No pattern assesses a person; the
  unit of analysis is the working relationship's moves, never the people
  making them.

THE LEDGER — two append-only files, outside the project tree so working
notes are never accidentally committed, under the user-level Claude
directory at ~/.claude/mining/<slug>/, where <slug> is the project's
absolute path, slugified. The user may name a different location when
invoking — an override, never a question the skill asks.
- capture.md — capture appends here and nothing else touches it. Arm
  opens the session with a marker line; capture and distill's
  reconstruction append stamped lines:
    SESSION START [YYYY-MM-DD hh:mm]
    [YYYY-MM-DD hh:mm] event — one line, concrete enough to relocate
    [YYYY-MM-DD hh:mm] (r) event — same, reconstructed at distill
  Lines above this session's SESSION START marker belong to earlier
  sessions: carried forward and attributed to their own stamp, never
  re-mined as the current session's.
- register.md — distill appends here and nothing else touches it: after
  processing, one watermark line
    PROCESSED THROUGH [YYYY-MM-DD hh:mm]
  and one entry per candidate
    - rung N | trigger -> move -> effect | evidence: [stamp of its line]
  Capture lines after the last watermark are unprocessed. THE REGISTER
  IS IDEMPOTENT ON EVIDENCE STAMP: the latest entry for a given evidence
  stamp is the candidate's state — an entry appended for a stamp that
  already appears supersedes the earlier one, and one stamp never counts
  twice toward recurrence, however the duplicate arrived. Nothing in
  either file is ever rewritten — concurrent sessions interleave appends
  recoverably instead of overwriting each other.

PHASE 1 — CAPTURE (armed by invoking with "arm").
Append one stamped line per surprise to capture.md, as it happens.
Capture is deliberately cheap: no classification (that is distill's
job) — the only care taken at capture time is the fence's redaction.
Stated plainly, because it is true everywhere: nothing can detect a
skipped capture line — continuous capture is a discipline, not an
enforceable rule, and distill's reconstruction pass exists precisely
because capture will sometimes fail. If armed late, say so: capture
covers only what remains reachable from here.

ORE CLASSES — five, applied at distill; each borrowed from a discipline
older than this skill — extend by discipline, not by anecdote:
1. CORRECTIONS — the principal redirects the agent (calibration
   training). The highest-grade ore: every correction marks a
   miscalibration.
2. FRICTION — rework, error-and-repair, near-misses (postmortem and
   incident-learning culture). Lessons live where things caught.
3. REPETITION — a move performed about three times by hand (the
   refactoring rule of three). A candidate for extraction or automation.
4. DEAD SPEND — effort that changed nothing (lean waste). Ore for what
   to REMOVE from the process, not add.
5. CONFIRMED WINS — a move that worked and would decay unwritten.
   Survivorship-prone: this class needs the strictest evidence.

PHASE 2 — DISTILL (invoked with "distill", at session end or later).
- Reconstruct first: sweep the reachable context for surprises not
  already in capture.md, whether capture ran or not — armed capture is
  never assumed complete. Append each reconstructed surprise to
  capture.md as an (r) line before going further, so the watermark
  covers it and no later distill re-mines it. Reconstruction is weaker
  than capture at the moment, and the report says which mode produced
  each line.
- Then gate: zero captured, zero reconstructible, AND no carried-forward
  lines from earlier sessions means "nothing to mine" — report exactly
  that and stop. An empty mine is a finding, not a failure.
- Process carried-forward lines first, attributed to their own sessions.
- Bind: every candidate must point at its concrete event. A pattern that
  cannot cite its evidence is not extracted, whatever it claims.
- Shape: a keepable pattern is a triple — TRIGGER (the situation you
  would recognize next time), MOVE (what to do), EFFECT (what changes).
  Missing a trigger, it is a platitude; missing a move, an observation;
  missing an effect, unfalsifiable. All three or it stays in the ground.
- Route: write each pattern to the strongest available home that is
  DURABLE (survives the session), DISCOVERABLE (surfaces when its
  trigger occurs, not by luck), and BINDING (something re-invokes it —
  a tool, a habit, a test, a person). Instruction files, persistent
  memory, a skill, a hook, a test are all homes when present; the floor
  that always exists is a user-owned file, and routing there says so
  rather than pretending it binds.
- Promote by recurrence, never by enthusiasm: observation → recorded
  candidate (with evidence) → confirmed (recurred in a later session) →
  institutionalized (moved to a stronger, more binding home). The
  register carries each candidate's rung; distill appends an updated
  entry for the ones this session confirmed. One session is a
  hypothesis; doctrine takes three.
- Where the installation has a gated authoring path for load-bearing
  instruction text, institutionalization flows through it; absent one,
  institutionalization means writing the pattern into the strongest home
  available and saying plainly that no gate reviewed it. Where a second
  intelligence is available, split extraction from evaluation. Neither
  is assumed: evidence-binding is the portable floor against the miner
  grading its own session.

OUTPUT — the mining report, and nothing else changes hands:
  MINED: per pattern — class, evidence event, capture or reconstruction,
    trigger/move/effect, home written, ladder rung.
  LEFT IN THE GROUND: candidates not extracted, each with the leg it
    failed (no evidence, no trigger, no move, no effect, out of scope).
  LEDGER: where it lives, the new watermark, what carries forward.
Report honestly when the session was rich in activity and poor in
surprise — a productive session with nothing to mine is common, and
saying so is cheaper than manufacturing insight.
