# Token-Residency Model (canonical, rev 6)

One axis prices what a multi-agent system AUTHORS for a context: how
long the tokens stay resident, and in whose context. Name the class
first; template, budget, and prohibitions follow.

SCOPE: context-borne artifacts and messages the system authors —
anything whose tokens enter an LLM context. Class attaches to the
context-entering UNIT, never the whole file: a plugin manifest's
router-surfaced description is HOT while its machine wiring is out of
scope; an eval fixture's prompt, setup file bodies, and rubric enter
contexts and are priced as the dispatch prompts and reference material
they are, while its ids and harness wiring are not; a workflow's
meta.whenToUse is WARM-in-place. Out of scope: units no context ever
loads (lockfiles, manifest wiring, fixture scaffolding) — their
constraints come from their consumers — and user-authored turns,
which the system does not author. The classes and laws are
system-generic: this repo's artifacts appear as instances, never as
the definition — a consumer maps their own artifacts by residency
alone.

## The four residency classes

| Class | Residency | Instances |
|---|---|---|
| HOT | loaded every session by standing machinery | CLAUDE.md, memory index, frontmatter descriptions |
| WARM | loaded per dispatch or reference | SKILL.md bodies, briefs, specs, blueprints, research tables, living state artifacts |
| COLD | write-once, verbatim, never rewritten | filed rulings, post-mortems, transcripts |
| CHANNEL | resident in the orchestrator for the whole session | dispatch prompts, subagent returns, the session ledger |

HUMAN is not a fifth residency class — it is an AUDIENCE OVERLAY on
any class. It attaches only where a person is the PRIMARY audience —
the surface exists to be read by them. A surface whose PURPOSE is
agent loading (a skill body, a brief) never takes it; a dual-read
artifact (a README people read that agents also consult) stays
overlaid, priced per precedence rule 2; a maintainer reading source
is not an audience. Where it applies,
readability governs the form at the point of contact: outcome first,
complete sentences, structure kept. The carrier's residency class
still prices the substance: file the bulk, present the digest. A
surfacing message to a returning user is CHANNEL-priced with the
HUMAN overlay — finding IDs and decisions, presented readably,
against the filed record. Reports, READMEs, and handover prose carry
the overlay. Class laws that assume an agent
reader — no narrative history, IDs and paths over prose — are
suspended, not merely softened: a human doc's narrative can be its
load-bearing substance.

## Precedence

1. Shipped law and repo-documented invariants beat class laws — a
   verbatim-filing mandate, a contract that must stay in-header. A
   class law that would degrade a documented invariant does not apply
   there.
2. Dual-audience artifacts: split surfaces before blending laws —
   each audience gets its own surface (a file, or a bounded section)
   in its own class. A README is HUMAN-overlaid prose whose
   enumerable tables serving agents are WARM sections; never cut the
   human doc to a WARM ceiling. Where surfaces cannot split (a single
   message), the overlay governs form and the class governs
   substance.
3. An artifact may carry a NAMED CONTRACT that governs it in place of
   class-generic law (see Named contracts).

## Class laws

HOT — every token pays rent every session.
- Deltas, not norms: the norm lives in the governing skill or repo.
- Pointers, not content; a line where a table tempts (provenance:
  repo doctrine, not research).

WARM — blank-context complete, minimally.
- Premium slots: attention is U-shaped; load-bearing content
  (DONE-WHEN, commands, laws) lives at top and bottom.
- One canonical exemplar over three paragraphs of description.
- Skip markers: sections a budget-pressed reader may skip say so.
- Ceiling ~500 lines; deeper detail forks to references one level
  deep, where the medium permits (precedence rule 1 otherwise).
- IDs and paths over prose; no narrative history.
- Living state artifacts (resume records, working plans) are WARM
  however rarely read: COLD holds records of the past; a state
  file's function is to be rewritten.

COLD — fidelity over brevity.
- Verbatim, never rewritten, never compressed after filing.
- A COLD record found wrong is still never rewritten: a correcting
  entry is appended beside it and indexed; the original stands
  untouched — the correction lives in the entry and the index, never
  on the original.
- Cited by pointer; indexed by one line in a hotter surface. Loading
  a COLD artifact into a dispatch is a CHANNEL event priced at that
  dispatch — it is not a reclassification and licenses no
  compression.

CHANNEL — the orchestrator pays until session end.
- Prompts cite WARM/COLD artifacts by path; never inline what a path
  can carry.
- Returns are schema'd and capped: status, deltas, decisions,
  NOTES-as-claims; bulk output goes to disk, the return carries
  pointer + summary.

## Named contracts

An artifact whose governance outgrows class law carries a named
contract (precedence rule 3). A contract lives BESIDE the law it
extends and ships only where that law ships — never in the generic
doctrine, because a contract citing law its reader cannot load fails
the blank-context test. Instance: this repo's decision-ledger
contract, which lives in advisor-mode's references/ in this repo.

## Skill packaging directive

- The skill's body carries the class table and decision procedure,
  compact; each class's template and ONE canonical exemplar live in
  references/, loaded only when authoring that class — the skill
  practicing WARM's own exemplar and progressive-disclosure laws.
- Exemplars are domain-neutral (a generic brief, a generic memory
  index), usable outside this repo; repo artifacts may be cited as
  instance pointers, never baked in as the exemplar.

## Grounding (provenance-tagged)

Primary sources inline per bullet — audit the source, not a digest.
- vendor-canonical: progressive disclosure — skill metadata preloads,
  bodies load on relevance, references one level deep, under ~500
  lines (Anthropic skills guidance,
  docs.claude.com agent-skills best practices).
- paper: mid-context content suffers 30%+ accuracy loss — a floor,
  not an estimate ("Lost in the Middle",
  arxiv.org/abs/2307.03172).
- benchmark: all 18 tested frontier models degrade as input grows —
  minimalism is an accuracy measure, not just a cost measure
  (trychroma.com/research/context-rot).
- directional, low-authority sources: markdown ~34-38% cheaper than
  JSON on structured data and ~40-60% on document content — two
  measurement bases, not one range; XML worse
  (jsonkit.in json-vs-markdown-llm-prompts).
- convention, no empirical metrics in the source: GitHub's AGENTS.md
  guidance from 2,500+ repositories — one real snippet beats
  paragraphs of description (github.blog
  how-to-write-a-great-agents-md).
- convention: skip markers borrowed from the llms.txt "Optional"
  section (llmstxt.org).
- vendor guidance: filesystem artifacts between agents avoid the
  game of telephone (anthropic.com/engineering, harness design and
  effective-context-engineering-for-ai-agents).

## Decision procedure

1. In scope? Does the unit enter a context, and which unit is it.
2. Name the residency class by who loads it, how often, for how
   long; apply the HUMAN overlay if a person is the audience. A
   named-contract artifact follows its contract.
3. Apply the class laws under the precedence rules.
4. On class change — a WARM brief archived COLD, a COLD fact promoted
   to a HOT index line — re-price: inline content becomes a pointer.
5. SHIP RULE (a ship-time step, the mover's, not the author's): a
   shipped file may cite only what ships with it. Unconditional
   citations of session-scoped or absent artifacts are replaced by
   self-contained statements or in-repo pointers before the move; a
   citation guarded by an existence check is the sanctioned fallback,
   not a violation. The carve-out is load-bearing: any compact
   rendering of this step keeps it or drops the whole step.

NOT COVERED, by design: CHANNEL authoring guidance in detail
(separate thread); the skill text operationalizing this model
(authored only against the locked model); per-template texts (ride
with the skill).
