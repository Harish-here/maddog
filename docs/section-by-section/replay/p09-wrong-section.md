# Pattern 9 — Sentence in the wrong section

### babf14f7-L869
- pattern: 9
- target: agents/executor-lead.md
- section: Lead outline (Work Patterns / Classify)
- session: babf14f7-34d2-4421-b354-977458b8f90e
- lines: proposal L848, catch L869

Proposal:
`````text
- **Option B — propagate and mirror the stages.** The Lead carries the same loop, so its body would run Outcome, Slice, Classify, Dispatch, Evaluate, Done, with Work Patterns and Return staying as their own sections outside the loop. Same shape as advisor-mode and `executor-judge`.
`````

Catch:
`````text
Option B- But Work pattern is CLASSIFY
`````


### d8a02f04-L229
- pattern: 9
- target: skills/advisor-mode/SKILL.md
- section: S7 — Classify
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L222, catch L229

Proposal:
`````text
### Classify

Route by judgment shape, not size, difficulty, or subject. Mechanical work
ALWAYS goes to the Fast tiers: Fast-Read to read, Fast to change or run.
Once a hand owns a slice, never do its next step yourself; to change
course, wait for its return, or stop it and REROUTE. Pass a hand no more
authority than held.

| Shape | Hand | When |
|---|---|---|
| READ | Fast-Read | facts as found; no judgment |
| MECHANICAL | Fast | decisions all closed |
| BOUNDED | Smart | local judgment: implementation choice, criteria review, diagnosis with a known evidence surface |
| GATE | Judge | the Gate ladder below calls for an independent verdict |
| EVOLVING | Lead | next action depends on discovery |

The one exception to the Fast tiers is work so small that dispatching it
costs more than doing it, such as a single command whose output you need
now. That you do yourself, and it is rare; anything larger follows Dispatch
First.
`````

Catch:
`````text
'the execption text..' is it the right place as of now we're taking about the classification alone
`````


### d8a02f04-L359
- pattern: 9
- target: skills/advisor-mode/SKILL.md
- section: S11 — Evaluate
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L357, catch L359

Proposal:
`````text
### Evaluate

A return is evidence, not proof. Check it against DONE-WHEN. Verify
load-bearing claims at the primary evidence cited: spot-check the source,
re-run the gate, or, for an absence claim, check its search pattern and
scope. Redoing the work is not verification; a claim you or a Judge already
cleared at its evidence needs no second pass. Keep observed, produced, and
concluded apart.

| Result | Verdict |
|---|---|
| valid | ACCEPT, then SLICE or DONE |
| incomplete | CONTINUE, same owner |
| wrong shape | REROUTE |
| blocked | RESOLVE when the block is yours to clear (a decision, fact, or grant you hold), then dispatch again; otherwise ESCALATE |
| gate needed | JUDGE |

CONTINUE resumes a hand only while its task, boundary, and context still
hold and resuming still beats a fresh start; idle time erodes that. A fresh
hand starts from a written summary of state, never a transcript.

You accept a Lead's return whole; the routing inside it was the Lead's.
`````

Catch:
`````text
Does this continue seems out of place isn't ? Because reason we i have this text is resue the hand which has already contetx about that slice so we alredy paid for that task if next slice if task has overlapp or neede prirpr conetxt or sub slice of prevsiou one then we need to use the same hand just that we need to make sure it should be in usable state which not full context exhausted. The resume should be depends on the next slice. - Lets thingk in this directipon
`````


### d8a02f04-L467
- pattern: 9
- also: 4
- target: skills/advisor-mode/SKILL.md
- section: Outline (Assembly)
- session: d8a02f04-bf9a-4dd7-abc5-467e17729f03
- lines: proposal L465, catch L467

Proposal:
`````text
DESC
## Role                      S1
### Family Laws              S2
### Core Laws                S3
## Uncertainty               S13   ← moved from after Done
## Operate                   S4
### Outcome                  S5
### Slice                    S6
### Classify                 S7
#### Gate                   S8
### Dispatch
#### Dispatch First         S9
#### Resume or fresh        S11b  ← moved from Evaluate
#### Contract               S10
### Evaluate                 S11a
### Done                     S12   ← last in the file
`````

Catch:
`````text
Does undertanity dserves a section ?
`````
