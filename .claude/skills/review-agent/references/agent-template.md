# Agent template — spine and dimension overlays

Guidance and enforcement for authoring agent files in this repo, and the review
contract's structural reference. Every agent file is reviewed against the SPINE
plus exactly ONE dimension overlay. An agent that mixes dimensions — an
execution agent with a pipeline position, a persona agent taking arbitrary task
shapes — is itself a load-bearing finding, not a style note.

## SPINE — every agent file, both dimensions

- Frontmatter: `name`; `description` following the five slots in the review
  checklist's Dimension 2 (that block is the single home for description rules
  — do not restate them here or anywhere else); `tools` as the MINIMAL set the
  role needs. Structural invariants are enforced by tool omission, never by
  instruction — a prohibition the agent cannot violate beats one it is asked to
  honour (the lead holds no Write/Edit; the judge cannot fix by construction).
- The body opens with an identity stance ("You are X. You were handed ...")
  and closes with a verbatim return contract ("Return exactly: STATUS: ...")
  that includes a NOTES field. Nothing follows the return contract.
- The body never restates the frontmatter description — the registry injects
  it; a stale copy teaches the wrong routing.
- Agents are defined by judgment class or discipline role, never by model
  name. Intelligence is budgeted by the caller at dispatch; a model name used
  as identity inside the body is a defect.
- Laws in one file must not contradict each other: a prohibition beats an
  obligation in practice, so an obligation cancelled by a prohibition is a
  defect even when never stated as an exception. Where two laws CAN collide on
  one input, the file pre-resolves the collision explicitly — a carve-out
  ("EXTRACT is the exception...") or a precedence statement ("the mode law
  outranks this one").

## DIMENSION TABLE

| Dimension | Identity | Members | Signature machinery |
|---|---|---|---|
| EXECUTION | a judgment class — what shape of task it takes | executor-fast, executor-smart, executor-lead, executor-judge, researcher | classify-first + MODE blocks (takes / output / LAW / E.g.) |
| PERSONA | a discipline role at a fixed pipeline stage | product-pm, product-ux, product-be, product-ui, product-qa | charter + artifact contract + pipeline position |

Every agent declares exactly one dimension by its structure. New dimensions are
added to this table deliberately, never discovered by drift.

## EXECUTION overlay

Body order: dispatch contract → classify-first preamble → numbered MODES →
cross-mode laws → return contract.

- The classify-first preamble states that the caller sees only the frontmatter
  description, so classification is always the agent's own; a mode named in a
  prompt is a hint from someone who has not read the file.
- Each MODE block: `NAME — takes: ... Output: ... LAW: NAMED PRINCIPLE
  (attribution) — statement. E.g. worked example.` Every mode has all four
  parts; a law without an example makes the file's own framing false.
- Modes are derived from real dispatch history; add one only when a genuine
  usage cluster demands it.
- A single-shape EXECUTION agent (one fixed task shape — researcher) collapses
  the machinery: no classify-first, no MODE blocks; its body is the one
  shape's caps and prohibitions plus the return contract. It remains
  EXECUTION — its identity is still a task shape, never a role.

### Law selection rules

1. The law must govern the mode's DOMINANT FAILURE SHAPE as the principle is
   canonically stated. Before borrowing a named principle, check its native
   domain and documented misapplications; a name-level vibe match is a defect
   (the family has already shipped one: a fence law spent on a contradiction
   case another law owned).
2. Strong form: a bright-line prohibition with a mechanically observable
   violation, or a named seductive wrong move. Obligations degrade under
   pressure; prohibitions hold. A comparative ("X beats Y") is the weakest
   form and never carries a law alone.
3. Tier fit: the law must be executable at the mode's tier. A cheap-tier law
   is checkable without discretion; only a top-tier law may demand judgment.
   A trigger the tier cannot help but fire ("any judgment call") makes the
   rule discretionary — reference the task's boundary, not the agent's
   psychology.
4. Coined laws (no external source) are legal and exempt from rule 1, but not
   from rules 2-3. A family-shared coined law is verbatim-identical in every
   file that carries it — edit all copies or none.
5. Cross-file reuse of one principle at two tiers is legal when the textual
   delta encodes the tier difference (fast reports what it cannot reproduce;
   smart repairs until reproduction stops). Same-file reuse is not.

### Example (E.g.) rules

6. The example exercises the LAW's specific tension, not merely the mode.
   Substitution test: an example that reads the same under a different law
   fails. It shows the seductive wrong move at the moment it is tempting —
   never a law restated in narrative voice, never an unbroken success.
7. Normative content lives in the law; the example illustrates it. A rule
   that exists only inside an example is misfiled; a law sentence duplicated
   by its own example is weight without work.
8. Delegation-marker test: if the agent must delegate hands work, the example
   depicts delegation UNLESS the enclosing mode body already states it — an
   example is the mode's sole local carrier of any rule the body omits.
9. A law is enforced through the return artifact, never through mandated
   reasoning: prefer a field only law-compliant work can fill over a
   thinking ritual. A law with no artifact tooth is a Dimension 5 finding.
10. Example difficulty matches the tier that will read it: the wrong move
    shown must be tempting AT that tier — bright-line for cheap tiers, a
    defensible-looking judgment call for top tiers. An example whose wrong
    move a cheaper tier would also never make teaches the top tier nothing.

## PERSONA overlay

Body order: identity stance naming the handed artifacts → recon (breadth
delegated with output caps, depth the agent's own) → charter/principles →
ARTIFACT CONTRACT → WRITE BOUNDARY → return contract.

- Scope is ONE feature. The stance names the upstream artifacts the stage
  requires; missing artifacts are a hard stop, not an improvisation license.
- The ARTIFACT CONTRACT names the exact output file and its ordered sections.
  The agent produces that artifact and nothing else; precision is judged by
  whether a downstream agent can consume it with zero judgment.
- WRITE BOUNDARY confines Write/Edit to the artifact tree (docs/product/**),
  stated even though tools allow more — here the boundary is a path, which
  tool restriction cannot express.
- Governance is by charter (baked-in standards applied as design moves), not
  per-task laws — the pipeline already classified the task. Stage GATES live
  in the orchestrator skill, never in the agent file.
- The description carries the pipeline-position slot (stage order, required
  inputs, downstream consumer) — the one slot an EXECUTION description must
  never have. A verification-role persona (qa) may replace recon with a
  verification protocol and add role-specific disciplines; its read-only
  invariant is stated absolutely and backed by tool omission where possible.
