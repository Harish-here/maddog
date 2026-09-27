# Pattern 2 — Redundancy missed, incl. a definition the word already carries

### 137dd3e7-L1150
- pattern: 2
- target: agents/executor-lead.md
- section: S5 — Core Laws (Boundary stop, merged from Package Laws)
- session: 137dd3e7-e797-4768-a264-fc98976946ff
- lines: proposal L1147, catch L1150

Proposal:
`````text
## S4 is closed. S5 is next.

```
S5 — Package Laws, now carrying S4a (lines 71–93)
Does: five laws special to Lead: boundary stop, no nesting or self-judging,
      rent hands never verdicts, evidence drives the next move, and do not
      shadow-orchestrate.
Fails: weight test on law 1. It is one 85-word sentence with six triggers.
       Duplicate test on law 5: the shared routing text already says "Never
       do a hand's work yourself, nor take work back merely because you
       could."
Verdict: COMPRESS. Evidence: O1, O2, O5.
```

**Draft:**

> ## Core Laws
>
> Family Laws bound every hand and never license what any law here forbids; among core laws, the earlier wins.
>
> 1. **Boundary stop.** Return to Advisor before a step that needs authority outside the package or changes its intent or scope. Return too before a hard-to-reverse action (push, publish, delete; a push counts even to a user-named branch) or an instruction-file edit, unless the dispatch carries that exact action or text, or a standing grant covering it, as user-approved; never run one behind a wait.
> 2. **No nesting or self-judging.** Never create a second Lead for this package or act as an independent Judge of it; checking your own integrated result is acceptance, not judging.
> 3. **Rent hands, never verdicts.** A hand's findings and a Judge's verdict are evidence for your next move, never your judgment made for you.
> 4. **Evidence drives the next move.** Current evidence picks the next action; never keep a path because an earlier plan named it.

### What changed and why

- **Heading renamed to "Core Laws".**
  - The other four executors use the pattern "Family Laws, then Core Laws".
  - Lead had three tiers. With the six general laws gone, it now fits the family pattern.
- **The ranking sentence is byte-identical to the other executors' sentence.** This follows O3, even though the check script does not enforce it.
- **Law 1 is split into two sentences.**
  - In the old single sentence, "unless the dispatch carries…" could be read as excusing a change of intent.
  - Now it attaches only to hard-to-reverse actions and instruction-file edits.
- **Law 1 drops two triggers:** "a consequential decision outside your authority" and "a new package boundary". The draft covers both with "authority outside the package" and "changes its intent or scope".
- **Law 5 is removed as a duplicate of the shared routing text.**
  - Its one extra idea was "a wrong slice means changing the boundary, hand, or strategy".
  - That idea is what REROUTE means in the verdict block, and the verdict block reaches Lead through the fifth shared text.
- **Words:** 160, down from about 230 when S4a's sentence is counted. The running total is about 1,665.

Do you close S5 as COMPRESS with this text?
`````

Catch:
`````text
Boundary stop is already in Family law right? - My arugment what if we drop all ?
`````


### 137dd3e7-L1243
- pattern: 2
- target: agents/executor-lead.md
- section: S7 — Orchestration
- session: 137dd3e7-e797-4768-a264-fc98976946ff
- lines: proposal L1241, catch L1243

Proposal:
`````text
## S6 is closed. S7 is next.

```
S7 — Orchestration (lines 126–133)
Does: three Lead-only rules that sit above the shared routing text:
      classify each slice and never the whole package; a slice that is
      merely hard is not Lead's; and what Lead's own direct work is.
Fails: duplicate test. The section exists only to lead into S8
       (Dispatching), and your design record describes it that way:
       "Orchestration keeps Lead's lines above ROUTE". Two headings do one
       job. Two clauses also repeat text elsewhere.
Verdict: MERGE into S8. Evidence: O1, O2, O5.
Draft: S8's closure carries the merged section. The Lead lines it will
       carry are below, so you can judge them now.
```

**Lead's lines, compressed for the merge:**

> Classify each slice, never the whole package; a package may hold every shape. A slice that is merely hard is not yours: raise the hand's model or effort. Your own direct work is reasoning and the reads your judgment must hold first-hand (verification, carried investigation).

### What I cut

| Cut | Why |
|---|---|
| "by the judgment it needs" | The shared routing text opens with "Route by judgment shape". |
| "every change goes to a hand" | The new opening already says it. |
| "verification at cited evidence and the investigation you carry across steps" | I shortened it to the parenthesis "(verification, carried investigation)". Your design record uses those same two words for it. |

- **All three rules survive.**
  - Each one is a Lead quirk.
  - The Advisor has none of them, and nothing else in Lead's file carries them.
- **Words:** 45, down from 66. The running total is about 1,570.

Do you close S7 as MERGE into S8 with these lines?
`````

Catch:
`````text
Drop the entire sections -  This is basically the operate loop
`````


### 137dd3e7-L1398
- pattern: 2
- target: agents/executor-lead.md
- section: S19 — Return
- session: 137dd3e7-e797-4768-a264-fc98976946ff
- lines: proposal L1396, catch L1398

Proposal:
`````text
## S18 is closed. S19 is the last body section.

```
S19 — Return (lines 290–302)
Does: fixes the fields Lead sends back: STATUS, BLOCKED-ON, RESULT,
      DECISIONS, DELEGATION LOG, NOT DONE, NOTES.
Fails: weight test, lightly. Three field descriptions run long. Two of
       them name things that the reworked file now says elsewhere.
Verdict: COMPRESS. Evidence: O1.
```

**Draft.** It follows the S15 paragraph under `## Return`:

> The dispatch shapes RESULT; the outer fields stand whatever it says.
>
> Return exactly:
> STATUS: done | partial | blocked   (partial whenever NOT DONE is not "none")
> BLOCKED-ON: <the blocking condition, or the question for Advisor — only when partial or blocked>
> RESULT: <the outcome and the evidence Advisor needs, in the requested format>
> DECISIONS: <material calls closed inside the package, one line each, or "none">
> DELEGATION LOG: <one line per hand: what it was asked, what it returned, or "none">
> NOT DONE: <what remains, was rerouted, or was escalated, or "none">
> NOTES: <anomalies, assumptions — never a conclusion>

### What changed

- **BLOCKED-ON now reads "the blocking condition, or the question for Advisor".**
  - S14 removed the sentence that said where Lead's question goes.
  - The field now says it directly.
  - The old list is covered by "the blocking condition". That list was "authority or evidence gap, changed intent, expanded scope".
- **The first sentence and the DELEGATION LOG line lose a few words each.**
- **Every field name stays,** and so does the partial rule.
  - The other executors share the outer fields.
  - Your drift audit reverted earlier attempts to change envelopes.
- **DECISIONS and DELEGATION LOG stay in full.** I leaned on those two fields at S4, when the law "Work is paid once" was removed.
- **Words:** about 92, down from 106.

### Where the whole file lands

| Part | Words |
|---|---|
| Shared texts, nine of them, byte-identical and checked | about 550 |
| Lead's own words | about 480 |
| **Total** | **about 1,030**, down from 1,910 |

- **Lead's own text comes in under 500 words.** That figure matches your target.
- **The total stays above 500.**
  - The shared texts alone now exceed 500 words.
  - They grew during this pass, because you chose to make the orchestration behaviour byte-identical with the Advisor's.
- **I think this is the right result.** Every word above Lead's own 480 is text that the check script keeps identical across the family.

Do you close S19 as COMPRESS with this text? The frontmatter description comes next, and after that the arrangement.
`````

Catch:
`````text
See the retrun is already shaped by the dispatcher -  Do we actually need these many ?
`````


### 01c6d363-L137
- pattern: 2
- target: skills/section-by-section/SKILL.md
- section: S3 — Verdicts
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L134, catch L137

Proposal:
`````text
## Placement change

- Verdicts currently sits third, before the agent has read the target, met the user, or built a section map. It hands over a vocabulary for a job that has not started.
- I propose moving it to sit between Start and Section loop. The agent then meets the verdicts at the moment it first needs one, which is the Diagnose step.
- The ordering rule the file already states for the final assembly says instructions acted on first go at the top. Verdicts is acted on inside the loop, so it belongs next to the loop.

## Replacement text for S3

```text
## Verdicts

| Verdict | Means |
|---|---|
| KEEP | unchanged |
| REMOVE | deleted |
| COMPRESS | same instruction, fewer words |
| REWORD | same instruction, clearer words |
| RESHAPE | same content, a form that fits it |
| REPLACE | the instruction is wrong; a different instruction takes its place |
| MOVE | relocated unchanged |
| MERGE | folded into a named partner, which keeps the question |
| SPLIT | two sections, each closing on its own verdict |
```

**Approve the text and the move, or tell me what to change.**
`````

Catch:
`````text
Can that order of the verdicts be frequently occure
`````


### 01c6d363-L220
- pattern: 2
- also: 1
- target: skills/section-by-section/SKILL.md
- section: S5a — Check (three vs. five checks)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L214, catch L220

Proposal:
`````text
"How unique" and "no overlap" are already covered — that is the redundancy check, in full. Coherence is not covered, and you are right to ask.

## What each existing check already covers

- **Redundancy** covers uniqueness and overlap. Its sentence "different wording is not different meaning" is the sharpest line in the section.
- **Clarity** covers a section contradicting *itself*, and covers whether the instruction can be acted on without interpretation.
- **Responsibility** covers two sections owning the same question.

## What is missing, and it is forced by decisions you already made

**Coherence — two sections that cannot both be obeyed.** This is not self-contradiction and not duplication. Two sections can be unique, clear and separately owned, and still issue conflicting orders.

[...]

**Correctness — the instruction makes an agent do the wrong thing.** This one I would not have raised if you had not asked about expanding.

[...]

Three sentences on the choice. Coherence closes a detection hole the file already has a resolution step for. Correctness closes a bigger one: the skill collects evidence of misbehaviour and then never tests against it. Adding both takes the loop from three checks to five, on a section you have already told me feels ceremonious.
`````

Catch:
`````text
I'm okay with Coherance. But what clarity checks and correctness checks - is there enough differentiation between the to be two items?
`````


### 01c6d363-L285
- pattern: 2
- target: skills/section-by-section/SKILL.md
- section: S5b — Diagnose (axes as sub-heads)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L282, catch L285

Proposal:
`````text
```text
### Diagnose

Read the axes in the order below. The first line true of the section gives the
verdict, and it is the only one, however many others are also true.

#### Redundancy
Meaning this file carries nowhere else; different wording is not different
meaning.

- The intent needs nothing this section says → REMOVE: deleted.

#### Responsibility
One question → one owning section.

- It answers two questions → SPLIT: two sections, each closing on its own
  verdict. The halves re-enter the loop immediately, in order, before the next
  section.
- Another section already answers its question → MERGE: folded into a named
  partner, which keeps the question. Never hide an ownership conflict by
  rewording one of the two.
- The question is its own but it sits in the wrong place [...] → MOVE: relocated unchanged.

#### Coherence
No other section issues an order that cannot be obeyed alongside it.

- Another section's order cannot be obeyed alongside this one → name both in the
  proposal; the user closes which section changes, and it takes that change's
  verdict. Unclosed here, it carries to Assembly.

#### Correctness
Following it produces the right result. Judged only against evidence: an
observation, or a failure this run hit. Never against preference.

- Evidence shows that following it produces the wrong result → REPLACE: the
  instruction is wrong; a different instruction takes its place.

#### Clarity
Direct, self-consistent, actable without interpretation.

- Its content is a list, parallel cases, or a single rule, in a form that does
  not match → RESHAPE: same content, a form that fits it.
- It says its one thing in more words than it needs → COMPRESS: same
  instruction, fewer words.
- It is vague, ambiguous, or contradicts itself → REWORD: same instruction,
  clearer words.

No line above is true → KEEP: unchanged.
```

**Approve the section and the heading promotion, or tell me what to change.**
`````

Catch:
`````text
Can we compress the each bulleteni points where it is verbose wihtout losing the actula meaning
`````


### 01c6d363-L492
- pattern: 2
- target: skills/section-by-section/SKILL.md
- section: S6a — Assembly preamble
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L489, catch L492

Proposal:
`````text
```text
## Assembly

Assembly changes no closed section on its own: where a step below needs one
changed, post it as a proposal and the user closes it as in the loop, with its
own ledger row.

Where the scope was named sections, the affected context joins it here — sections
sharing a question, a reference, an ordering, or an overlapping instruction with a
reviewed one. Any the user closes here stops being UNREVIEWED.
```

- One sentence removed, nothing else altered.
- The remaining two are now separate paragraphs. [...]

**Approve and I open the Assembly steps, which is the last long section.**
`````

Catch:
`````text
Wait why do we need this section?
`````


### 3dac0029-L252
- pattern: 2
- target: skills/section-by-section/SKILL.md
- section: Tested-text law, Write, Assembly step 6, Assembly step 7 (four-axis template fix)
- session: 3dac0029-0090-466f-be1d-480786f2fe6c
- lines: proposal L245, catch L252

Proposal:
`````text
Text for both, written as rules rather than as fixes for what the scenarios happened to do.

## The law

````text
**Tested-text law.** Every text this skill proposes for the file is run over the
axes first: replacement text, a description, an outline, the composed draft. Every
axis but correctness, which needs evidence new text cannot have. Show the result
above the text, one line per axis, every axis named, `clean` where it found
nothing. An axis absent from the block did not run.

```text
Tested:  <axis> — <what it caught and what changed, or `clean`>
```
````

```text
Tested:  redundancy — cut "a missing line means the test did not run"; the
                      point is now made once, about a missing axis.
         responsibility — clean; the law still owns the rule and its shape.
         coherence — checked against Discuss, which bans prose at its own step.
                     The scope stays "proposes for the file", so a diagnosis
                     post is untouched.
         clarity — the template shows one axis line and the rule says every
                   axis takes one, closing the reading that let a run name a
                   single axis.
```

## Assembly step 6

```text
6. **Verify.** Against the intent anchor fixed at Start:
   - Show the outline, one line per surviving section in the proposed order.
   - Test the description against what the body now does: third person, what the
     file does and when to use it.

   Each carries its own `Tested:` block. The user closes the description under
   `DESC`, then the outline, as shown or with the changes named.
```
[...]

## Assembly step 7

```text
7. **Compose.** Write the draft whole, in the closed order: what an agent acts
   on first at the top, prohibitions and finish conditions at the bottom,
   optional material marked. Composing writes the order and the joins: show the
   draft with its `Tested:` block over those. Closed text is copied as approved,
   never re-tested.
```
[...]

## One thing I did not change

The Write step still says "under the tested-text law" without naming the block. It fired correctly in the test, so I left it alone rather than edit on a hunch. It does mean two steps name the block and one names the law. Say if you want it matched.

Approve, and I apply all three, add the ledger rows, and re-run the Assembly scenario to confirm the test line now appears.
`````

Catch:
`````text
Seems like we're reepating a lot of sam text
`````


### d8a02f04-L297
- pattern: 2
- target: skills/advisor-mode/SKILL.md
- section: S2 — Family Laws (reopened)
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L290, catch L297

Proposal:
`````text
Tested:  redundancy — "publishing" and "deleting" dropped; both are cases
                      of the remaining clauses.
         responsibility — clean.
         coherence — clean: outside the workspace, the first sentence
                     applies; inside it, the second.
         clarity — COMPRESS: about 52 words down to about 40, every case
                   still covered. Trade-off: the word "publish" no
                   longer appears, so a model has to match a publish to
                   "seen outside the workspace". That's a concrete test,
                   not a decode.

  - Hard-to-reverse means changing state others depend on, or anything
    seen outside the workspace, even if it can be undone. Inside a
    user-named workspace, a change is reversible unless it discards work
    or data that exists nowhere else.
`````

Catch:
`````text
My question is - Hard to reverse it self is givinf signal right do we need to explain - lets discuss
`````


### ec3c9100-L330
- pattern: 2
- target: agents/executor-smart.md
- section: S6c — Pattern table (middle column)
- session: ec3c9100-fc97-4101-93d2-3c244bd44ced
- lines: proposal L307, catch L330

Proposal:
`````text
# S6 Classify: split into three parts, with REWORD + REMOVE on the pattern table

S5 is closed. S6 has three separate parts, so I split it the way I split S3:

- **S6a:** the shared Patterns preamble.
- **S6b:** the rule to classify on every pass.
- **S6c:** the pattern table.

## S6a — Patterns preamble (lines 93–96)

```text
Does:     Classify before the first tool call; one or several patterns may
          apply; hold each one's law; work that fits none is returned.
Fails:    nothing. The fragment check confirms it matches the constitution.
Verdict:  KEEP
```

## S6b — Classify on every pass (lines 98–99)

```text
Does:      Classifies again on every pass through the loop, because a pass
           after VERIFY can bring a new pattern. The example given is that a
           fix after DIAGNOSE is BUILD.
Elsewhere: Lead's "Classify every slice, not only the first" is the matching
           rule. S9 Verify also says "then CLASSIFY again". The DIAGNOSE row in
           S6c says the same thing as the example.
Fails:     nothing. It mirrors Lead's rule. It was added in the latest commit
           (ad490ff), and a Sonnet test run showed Smart re-classifying on
           each pass only with this rule present.
Verdict:   KEEP
```

## S6c — Pattern table (lines 101–106)

```text
Does:      Defines BUILD, TRANSFORM, DIAGNOSE and REVIEW, each with its work
           and its law. The columns are Pattern | Work | Law; Lead uses Flow
           and Judge uses Target for the middle column.
Elsewhere: S6b says "a fix after DIAGNOSE is BUILD". The constitution's
           routing table defines Smart's work as "implementation choice,
           criteria review, diagnosis with a known evidence surface", which
           the four rows match.
Fails:     redundancy (REMOVE). The DIAGNOSE row ends with "A fix built on
           the diagnosis is BUILD work under its own law." S6b now says the
           same thing. The row's sentence is older (0860182); S6b was added
           later and tested. The row's sentence goes, and S6b stays.
Also:      clarity (REWORD), three points:
           1. BUILD says "create a defined outcome" and "what the delegated
              outcome requires". These are the same misuse of "outcome" that
              S1 fixed; they mean the goal.
           2. REVIEW says "executor-judge's, not yours". You chose short names
              in S1, and Lead's body says "Judge", so this becomes "Judge's".
           3. TRANSFORM's law ends "stop before crossing an invariant that
              cannot be established". It can be read two ways: an invariant
              nobody stated, or one whose survival you cannot show. The second
              fits Invariant Preservation. I'd write it as "stop before a
              change whose effect on an invariant you cannot establish".
Verdict:   REMOVE (the DIAGNOSE sentence) + REWORD (points 1 to 3)
Evidence:  O1
```

## Checked and left alone in S6c

- **Pattern names and laws:** they fit Smart's shape. DIAGNOSE is bounded here ("a bounded symptom and evidence surface"), while Lead's DIAGNOSE is for an investigation that keeps changing. The routing split between them is clear.
- **REVIEW's gate clause:** it matches Judge's description and the constitution's GATE row, so a gating review leaves Smart.

Do you close S6a as KEEP, S6b as KEEP, and S6c as REMOVE + REWORD?
`````
the user continued that discussion rather than a new proposal landing first.

Catch:
`````text
Lets discuss the need of the coulmn
`````


### f09ade50-L398
- pattern: 2
- also: 3
- target: agents/executor-fast-read.md
- section: Assembly A2 — the opened-source rule (S5, law 1)
- session: f09ade50-46a3-4137-938b-80a10f28fa69
- lines: proposal L396, catch L398

Proposal:
`````text
### A2. The opened-source rule sits in EXTRACT, but three rows need it (S11 → S5)

- **The problem:** SWEEP cites items, VERIFY cites passages, and EXTRACT quotes text. O3's failure, a quote the cited page does not hold, can happen in any of them. Today the rule covers EXTRACT alone.
- **The clash to resolve:** law 2 blocks when a source *the dispatch names* cannot be opened. The new rule must cover only pages the model *found* on its own.
- **Proposed:** S11 takes MOVE for that sentence, and S5 takes MERGE.

```text
Tested:  redundancy — the rule is stated once, in law 1
         responsibility — law 1 owns every citation; EXTRACT keeps only its copying rule
         coherence — "a page you found" leaves named sources to law 2's blocked
         clarity — clean
         ambiguity — "found" versus "named" separates NOT DONE from blocked
```

```markdown
1. **Evidence, never judgment.** Report what the sources show, quoting a
   source wherever you state what it says, with enough context to keep
   its meaning. Quote and cite only a source you opened yourself; a search
   result's summary is not the source, and a page you found but could not
   open goes in NOT DONE. Never merge sources into one statement,
   synthesize a conclusion, infer intent, diagnose, weigh explanations, or
   recommend; if the question needs that, return `blocked` with the
   evidence you have.
```

Do you close A1 (S6 REWORD), A2 (S11 MOVE and S5 MERGE with this text), and A3 (S1 REWORD)?
`````

Catch:
`````text
A1 REWORD, A2 MOVE + MERGE, A3 REWORD. but does the 'evidence, nev...' is verbose i feel - or does it carry all the neccessary text
`````
