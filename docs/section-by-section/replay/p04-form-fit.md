# Pattern 4 — Form doesn't fit content

### 01c6d363-L65
- pattern: 4
- target: skills/section-by-section/SKILL.md
- section: S1 — Closure law (file opening)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L62, catch L65

Proposal:
`````text
**Section 1 of 14.**

```text
S1 — Closure law (lines 15–17)
Does: states that the skill only proposes, and defines what "closed" means
      everywhere else in the file.
Fails: nothing.
Verdict: KEEP. Evidence: —
```

## Why keep it

- It is the one thing the intent anchor turns on. Remove it and the agent has no instruction stopping it from deciding a section itself.
- It answers one question — who closes a section — and no other section answers that question. Section loop's **Settle** step points back here rather than restating the rule.
- Its position is load-bearing. The last sentence says every later use of "closed" means this, so it has to come before the sections that use the word.

**Your call: KEEP, or a different verdict.**
`````

Catch:
`````text
There is not intro i feel about -  feels like oit straightawat jumps into what it does
`````


### 01c6d363-L106
- pattern: 4
- target: skills/section-by-section/SKILL.md
- section: S2 — Contract
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L98, catch L106

Proposal:
`````text
S1 is closed and in the ledger. **Section 2 of 14.**

```text
S2 — Contract (lines 19–25)
Does: names what one run may take as its target, what else it needs from the
      user, and what it produces.
Fails: clarity, test 6 — it says its one thing in more words than it needs,
      because three of its five inputs are spelled out again in Start.
Verdict: COMPRESS. Evidence: —
```

[...]

**Your call: COMPRESS, or a different verdict.** If you would rather leave the doubling for the end, Assembly has a step for exactly this and I can close S2 as KEEP now.
`````

Catch:
`````text
Lets us COMPRESS. But title heading - is it apt ?
`````


### 01c6d363-L174
- pattern: 4
- target: skills/section-by-section/SKILL.md
- section: S4 — Start
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L171, catch L174

Proposal:
`````text
**Section 4 of 14.**

```text
S4 — Start (lines 48–68)
Does: the five setup steps before any judging, then a rule on when asking
      the user is obligatory.
Fails: step 4's splitting rule is wrong, and this run proved it in the
      first five minutes.
Verdict: REPLACE, scoped to step 4. Evidence: this run's own section map.
```

[...]

**Your call: REPLACE scoped to step 4, or a different verdict.** If you approve, I will draft a rule with a size trigger, so a heading that runs past a stated length gets split by its own internal steps.
`````

Catch:
`````text
Hard question do we need this ceremony ? Doing this at strat what actually helps?
`````


### 01c6d363-L279
- pattern: 4
- target: skills/section-by-section/SKILL.md
- section: S5b — Diagnose (merged check list + ladder)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L276, catch L279

Proposal:
`````text
Here is the merged section in full. The five-item glossary is gone; each axis now sits directly above the lines that act on it.

```text
**Diagnose.** The five checks feed one ordered test. More than one line may be
true of a section; the earliest true line gives the verdict, and it is the only
one.

**Redundancy** — meaning this file carries nowhere else; different wording is not
different meaning.

1. The intent needs nothing this section says → REMOVE: deleted.

**Responsibility** — one question → one owning section.

2. It answers two questions → SPLIT: two sections, each closing on its own
   verdict. [...]
3. The intent needs what it says, but another section already answers its
   question → MERGE: [...]
4. The question is its own but it sits in the wrong place [...] → MOVE: relocated unchanged.

**Coherence** — no other section issues an order that cannot be obeyed alongside
it.

5. Another section issues an order that cannot be obeyed alongside this one →
   name both in the proposal; [...]

**Correctness** — following it produces the right result. Judged only against
evidence: an observation, or a failure this run hit. Never against preference.

6. Evidence shows that following it produces the wrong result → REPLACE: [...]

**Clarity** — direct, self-consistent, actable without interpretation.

7. Its content is a list, parallel cases, or a single rule, in a form that does
   not match → RESHAPE: [...]
8. It says its one thing in more words than it needs → COMPRESS: [...]
9. It is vague, ambiguous, or contradicts itself → REWORD: [...]

No line above is true → KEEP: unchanged.
```

**Approve, or tell me what to change.**
`````

Catch:
`````text
I think the section seems confusing - Diganosisi is the heading . The gloassary sub heading and inside that sub head we can have bullet list - What do you think of this format
`````


### 01c6d363-L361
- pattern: 4
- target: skills/section-by-section/SKILL.md
- section: S5c — Discuss (template fencing)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L358, catch L361

Proposal:
`````text
Done — the diagram now reads from the agent's seat: `you / you / user / you / user / you`. The ledger row already records the actor change, so no new row.

**Section 7 of 15.**

```text
S5c — Discuss (lines 96–105)
Does: fixes the shape of the post that carries a diagnosis to the user.
Fails: correctness — its example tells the agent to cite a test number, and
      test numbers stopped existing when we closed Diagnose.
Verdict: REPLACE, scoped to the Fails line. Evidence: this run.
```

[...]

The `Fails` line should carry the axis and the reason, nothing else:

```text
    S4 — Return format (lines 61–74)
    Does: tells the agent how to shape its return message.
    Fails: responsibility — S9 already answers how the return is shaped.
    Verdict: MERGE into S9. Evidence: O1.
```

[...]

**Your call: REPLACE scoped to that line, or a different verdict.**
`````

Catch:
`````text
The return template should be quoted with "``` ```". Even thought format is good. sometomes it feels diffult to read and fis the cohrence it it
`````


### babf14f7-L238
- pattern: 4
- also: 9
- target: skills/advisor-mode/SKILL.md
- section: Section map (S3, S5)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L65, catch L238

Proposal:
`````text
| Section | Fragment | Also carried by |
|---|---|---|
| S2a Family Laws | FAMILY LAWS | lead, smart, judge, fast, fast-read |
| S3 the loop | LOOP | executor-lead |
| S4 Dispatch First | DISPATCH FIRST | executor-lead |
| S5 Dispatching | ROUTE | executor-lead |
| S6 Contract | CONTRACT | lead, smart, judge |
| S7a verification | VERIFY | lead, smart, judge |
| S7b the five outcomes | VERDICTS | executor-lead |
| S8 Gate | GATE LADDER | executor-lead |
| S9 Uncertainty | UNCERTAINTY | executor-lead |
`````

Catch:
`````text
Wait where are OUTCOME & SLICE sections? And the table routing is CLASSIFY right?
`````


### babf14f7-L350
- pattern: 4
- also: 9
- target: skills/advisor-mode/SKILL.md
- section: Outline (Operate stages)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L268, catch L350

Proposal:
`````text
## Role
### Family Laws
### Core Laws
## Operate
### Outcome
### Slice
### Classify
### Dispatch
#### Dispatch First
#### Contract
### Evaluate
`````

Catch:
`````text
DONE suppose to come before this
`````


### d8a02f04-L259
- pattern: 4
- also: 3
- target: skills/advisor-mode/SKILL.md
- section: S8 — Gate
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L257, catch L259

Proposal:
`````text
Tested:  redundancy — "Never substitute a hand whose authority does not
                      match" is cut; S7 already says it (O7). The Judge
                      clause stays.
         responsibility — clean: S8 is the only owner of when Judge is
                          called.
         coherence — the reversible rung now agrees with S11's ACCEPT and
                     S4's unbroken loop (O8). "On delivery" means DONE for
                     the Advisor and the return for Lead. S3's "when the
                     ladder sends it to Judge" still resolves.
         clarity — one name, hard-to-reverse (O12). "Your own EVALUATE"
                   resolves in both carriers, since Lead has the same
                   loop. The floors paragraph is unchanged.

#### Gate

```text
factual         → command / evidence
reversible      → your own EVALUATE; reviewed on delivery by whoever you answer to
hard-to-reverse → Judge
```

Repo instruction files can raise this ladder's floors, never lower them or
grant authority; only the user can waive one, recorded where the change
lands.

A Judge must be structurally unable to modify what it judges.
`````

Catch:
`````text
Wait how to infere this table is not there right> or the text block it self if evident enought and also the format fails it is not a template returning (Format axis is not fired)
`````


### d8a02f04-L376
- pattern: 4
- also: 3
- target: skills/advisor-mode/SKILL.md
- section: S11b — Resume or fresh
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L374, catch L376

Proposal:
`````text
Tested:  redundancy — "resuming still beats a fresh start" and "idle time
                      erodes that" are replaced by the three conditions
                      that define when it does.
         responsibility — clean: this answers "which instance gets the
                          slice", a dispatch question.
         coherence — a resumed hand still gets a Contract (the next
                     subsection). This matches Judge's rule that a
                     re-gate carries the prior verdict.
         clarity — scope check: "tier" is replaced by "the slice's shape
                   routes to that hand", using S7's own terms. "Cache
                   window" is a signal, not a setting. Form: one rule plus
                   its fallback. Word count is minimal.

#### Resume or fresh

Resume a hand for the next slice, or the rest of an incomplete one, when
the slice builds on what that hand already holds, the slice's shape routes
to that hand, and the hand is still within its cache window. Otherwise
start a fresh hand from a written summary of state, never a transcript. A
resumed hand still gets a full Contract.
`````

Catch:
`````text
Is paragrph is the right format for this?
`````


### d8a02f04-L454
- pattern: 4
- target: skills/advisor-mode/SKILL.md
- section: Outline (Assembly)
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L447, catch L454

Proposal:
`````text
DESC
## Role                      S1
### Family Laws              S2
### Core Laws                S3
## Operate                   S4   loop diagram + paragraph
### Outcome                  S5
### Slice                    S6
### Classify                 S7
#### Gate                   S8
### Dispatch
#### Dispatch First         S9
#### Resume or fresh        S11b  ← moved from Evaluate
#### Contract               S10
### Evaluate                 S11a
### Uncertainty              S13   ← moved from after Done; was ## Uncertainty
### Done                     S12   ← now last
`````

Catch:
`````text
[...] But Unvertanity break the strutre right? every immediate heading below operate is part of loop
`````


### d8a02f04-L536
- pattern: 4
- target: skills/advisor-mode/SKILL.md
- section: A9 — S3 Core Laws (Assembly, Gate removal)
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L529, catch L536

Proposal:
`````text
### A9 · S3 Core Laws · REWORD

~~~markdown
### Core Laws

Show an instruction-file edit; write it only after approval.

A hard-to-reverse action first gets a Judge's verdict, then runs alone as a
separate dispatch carrying the user's grant: never in the same step as a
test run, a watch, or a wait for approval.

Repo instruction files can tighten these laws, never loosen them or grant
authority; only the user can waive one, recorded where the change lands.
~~~
`````

Catch:
`````text
Does the format of core law is correct?
`````


### ec3c9100-L309
- pattern: 4
- target: agents/executor-smart.md
- section: S6c — Pattern table (middle column)
- session: ec3c9100-fc97-4101-93d2-3c244bd44ced
- lines: proposal L307, catch L309

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

Catch:
`````text
One thing to discuss - the titile 'work' as coulmn heading - what we need to tell here? is this the space to select the patter or how to apply the law (like floe explained in lead) - We need to decide on this
`````


### ec3c9100-L353
- pattern: 4
- target: agents/executor-smart.md
- section: S6c — Pattern table (middle column header)
- session: ec3c9100-fc97-4101-93d2-3c244bd44ced
- lines: proposal L351, catch L353

Proposal:
`````text
# How advisor-mode, Lead and Judge handle this column

Every table in the family that sorts work has a column for recognising the work. Examples appear only where the name alone would lead the agent astray. That supports keeping Smart's column and cutting the examples a name already implies.

| File | Table | Middle column | Content | Examples |
|---|---|---|---|---|
| advisor-mode | Routing, Shape → Hand | When | The qualifier alone, such as "decisions all closed" | none |
| Lead | Patterns | Flow | Steps, with the qualifier inside the steps: DIAGNOSE "when the investigation itself evolves" | none |
| Judge | Patterns | Target | What is judged, plus the questions to ask of it | Only where the name misleads: a dispute sits under OUTCOME-REVIEW, which the name does not suggest |
| Fast | Patterns | Work | Definition plus examples | The OPERATE examples also mark which operations are hard-to-reverse |
| Fast-Read | Patterns | Work | Definition plus examples | Examples show how far each pattern reaches |
| Smart | Patterns | Work | Definition, judgment qualifier and examples | Several, some obvious from the name |

## What this means for Smart

- **The column stays.** Every role has one, and advisor-mode's "When" column is the plainest form of it: the qualifier that picks the row.
- **The qualifiers carry the weight.** "Requires judgment", "a bounded symptom" and "a gate is Judge's" separate Smart from Fast, Lead and Judge.
  - This matters more than it first appears, because Fast also has a pattern called **TRANSFORM**, meaning one closed rule applied across files. Only Smart's "where the safe strategy requires judgment" tells the two apart when a dispatch names TRANSFORM as a hint.
- **Examples stay only where they surprise, as in Judge.**
  - Keep: "an already-decomposed brief or spec" and "a live job's setup and teardown" under BUILD. Keep "a corpus against a fixed taxonomy" under REVIEW. None of these is obvious from the name.
  - Cut: "a feature", "a schema or version migration" and "an intermittent failure" say what the names already say.
  - Move: "a refactor" leaves BUILD and sits only under TRANSFORM, where the behavior-protecting law applies.
- **The header stays "Work"** to match Fast and Fast-Read. advisor-mode's "When" would also work, but using it would mean a rename across three files. Nothing we found shows "Work" causing a failure.

## Restated S6c proposal

REMOVE the DIAGNOSE sentence that repeats S6b, REWORD the three points (goal for "outcome", "Judge's", the TRANSFORM invariant clause), and COMPRESS the examples as listed above. S6a and S6b stay as KEEP.

Do you close S6a as KEEP, S6b as KEEP, and S6c as REMOVE + REWORD + COMPRESS?
`````

Catch:
`````text
"Applies when" - what do you think ?
`````


### ec3c9100-L373
- pattern: 4
- target: agents/executor-smart.md
- section: S6c — Pattern table (Law column heading)
- session: ec3c9100-fc97-4101-93d2-3c244bd44ced
- lines: proposal L371, catch L373

Proposal:
`````text
# S6c replacement table for your approval

I recorded S6a and S6b as KEEP. Here is the S6c table with all four verdicts applied.

```text
Tested:  redundancy — the DIAGNOSE sentence repeating S6b is gone; examples a
                      name already implies are cut ("a feature", "a schema or
                      version migration", "an intermittent failure", "an
                      implementation against acceptance criteria", "a design
                      against stated constraints").
         responsibility — "a refactor" now sits only under TRANSFORM, so
                      BUILD and TRANSFORM no longer claim the same work.
         coherence — clean; REVIEW's gate clause still matches Judge's
                      description and the constitution's GATE row.
         clarity — the header is "Applies when", and each row reads as a
                   condition on the task. "Outcome" became "goal" and
                   "result". "executor-judge's" became "Judge's". The
                   TRANSFORM clause now reads "a change whose effect on an
                   invariant you cannot establish".
```

```markdown
| Pattern | Applies when | Law |
|---|---|---|
| BUILD | the task creates a defined result and the implementation path needs judgment, such as an already-decomposed brief or spec, or a live job's setup and teardown within the boundary. | YAGNI: build only what the goal requires; no speculative abstraction, extension point, or infrastructure without evidence the boundary needs it. |
| TRANSFORM | the task changes an existing structure and the safe strategy needs judgment, such as a refactor that must preserve behavior, or an integration replaced without breaking consumers. | Invariant Preservation: preserve the explicitly required behavior, interfaces, data meaning, and other stated invariants while changing the implementation; stop before a change whose effect on an invariant you cannot establish. |
| DIAGNOSE | the task resolves an uncertain cause from a bounded symptom and evidence surface, such as a CI-only regression or inconsistent persisted state. | Falsification: treat explanations as hypotheses; seek evidence that can eliminate the leading hypothesis before investing in explanation or remediation. |
| REVIEW | the task evaluates an existing result or proposal against explicit criteria, such as a corpus against a fixed taxonomy. When an action that changes state others depend on waits on the verdict, the review is a gate: Judge's, not yours. | Normalization of Deviance: repeated deviation from the stated criteria is never evidence the deviation is acceptable; evaluate against the governing boundary, not local habit. |
```

The DIAGNOSE and REVIEW laws are unchanged. Fast and Fast-Read keep "Work", and that rename goes on the hand-off list as flagged only, not approved.

Do you approve this table?
`````

Catch:
`````text
Law - heading should we rename something to signal we need to apply the law - or is it already mentioned?
`````
