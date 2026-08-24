# Description Standard — skill `name` and `description` frontmatter

**Scope and adoption:** binds every NEW or CHANGED skill `description`/`name` from this
standard's adoption date. An existing skill is reviewed against it only when its
description changes — no retroactive failure for descriptions untouched since adoption.

Compliance contract for Dimension 2 routing review of skills (`skills/*/SKILL.md`,
`.claude/skills/*/SKILL.md`). Descriptions are **HOT** — every token pays rent every
session (`skills/efficient-md/references/hot.md`); this file itself is **WARM**, loaded
per review dispatch (`skills/efficient-md/references/warm.md`).

Provenance: `code.claude.com/docs/en/skills.md` (fetched copy, cited by line),
`agentskills.io/specification`, `platform.claude.com` agent-skills best-practices, and
`github.com/obra/superpowers` writing-skills.

## §1 MECHANICS

- Claude reads `description` (+ `when_to_use`, appended) to decide when to load a skill;
  if `description` is omitted, Claude uses the first paragraph of the body instead. [skills.md L323]
- `description` + `when_to_use` are truncated at 1,536 characters in the skill listing;
  when a description names multiple use cases, put the most important one first — it's
  the one guaranteed to survive the cut. [skills.md L323-324, L1041]
- Listing budget = 1% of context; on overflow descriptions drop least-invoked-first, names
  always survive — hence §2 rule 3. [skills.md L1035]
- Malformed YAML frontmatter produces empty metadata — no description to match, so the
  skill is silently unroutable **by the model**; `/skill-name` still works. [skills.md L1024]
- Both failure modes are documented: under-triggering (fix: keywords users would
  naturally say) and over-triggering (fix: a more specific description, or
  `disable-model-invocation`). [skills.md L1015-1031]
- An agent acts on an incomplete description instead of loading the body — procedure text
  in the description gets followed without the real instructions ever being read.
  [relayed, unverified — obra/superpowers rationale]

## §2 NAME RULES

1. 1–64 characters, matching `^[a-z0-9]+(-[a-z0-9]+)*$` — lowercase, digits, single
   hyphens, no leading/trailing/double hyphen. [agentskills.io spec]
2. Where `name` is present it MUST equal the directory name (agentskills.io spec).
   `name` is optional in Claude Code (skills.md L322) — an absent `name` passes
   D-NAME-1/2 and is reviewed on the directory name. For plugin skills the command is
   `/<plugin>:<name>` (skills.md L362-380); the directory-match rule still binds for
   spec portability.
3. Carries the task shape in ≤3 words — verb-noun, noun-role, or a bare domain noun
   where that is unambiguous (`review-agent`, `mine-session`, `release`) — the name is
   the only text guaranteed to survive listing overflow (§1, budget bullet).
4. No generic token alone (`helper`, `tools`, `utils`) and no plugin-name prefix inside
   the name — the plugin namespaces it at install time.

## §3 DESCRIPTION RULES

Four slots, in order. Slot content differs per skill; the order does not.

**Slot order authority:** claim-then-trigger, per skills.md L75, L839 and the
agentskills spec's own Good example — not "key use case first" (that governs which use
case survives the 1,536-char truncation cap when several are named, see §1).

1. **S1 CLAIM** — what the skill does, one clause, third person.
2. **S2 TRIGGER** — a "Use when …" sentence in the user's natural vocabulary; 3–7
   concrete situations or keywords.
3. **S3 REDIRECTS** — every "Do NOT use for X" / "Not for X" names the correct
   destination ("— that is `<neighbour>`"); needed only where a sibling skill or agent
   could plausibly capture the same shape. A bare prohibition with no destination is a
   defect. Where no skill is the right destination, the redirect must still name the
   disposition ("— do that directly, no skill"); only a redirect naming neither a
   neighbour nor a disposition is a defect.
4. **S4 INVARIANT** (optional) — a structural guarantee that changes what the caller can
   expect (e.g. "never merges"); include only when load-bearing at invocation time.

Prohibited in the description: the skill's procedure/steps/workflow — except where a
named stage/gate sequence is itself the discriminator a caller routes on; naming the
stages is permitted, describing how to execute them is not; norms the body already
holds; first/second person; XML tags; "claude"/"anthropic" in `name`; marketing
adjectives; reference to the skill's own body (section names, "see below") —
unreachable at routing time.

Budgets: target ≤500 characters; hard cap 1,024 (agentskills.io spec). Prefer folding
`when_to_use` content into `description` — both count toward the same 1,536-char listing
cap and `when_to_use` is not part of the open agentskills spec.

## §4 PARTITION TESTS

Run `checklist.md` Dimension 2's partition procedure (L88-96) unchanged, extending its
enumeration from `agents/` to every sibling skill installed alongside the target.

- D-PART-1 — keyword monopoly
- D-PART-2 — double-match (positive discriminator required on both sides)
- D-PART-3 — uncovered shape

## §5 FIELD INTERPLAY

| Field | Effect on routing | What the standard requires |
|---|---|---|
| (default) | description always in context; body loads on invocation | full standard applies |
| `disable-model-invocation: true` | description NOT in context — `/`-menu-only [skills.md L327, L489-491] | standard still applies (humans read the menu, a later flip re-enables model routing); S2 may be shorter |
| `user-invocable: false` | description stays in context, hidden from `/` menu [skills.md L328, L489-491] | full standard applies — this is the model-routed case |
| malformed YAML | empty metadata, skill unroutable by the model; `/skill-name` still works [skills.md L1024] | hygiene defect (Dimension 0), not a description-standard finding |

## §6 REVIEW CHECKLIST

| ID | Rule | Pass/Fail |
|---|---|---|
| D-NAME-1 | 1–64 chars, `^[a-z0-9]+(-[a-z0-9]+)*$` | |
| D-NAME-2 | `name` equals directory name (when present) | |
| D-NAME-3 | Task shape in ≤3 words, verb-noun/noun-role/bare domain noun | |
| D-NAME-4 | No generic-only token; no plugin-name prefix | |
| D-DESC-1 | S1 CLAIM present: one clause stating what the skill does | |
| D-DESC-2 | S2 TRIGGER "Use when …", 3–7 concrete situations, user vocabulary | |
| D-DESC-3 | S3 REDIRECTS: each names a destination or disposition, none bare | |
| D-DESC-4 | S4 INVARIANT, if present, is load-bearing at invocation (else advisory) | |
| D-DESC-5 | No procedure/steps/workflow (named routing-discriminator stages exempt); no restated body norms | |
| D-DESC-6 | No 1st/2nd person, no XML tags, no marketing adjectives, no claude/anthropic | |
| D-DESC-7a | ≤1,024 chars (hard cap) | |
| D-DESC-7b | ≤500 chars (target; over target is a NOTE, not a failure) | |
| D-DESC-8 | Description is specific enough not to capture neighbouring shapes (over-trigger check) | |
| D-DESC-9 | No reference to the skill's own body (section names, "see below") — unreachable at routing time | |
| D-PART-1 | Keyword-monopoly test run against all siblings | |
| D-PART-2 | Double-match test: positive discriminator on both sides | |
| D-PART-3 | Uncovered-shape scan run against all siblings | |
| D-FIELD-1 | `disable-model-invocation`/`user-invocable` set consistent with intended routing | |

## §7 EXEMPLARS

Fresh, hypothetical `changelog-draft` skill — not a repo skill; do not read as a rating
of any installed skill.

**Compliant** (353 chars):

> Drafts a CHANGELOG entry from the commits since the last release tag. [S1] Use when the
> user asks to write release notes, draft a changelog, or summarize what shipped since a
> version tag, before cutting a release. [S2] Not for auditing an existing CHANGELOG for
> accuracy — that is the release skill's READY gate. [S3] Writes only to CHANGELOG.md;
> never tags or pushes. [S4]

**Non-compliant** (same skill, defects tagged):

> Helps you with changelogs. [D-DESC-1: vague claim, no use case] [D-DESC-6: second person "you"]
> First, run git log, then extract the commits, then group them by type, then format as
> markdown, then write to CHANGELOG.md. [D-DESC-5: procedure/steps in description]
> Great for making beautiful, professional changelogs! [D-DESC-6: marketing adjectives]
> Don't use this for anything else. [D-DESC-3: bare prohibition, no destination]
>
> — also missing: no "Use when" trigger sentence at all [D-DESC-2].

**Partition illustration** (D-PART-2, double-match, hypothetical sibling): a
`release-notes-writer` skill with S1 "Writes user-facing release notes from merged PRs"
would double-match every task `changelog-draft` claims unless each gates on its own
source — commit log ("since the last release tag") vs. merged PRs — as the positive
discriminator, not a negative S3 clause on either side.

## §8 RELATION TO OTHER CONTRACTS

- `checklist.md` Dimension 2 (lines ~98–127) is the stricter five-slot superset for
  `agents/executor-*.md` descriptions — this standard is the base; do not restate its
  rules here, point to it.
- The description text itself is HOT (`skills/efficient-md/references/hot.md`) — every
  character is resident every session; this file, read per review dispatch, is WARM.
- `skills-ref validate ./my-skill` (agentskills.io CLI) is the mechanical pre-check for
  `name`/`description` field shape before a judgment-based review runs.
