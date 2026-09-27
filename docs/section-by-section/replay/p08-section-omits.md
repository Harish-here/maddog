# Pattern 8 — Section omits something its own question needs

### 137dd3e7-L1171
- pattern: 8
- target: agents/executor-lead.md
- section: S6 — Work Patterns
- session: 137dd3e7-e797-4768-a264-fc98976946ff
- lines: proposal L1169, catch L1171

Proposal:
`````text
## S5 is closed. S6 is next.

```
S6 — Work Patterns (lines 95–124)
Does: names the four ways Lead works, gives each a flow and one law, and
      says what happens to a plan once it is frozen.
Fails: format test. Four parallel cases sit in prose paragraphs, and each
       case has the same three parts.
Verdict: RESHAPE into a table. Evidence: O1, O2.
```

**Draft:**

> ## Work Patterns
>
> Four patterns combine freely in one package, with no transition ceremony; evidence decides which comes next, never an earlier plan. Hold each pattern's law while in it; core laws outrank them.
>
> | Pattern | Flow | Law |
> |---|---|---|
> | PLAN | open objective → investigate → decide → frozen plan | Last Responsible Moment: never freeze a decision while cheap evidence could still change it, nor a step that leaves a decision open for its hand. |
> | CAMPAIGN | probe → evidence → updated judgment → next move, repeated | Value of Information: never run a probe whose plausible results all lead to the same next move; name first the result that would end the path. |
> | DIAGNOSE | symptom → hypotheses → targeted evidence → cause, when the investigation itself evolves | Multiple Working Hypotheses: never commit to a cause the evidence has not separated from its live rivals. |
> | DELIVER | decided outcome → decompose → dispatch → integrate | Fallacy of Composition: never report the package done because every slice passed; verify the integrated result against the success condition. |
>
> After PLAN, classify each frozen step by shape; an evolving step stays yours. If none is evolving, return the plan to Advisor with each step classified, unless integrating the steps needs judgment carried across them or the dispatch asked you to deliver.

### What changed and why

- **This section is Lead's main quirk, so I cut little.**
  - All four laws stay with their names.
  - Each name points the model at a known idea, so it carries a lot of meaning in a few words.
- **Added four words to the intro: "never an earlier plan".** They keep the core of law 4, which S5 just removed.
- **Dropped from PLAN: "mechanical → Fast, bounded → Smart".** The shared shape table already says it. I kept "an evolving step stays yours". The table sends evolving work to "Lead", and this clause tells Lead that means itself.
- **Dropped from DIAGNOSE: "a bounded symptom with a known evidence surface is Smart's".** The shape table's BOUNDED row says the same thing.
- **Dropped from DELIVER: "return to PLAN or CAMPAIGN when live evidence changes the path".** The intro sentence now covers it.
- **Words:** 193, down from 231. The running total is about 1,560.

Do you close S6 as RESHAPE with this text?
`````

Catch:
`````text
[...] And also we have force thinking before proceeding it should classify the what actions might invloves- what do you think;
`````


### 01c6d363-L211
- pattern: 8
- target: skills/section-by-section/SKILL.md
- section: S5a — Check three things
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L197, catch L211

Proposal:
`````text
Start is closed. Now into the loop itself, which is where the seven sub-sections begin. **Section 5 of 14.**

```text
S5a — Check three things (lines 72–76)
Does: opens the loop with "for each in-scope section, in file order", then
      defines the three checks every diagnosis uses.
Fails: clarity, test 5 — three parallel definitions written as one run of
      prose.
Verdict: RESHAPE. Evidence: —
```

[...]

**Your call: RESHAPE, or a different verdict.**
`````

Catch:
`````text
Choerence - do we need to add this? How unique? no overalpp? - All these are covered or not? like wise do we need to expand the check things?
`````


### 01c6d363-L317
- pattern: 8
- target: skills/section-by-section/SKILL.md
- section: S5f — Draft (missing Approve step)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L309, catch L317

Proposal:
`````text
You found a real hole, and it is bigger than compression.

## The hole

- Every verdict is a one-word order. Nothing in the file says what the resulting text must satisfy.
- COMPRESS says fewer words and stops there. Nothing forbids a shorter line that no one can read, which is exactly what my preamble line was until you caught it.
- The same is true of REWORD, RESHAPE, REPLACE, SPLIT and MERGE. All six produce text, and none of them states a bar for that text.

## Where it belongs

The Draft step, which is where every verdict's text actually gets written. [...]

```text
Replacement text must survive the axes that judged the section: it carries the
meaning whole, answers one question, contradicts nothing, and can be acted on
without interpretation. Fewer words that cost comprehension are not a
compression. Where a shorter line has to be decoded, keep the longer one.
```

[...]

**Do you want that drafting rule closed now, or when we reach the Draft step?** Holding it costs nothing; it is already written down here.
`````

Catch:
`````text
We can hold it there but i'm approvin the draft every turn right so model needs to go thru axes when it present to me right?
`````


### 01c6d363-L521
- pattern: 8
- target: skills/section-by-section/SKILL.md
- section: S6b — Assembly steps
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L515, catch L521

Proposal:
`````text
**Section 13 of 15.**

```text
Section:  S6b — Assembly steps (lines 140–160)
Does:     seven steps that resolve what the loop left open and compose the
          final file.
Fails:    clarity — three steps rename axes the loop already named, and one
          step carries two instructions.
Verdict:  REWORD
Evidence: —
```

## The naming problem

- Step 2 is called "resolve ownership", step 3 "resolve cross-section redundancy", step 4 "resolve contradictions".
- Those are the responsibility, redundancy and coherence axes. The loop now names all three, and Assembly calls two of them something else.
[...]

## The overloaded step

Step 7 says two things. Write the file in the closed order [...] And keep it under a size ceiling, forking the heaviest tables and examples into a `references/` file. [...]

**Your call: REWORD, or a different verdict.**
`````

Catch:
`````text
Lets discuss about the how this is formed first - We are checking text section by section like small lego pieced in this section only we're finalling checking where all the lego piecced that we craft are making sense as a single picture together liek fitting well each other and find strutural flaw/gaps/questions that it not anwered. one way of we are doing is evey sections should answer uniquer questions. all of them are arranges in progress disclosure manner (LAW) and aslo can we incporate any thing from this article

<pasted_content id="7ea1">
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
</pasted_content id="7ea1">

 . so keep all this in the mind now review this sections
`````


### 01c6d363-L1268
- pattern: 8
- target: skills/section-by-section/SKILL.md
- section: DESC (frontmatter description) vs. S6b step 8 (Hold the size)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L613, catch L1268

Proposal:
`````text
## The description, tested

It is third person, it says what the skill does and when to use it, and it is well under the length limit. One line of it clashes with what we built: it says this is "not for shaping a file by how long it stays loaded", and Assembly step 8 now caps the body at 500 lines and forks the overflow.

My reading is that they do not actually conflict. The disclaimer is about why you reach for the skill; step 8 is about what the run does on its way out. But it is a coherence hit and the rule says you close it.
`````

Catch:
`````text
[...]
Biggest conceptual issue

The skill mixes review methodology with artifact production policy

[...]

This is especially visible here:

> "Body under 500 lines."

and:

> "Fork the heaviest tables and examples one level down..."

That is a formatting policy.

Your own description says:

> "Not for shaping a file by how long it stays loaded — that is a separate formatting pass."

Yet Assembly still imposes line-count and reference-forking rules.

Contradiction.

I would remove all size/forking policy from this skill.
`````


### babf14f7-L141
- pattern: 8
- target: skills/advisor-mode/SKILL.md
- section: S3 — Operate (the loop)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L138, catch L141

Proposal:
`````text
Section:   S3 — ## Operate (lines 34–39), the LOOP fragment
Does:      Names six stages of a session and says the loop re-enters at CLASSIFY
           until the outcome is met
Elsewhere: Every stage name is a pointer to a section that already exists.
           CLASSIFY and the hand it picks live in S5. DISPATCH's contents live
           in S6. EVALUATE lives in S7a and S7b. DONE restates S2a's first law
Fails:     clarity — six parallel stages, written as a bare arrow line with no
           code fence, no definitions, and no actors. The form does not match
           the content
Also:      responsibility fired once: the loop says "the next slice" but no stage
           produces a slice
Verdict:   RESHAPE
Evidence:  O1, O2, O3, O4
`````

Catch:
`````text
ASSIGN out SLICE in, take the loop text and the S1 line. The explain of the of each should be a separate section. we missed a text saying this loop is every turn - or it is not needed?
`````


### babf14f7-L288b
- pattern: 8
- target: skills/advisor-mode/SKILL.md
- section: S7a — Evaluate (VERIFY)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L285, catch L288

Proposal:
`````text
A return is evidence, not proof. Check it against DONE-WHEN. Verify
load-bearing claims at the primary evidence cited: spot-check the source,
re-run the gate, or, for an absence claim, check its search pattern and
scope. Redoing the work is not verification. Keep observed, produced, and
concluded apart.
`````

Catch:
`````text
[...] Wet Evaluate - advisor should avosi the ceremony of checking already implemented works - make sure that is reflected in the text
`````


### babf14f7-L356
- pattern: 8
- target: skills/advisor-mode/SKILL.md
- section: S7b — Evaluate (the five verdicts)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L331, catch L356

Proposal:
`````text
valid       → ACCEPT
incomplete  → CONTINUE, same owner
wrong shape → REROUTE
blocked     → RESOLVE, else ESCALATE
gate needed → JUDGE
`````

Catch:
`````text
take Done, S9 reword, drop the Dispatch line. Did we mention the evalute can got it slice again as we mentioned ij the loop?
`````


### d8a02f04-L768
- pattern: 8
- also: 9
- target: agents/executor-lead.md
- section: S7 — Classify
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L766, catch L768

Proposal:
`````text
Section:   S7 — Classify (83–91)
Does:      The PATTERNS fragment: classify the work's patterns before the
           first tool call, treat a named pattern as a hint, core laws
           outrank pattern laws, and work that fits no pattern is not
           yours: return it. Then Lead's own line: evidence picks the next
           pattern; reclassify with no ceremony.
Verdict:   KEEP — O3 carried to S16 with G2
`````

Catch:
`````text
yes, close S7 as KEEP but drop "work patterns" heading and make sure the mulitple pattern can be applicable wehn slice for on out come and then evolving slices can alspo have new working patter - what aodyou think ?
`````


### f09ade50-L119
- pattern: 8
- target: agents/executor-fast-read.md
- section: S1 — Role opening
- session: f09ade50-46a3-4137-938b-80a10f28fa69
- lines: proposal L117, catch L119

Proposal:
`````text
## S1: proposed verdict is REWORD + COMPRESS

From here on, every section's diagnosis will list every verdict that applies, with the main one first. Checking S1 against every verdict found one more than before. "With no judgment" says again what "as found" and the next sentence already say.

```text
Section:   S1 — Role opening (lines 17–20)
Does:      names the role, gives it one question answerable as found, leaves meaning with the dispatcher, states its limits
Elsewhere: DESC routes any run, "even a read-only command", to Fast; law 2 (S6) stops on a missing capability; law 1 (S5) forbids conclusions. Constitution: OPENING pattern (name, own, edge, limits); P30 puts "holds no shell, can change nothing" in the OPENING limit; P13 gives "cannot ask" and "you finish by returning".
Verdicts:  REWORD — the limits omit "run", which P30 places here; "wait" can read as "wait on a process" and traces to no property
           COMPRESS — ", with no judgment" repeats "as found" and the edge sentence ("what it means stays with whoever dispatched you")
Checked, not firing: REMOVE, SPLIT, MERGE, MOVE, coherence, REPLACE (no evidence), RESHAPE
Evidence:  —
```

**Proposed text:**

```text
Tested:  redundancy — ", with no judgment" dropped; "as found" and the edge sentence carry it
         responsibility — clean
         coherence — law 2 already stops on a missing capability, and running is one; clean
         clarity — "wait" removed; "ask" becomes "ask for input", as in Fast's opening; "run or change anything" names both limits in one phrase
```

```markdown
You are EXECUTOR-FAST-READ. You own one closed question: one the sources
can answer as found. You report what they show; what it means stays with
whoever dispatched you. You cannot ask for input, run or change anything,
and you finish by returning.
```

Name the verdicts you close S1 on, for example "S1: REWORD + COMPRESS, text approved". Or name the ones you reject, such as keeping ", with no judgment".
`````

Catch:
`````text
Should we need to add that it should not synthesisi the info it should produce excatly what it fouund - is the sentnece tight / strict enough to say that
`````


### f09ade50-L447
- pattern: 8
- target: agents/executor-fast-read.md
- section: S1 — Role opening
- session: f09ade50-46a3-4137-938b-80a10f28fa69
- lines: proposal L117, catch L447

Proposal:
`````text
## S1: proposed verdict is REWORD + COMPRESS

[...]

```markdown
You are EXECUTOR-FAST-READ. You own one closed question: one the sources
can answer as found. You report what they show; what it means stays with
whoever dispatched you. You cannot ask for input, run or change anything,
and you finish by returning.
```

Name the verdicts you close S1 on, for example "S1: REWORD + COMPRESS, text approved". Or name the ones you reject, such as keeping ", with no judgment".
`````

Catch:
`````text
Btw in the opening we didn't say you have only read ability?
`````
