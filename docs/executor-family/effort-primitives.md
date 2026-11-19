# Effort primitives

STATUS: v1 foundation, approved by the maintainer on 2026-11-19. A theory:
checked on paper and by an independent judge, not yet by live runs.

This document fixes what a dispatching agent looks at in a piece of work
before it decides how much reasoning effort the receiving agent should
spend. It holds one definition and five questions. Rules that turn the
answers into an effort level are not here; they are built on top, version
by version, and may change. The definition and the questions may not.

## Definition

Effort is how much work the receiving agent puts into carrying the request
through and making sure the result is right.

Too little effort on work that needs it leaves the work unfinished or
wrong. Effort on work that does not need it is wasted, and sometimes makes
a small task worse.

## The five primitives

The dispatching agent answers each question about a piece of work at the
moment of handing it over, from the brief alone. No question names a
model, an effort level, or a tool.

### Size of the work

How many steps or parts must the receiver get through before it returns?

At lower effort a model stops before long work is done. "On long,
multistep tasks, Claude Fable 5.2 sometimes ends a turn before the work is
done ... This happens more often at `low` and `medium` effort."
([Prompting Claude Fable 5.2][fable])

### Difficulty

Does the work need working out, or is it routine?

On "a task that needs a few steps of working out ... the model often
answers without thinking first, particularly at `low` and `medium`
effort". The same guide adds: "When it skips thinking, it can be less
accurate on these tasks." ([Prompting Claude Sonnet 5.5][sonnet]) The best reasoning length
"increases with task difficulty but decreases with model capability".
([Wu and others, 2025][wu])

### Room for hidden error

Can the result look finished and still be wrong? This covers a missed case
and a wrong reading of a request that leaves choices open.

The reference article's main finding is that "higher effort is best for
tasks with lots of hidden edge cases." One benchmark task, an HTML
sanitizer, "went from 1/5 at low to 5/5 at xhigh".
([Spending your effort][article])

### Outside check

Will anything other than the receiver check the result before it is used?

One study found that "starting at the lowest effort and escalating only
after a verified failure, matches or improves on fixed top effort".
([Sun and others, 2026][sun]) Where nothing else checks, the receiver's own effort is the
only check: "without a user in the loop, high effort does better."
([Spending your effort][article])

### Cost of a miss

What is lost if a wrong result gets used?

More effort is worth its price for "complex tasks with high production
requirements such as performance optimization or security review".
([Spending your effort][article]) Effort allocation weighs "the expected
payoff from a controlled process" against its cost. ([Shenhav and others,
2013][shenhav])

### Where the primitives came from

The maintainer named four reasons a task needs effort: complexity, volume,
scale, and critical nature. Complexity is difficulty, volume and scale are
size, and critical nature is cost of a miss. Room for hidden error and
outside check come from the sources.

## Building on the primitives

- A later version adds or changes selection criteria. It never rewords a
  question.
- A change to the definition or to a question needs the maintainer's
  approval and an independent judge's ruling against the sources.
- A property of work that no question can describe is a finding. Report it
  before building around it.

Finished when a dispatcher can answer all five questions for a piece of
work without reading anything but its brief.

## v1 answer scales

Not part of the foundation. A later version may refine a scale without
touching its question.

| Primitive | Answers |
|---|---|
| Size of the work | few, many |
| Difficulty | routine, needs working out |
| Room for hidden error | none; the receiver can find it by checking its own work; only the dispatcher can tell |
| Outside check | yes, partly, no |
| Cost of a miss | low, high |

The hidden-error scale must keep its last two answers apart. Effort helped
most where the receiver could test its own result, for example with "a
randomized test against a reference". Where the error was a wrong reading,
more effort came with more failures: in the article's benchmark chart the
count labelled "picked the wrong reading" rose from 25 at the lowest level
to 47 at the highest. ([Spending your effort][article])

## Held back as later selection criteria

Each attaches on top of the five questions without rewording them.

| Criterion | Why it is held back |
|---|---|
| How the five answers combine into an effort level | no source states a rule |
| Time and token cost of each level, and how much speed and spend matter for this work | cost belongs to the level; the need for speed belongs to the surroundings |
| Cases where extra effort harms, not only wastes | measured, conditions still being mapped |
| Number and names of effort levels; each model's default | differs by model and release |
| Adjustment for model strength | a stronger model needs less reasoning for the same task |
| Task type, such as maths or logic | one meta-analysis |
| Start low, raise after a checked failure | a policy over outside check; one study |
| Cases fixed by a stronger model or a clearer brief, not effort | a routing decision |
| Effort chosen per step inside one task | one study |
| A long standing prompt on the receiver | a property of the receiving agent, reported for one model |
| Strict rule-following | reported for one model |
| Whether the receiver can ask questions during the work | one passage |
| Reliance on a prompt cache | limits when effort may change, not how much the work needs |

## What is established and what is not

Established:

- An independent judge ruled that the definition and the five questions
  meet the maintainer's intent, after checking every citation at its
  source. Each question decides a sourced case that no other question
  decides.
- Three agents listed, from the sources alone, what decides effort. Their
  lists led to the difficulty question; nothing else they named needed a
  sixth.
- Three agents answered an earlier four-question version for fifteen task
  descriptions and agreed on at least twelve of fifteen per question.

Not established:

- No live run has yet shown that an answer predicts where effort pays.
- The agreement test has not been repeated on the five-question version.
- No source measures effort on dispatched agents; the measured results
  come from single agents working alone.

## Open choices

- The rule that turns five answers into an effort level: the maintainer
  decides, after live tests.
- Whether the v1 answer scales stand: the maintainer decides, after the
  agreement test is repeated.
- Whether a dispatched agent can pass effort to an agent it dispatches: no
  one named; a live check decides.

[article]: https://claude.dev/blog/spending-your-effort/
[fable]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2
[sonnet]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5
[wu]: https://arxiv.org/abs/2502.07266
[sun]: https://arxiv.org/abs/2610.34491
[shenhav]: https://doi.org/10.1016/j.neuron.2013.07.007
