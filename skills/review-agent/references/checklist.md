# Agent definition review — checklist

An agent definition is dispatch logic plus a behavior spec. Reviewing one is
a distinct discipline from reviewing code: the reader is the agent itself,
starting blank, with only what is on the page.

## Scope

Agent definitions and always-resident skill text (`agents/*.md`,
`skills/*/SKILL.md`, and anything a skill force-loads). Workflow definitions
(`workflows/*.js`) are deliberately out of scope for this pass.

## Evidence set

Assemble before reviewing: the target file(s); every file in `agents/`;
every `skills/*/SKILL.md` plus its `references/`; `README.md`; `CLAUDE.md`;
`.claude-plugin/*.json`; `install.sh`; and the binding design artifact for
this change (spec, decision ledger, or approved proposal).

Dimensions 2 and 6 are family-wide and cannot be executed on the target file
alone — they require the full evidence set above, every time.

## Binding spec

Dimension 1 (spec fidelity) requires a supplied design artifact. Without
one, report dimension 1 as NOT EXECUTED. Never substitute the file's own
claims about itself for its spec — a file cannot certify its own fidelity.

## Blank-context premise

Read every instruction exactly as the agent receives it: blank context, only
the frontmatter description visible to callers before dispatch, no ability
to ask a clarifying question. Flag any reference to a document, decision, or
conversation the agent has no path to reach.

## Ordering & budget

Run dimensions in this order: 0 first, then 2, 3, 4, 5, 1, 6, 7, 8. Dimension
0 is cheap and is the precondition the others assume — reasoning about a
file's content before confirming it is well-formed risks reasoning about raw
tool-call residue as if it were intent. Cap dimension 8 (token-weight) at
descriptions and always-resident skill bodies — never agent bodies, which are
pay-per-dispatch and not a token-weight concern. A dimension with no defects
is reported "checked-clean: <what was read>" — never padded with restated
procedure to look thorough.

## Output contract

Each finding: **type** (load-bearing | cosmetic | unverified assumption) +
**dimension** + **file:line** + a **concrete failure scenario** (what
happens when this line is followed, not what it "could" mean) + replacement
text where short. File each defect once, under its primary dimension;
elsewhere, cross-reference — never restate. The reviewer's own return format
carries STATUS/VERDICT; this contract governs the findings inside it, not
the envelope.

---

## Dimensions

### 0. FILE HYGIENE
**Subject:** raw bytes.
**Procedure:** read the file top-to-bottom as text, not as intent. Check for
tool-call or XML residue left at the end of a shipped file, truncation
mid-rule, a frontmatter block that never closes, duplicated blocks. This is
a read, not an inference — do not reason about what the file means before
confirming it is well-formed.
**Output shape:** one finding per hygiene defect, file:line, quoting the
offending bytes.

### 1. SPEC FIDELITY
**Subject:** file vs. supplied spec.
**Procedure:** every element the spec requires is present in the file and
uncontradicted by it. Where the spec and the file share verbatim text,
byte-compare (normalizing only line-wrapping) — do not eyeball similarity.
NOT EXECUTED without a spec (see Binding spec above). Do not infer design
history from git metadata; without the spec, history claims are unverified
assumptions — a commit log shows what changed, not why, and reading intent
into it produces confident, false claims about what did or didn't happen.
**Output shape:** one finding per spec element missing, contradicted, or
byte-divergent; NOT EXECUTED as a single line if no spec was supplied.

### 2. ROUTING PARTITION
**Subject:** frontmatter descriptions only, across the entire family.
**Procedure:** enumerate every agent in `agents/` yourself — do not rely on
a list handed to you. Run the keyword-monopoly test: a word appearing in
only one description captures every task containing that word, regardless
of fit. Find task shapes that match two descriptions, and shapes that match
none. A shape separated from a neighbor only by a "Do NOT use for..." clause
is not partitioned — a partition requires a positive discriminator on both
sides, not a negative one on either.
**Output shape:** one finding per monopoly word, per double-match shape, per
uncovered shape, per weak-negative tiebreak; quote both competing
descriptions.

### 3. NORMATIVE COHERENCE
**Subject:** the body's normative statements against each other.
**Procedure:** identity prose, role claims, obligations, prohibitions, and
mode-specific laws all count as normative. Check every obligation against
every prohibition in the same file — prohibition wins in practice, so a
cancelled obligation is a defect even if never stated as an exception. An
identity claim contradicted by an operating rule reads as agent failure just
as loudly as two rules contradicting each other.
**Output shape:** one finding per contradicting pair, quoting both
statements and naming which one the agent will actually follow.

### 4. BEHAVIORAL REALISM
**Subject:** statements vs. the agent's actual capabilities and
information.
**Procedure:**
  (a) apply the blank-context test (see preamble);
  (b) build the mode-output × return-field matrix in both directions —
      every declared output has a field to carry it, and every field is
      fillable — then re-run the check with STATUS forced to blocked;
  (c) for every trigger, threshold, or condition in the file: enumerate at
      least three real instances of the situation it names, including the
      two most dangerous shapes that situation can take, and check whether
      the stated condition actually names each one. A condition that fires
      only on the case its author was picturing is a defect.
**Output shape:** one finding per unfillable field, per missed trigger
shape, each with the concrete instance that exposes it.

### 5. OBLIGATION-WEAKNESS AUDIT
**Subject:** affirmative obligations only.
**Procedure:** list every affirmative obligation in the file. For each, ask
whether skipping it is silent — nothing downstream would detect or object.
For every silent one, name the structure that could convert it: a hook, a
tool removed from the agent's `tools:` list, artifact-first ordering (the
obligation must be discharged before the next step is even possible), or a
file-layout change. An obligation with no such structure available is still
a finding — name that too.
**Output shape:** one finding per silently-skippable obligation, naming the
converting structure or stating that none exists.

### 6. DOC COHERENCE
**Subject:** the repo's other documents.
**Procedure:** check named evidence — `README.md`, `CLAUDE.md`,
`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — against
the agent/skill files for: same family membership, same role identities, no
stale claims (a doc describing behavior the shipped file no longer has).
Model pins belong in exactly one place — the doctrine's exchange-rate table,
which lives in README — name that location explicitly when flagging a
duplicate pin elsewhere.
**Output shape:** one finding per stale claim or duplicate pin, quoting the
doc line and the contradicting file:line.

### 7. DECOUPLING
**Subject:** statements about external systems or consumers.
**Procedure:** no agent or skill should depend on a specific consumer's
implementation, or on another agent's internal mode taxonomy. Every
capability reference (a tool, an install-time feature) must carry a real
degraded fallback, checked per install mode — plugin and symlink are
different paths per CLAUDE.md, and a fallback that only exists on the
maintainer's own path is not a fallback.
**Output shape:** one finding per undocumented dependency or per
install-mode-specific fallback gap, naming which install mode breaks.

### 8. TOKEN-WEIGHT
**Subject:** always-resident text only.
**Procedure:** line by line, ask what could be pay-per-use (moved to a
reference, loaded on demand) instead of resident; what duplicates text the
registry already injects (e.g. frontmatter descriptions restated in the
body). Check partial duplication both ways: an incomplete copy of another
file's rule-set actively teaches the wrong closure and is worse than no
copy, so flag it at its primary home; and the reverse check — pay-per-use
text the agent needs BEFORE it knows to load the reference must be resident,
not filed where it can only be read after the decision it should have
informed.
**Output shape:** one finding per movable block, per stale duplicate, per
misfiled prerequisite, with the correct home named.

---

## Evidence appendix

### The 14 ground-truth failure classes

Distilled from real findings across three premortems; each was a load-bearing
defect that shipped past an unaided reviewer. Tagged with the dimension that
owns it.

1. A law cancelled by another law in the same file (obligation vs
   prohibition; prohibition wins in practice). — **Dimension 3**
2. Routing keyword monopoly: a word appearing in only one agent description
   captures every task containing it. — **Dimension 2**
3. Two descriptions matching the same task shape with only a weak negative
   clause as tiebreak. — **Dimension 2**
4. A return contract with no field for one mode's declared output;
   unfillable fields when STATUS is blocked. — **Dimension 4**
5. Literal tool-call/XML residue left at the end of a shipped file. —
   **Dimension 0**
6. An identity principle contradicting the agent's own delegation rules. —
   **Dimension 3**
7. A trigger condition that misses the most dangerous real-world shapes of
   its situation. — **Dimension 4**
8. An instruction requiring documents the reader is structurally prevented
   from seeing. — **Dimension 4**
9. A procedure filed in an on-demand reference that can only be performed
   BEFORE the reference is loaded. — **Dimension 8**
10. A capability reference with no degraded fallback on the recommended
    install path. — **Dimension 7**
11. Partial duplication of another file's rule-set, where the omitted item
    teaches a wrong closure. — **Dimension 8**
12. Stale claims in manifests/docs contradicting the shipped files. —
    **Dimension 6**
13. Model pins repeated in several places when the doctrine requires once.
    — **Dimension 6**
14. An affirmative obligation whose silent skipping nothing detects, fixable
    by structure. — **Dimension 5**

Also observed, in the reviewer itself rather than in a reviewed file: findings
returned untyped, with no load-bearing/cosmetic distinction; findings with no
per-finding failure scenario; and one confidently false history inference —
a reviewer read `git log`, saw one commit, and concluded prior review
findings "were never applied," when the folds in question predated that
commit entirely. The output contract's type/scenario fields and dimension
1's git-metadata rule above exist because of exactly these three failures.

### Provenance

Distilled 2026-08-14 from three opus premortems (executor family revamp: 18
findings; advisor-mode revamp: 14 findings; checklist premortem: 19
findings), PR #2 of maddog-skills.

### Deliberately missing / next pass

Workflow definitions; a findings-to-eval-fixture generation procedure;
micro-tested wording of each dimension; per-dimension maturity markers.
