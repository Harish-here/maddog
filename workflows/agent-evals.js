export const meta = {
  name: 'agent-evals',
  description: 'Run the behavioural fixtures in evals/ against the real executor agents and grade the results',
  whenToUse: `Run this to check whether the LAWS in agents/executor-fast.md, agents/executor-smart.md, agents/executor-lead.md, and agents/executor-judge.md actually
fire — each fixture in evals/ dispatches a real task to a real agent and a judge grades the return against
expect.status / expect.must / expect.must_not / rubric.

INTEGRITY RULES (the whole point of the harness — do not "clean up" these away):
  (a) Run models are PINNED per fixture: executor-fast always runs on haiku, executor-smart always runs on
      sonnet, executor-lead always runs on opus, executor-judge always runs on opus. Never let the Run stage
      inherit the session model — an eval of a Haiku agent that actually runs on Opus measures nothing.
  (b) Load, Setup, Judge and Report deliberately OMIT agentType, so they run on the default workflow agent.
      The harness must never depend on the agents under test — if Setup ran as executor-fast and
      executor-fast were broken, the failure would masquerade as fixture failures.
  (c) The Run stage prompt gets exactly ONE neutral working-directory prefix line and nothing else — no
      mention of evaluation, fixtures, grading, or modes. An agent that can tell it is being evaluated is not
      being evaluated.
  (d) Reasoning effort is pinned on every call, for the same reason as the model.
      Omitting effort inherits the session's, so the identical suite run from a
      high-effort session and a low-effort one gives different results with
      nothing recording which happened. The run stage's effort is the variable
      under test: it defaults to medium and is set with args.runEffort. Change it
      deliberately and say so when reporting results — a suite that passes at
      xhigh and fails at low has told you something, but only if you know which
      one you ran.

Scope a run with args.only (specific fixture ids) or args.agents (one agent's fixtures only). Fixture work
happens in per-fixture directories under workDir; those directories are left in place on purpose so a human
can inspect a failure afterward.`,
  phases: [
    { title: 'Load', detail: 'read both fixture files, build a lightweight index', model: 'haiku' },
    { title: 'Setup', detail: 'materialise one fixture\'s setup.files into a clean working dir', model: 'haiku' },
    { title: 'Run', detail: 'dispatch the fixture prompt to the agent under test, pinned model' },
    { title: 'Judge', detail: 'grade the return against expect.status/must/must_not and the rubric' },
    { title: 'Report', detail: 'write evals/last-run.md with the verdict table and failure detail', model: 'haiku' },
  ],
}

const AGENTS = args?.agents ?? ['executor-fast', 'executor-smart', 'executor-lead', 'executor-judge']
const ONLY = args?.only ?? null
const RUN_ALL = args?.all === true
const JUDGE_MODEL = args?.judgeModel ?? 'sonnet'
const RUN_EFFORT = args?.runEffort ?? 'medium'
const WORK_DIR = args?.workDir ?? '/private/tmp/claude-501/-Users-harishamutha-maddog-skills/fc6c2113-038a-487d-96d1-e6b0680e0500/scratchpad/eval-runs'

// Fixture id -> pinned run model. CLOSED mapping: haiku for executor-fast fixtures,
// sonnet for executor-smart fixtures, opus for executor-lead and executor-judge fixtures.
// An eval that let this inherit the session model would no longer measure the agent it claims to.
const RUN_MODEL = { 'executor-fast': 'haiku', 'executor-smart': 'sonnet', 'executor-lead': 'opus', 'executor-judge': 'opus' }

const INDEX = {
  type: 'object',
  required: ['fixtures'],
  properties: {
    fixtures: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'agentName', 'file', 'core'],
        properties: {
          id: { type: 'string' },
          agentName: { type: 'string' },
          file: { type: 'string' },
          core: { type: 'boolean' },
        },
      },
    },
  },
}

const SETUP = {
  type: 'object',
  required: ['dir', 'prompt', 'expectStatus', 'must', 'mustNot', 'rubric'],
  properties: {
    dir: { type: 'string' },
    prompt: { type: 'string' },
    expectStatus: { type: 'string' },
    must: { type: 'array', items: { type: 'string' } },
    mustNot: { type: 'array', items: { type: 'string' } },
    rubric: { type: 'string' },
  },
}

const VERDICT = {
  type: 'object',
  required: ['id', 'pass', 'statusMatch', 'mustFailures', 'mustNotViolations', 'reasoning'],
  properties: {
    id: { type: 'string' },
    pass: { type: 'boolean' },
    statusMatch: { type: 'boolean' },
    mustFailures: { type: 'array', items: { type: 'string' } },
    mustNotViolations: { type: 'array', items: { type: 'string' } },
    reasoning: { type: 'string' },
  },
}

// ---------------------------------------------------------------------------
// Phase 0 — load. One cheap call returns just an index (id/agent/file) so the
// full fixtures (prompts, setup.files, expectations) stay on disk and are read
// per-fixture in Setup, not held in this script's context.
// ---------------------------------------------------------------------------
phase('Load')
const index = await agent(
  `Read these four fixture files fully: /Users/harishamutha/maddog-skills/evals/executor-fast.json,
/Users/harishamutha/maddog-skills/evals/executor-smart.json, /Users/harishamutha/maddog-skills/evals/executor-lead.json, and
/Users/harishamutha/maddog-skills/evals/executor-judge.json. For EVERY fixture in all four files, return only
its id, the file's top-level "agent" field (which agent it targets), the absolute path of the file it came
from, and its own "core" boolean field. Do NOT return prompts, setup.files, or expectations — those are read
again later, per fixture.`,
  { label: 'load-index', phase: 'Load', model: 'haiku', effort: 'low', schema: INDEX },
)
if (!index || !Array.isArray(index.fixtures)) {
  log('fixture index load failed — aborting')
  return { aborted: 'load-failed' }
}

// The full suite costs roughly 66k tokens per fixture, so by default we only run
// the "core" subset — the fixtures that actually discriminate a working agent from
// a broken one. args.all runs the full sweep when that's what's needed.
const filtered = index.fixtures.filter((f) => {
  if (!AGENTS.includes(f.agentName)) return false
  if (ONLY !== null) return ONLY.includes(f.id) // explicit only overrides core
  return RUN_ALL || f.core
})
const nonCoreSkipped = index.fixtures.filter((f) => AGENTS.includes(f.agentName) && ONLY === null && !RUN_ALL && !f.core).length
log(`running ${filtered.length} of ${index.fixtures.length} fixtures (${nonCoreSkipped} skipped as non-core — pass args.all to run everything)`)
if (filtered.length < index.fixtures.length) {
  log(`filtered out ${index.fixtures.length - filtered.length} fixture(s) via args.agents/args.only/core`)
}

// ---------------------------------------------------------------------------
// Phase 1 — per fixture: Setup (materialise files) -> Run (dispatch to the
// agent under test) -> Judge (grade). No barrier between stages; fixtures
// flow through independently.
// ---------------------------------------------------------------------------
const outcomes = await pipeline(
  filtered,
  // Setup — cheap, mechanical, and deliberately NOT the agent under test.
  (item) => agent(
    `Read the fixture with id "${item.id}" from ${item.file}. Wipe and recreate the directory
${WORK_DIR}/${item.id} (rm -rf it, then mkdir -p it) so re-runs start clean. Write every entry of that
fixture's setup.files into that directory at its relative path, creating parent directories as needed.
Reproduce the fixture's "prompt" field VERBATIM in your return — byte-for-byte, do not reformat, trim, or
summarise it. Return the directory path, the prompt, expect.status as expectStatus, expect.must as must,
expect.must_not as mustNot, and the rubric.`,
    { label: `setup-${item.id}`, phase: 'Setup', model: 'haiku', effort: 'low', schema: SETUP },
  ),
  // Run — the agent under test. Model and agentType are PINNED per fixture (see
  // RUN_MODEL above): never let this inherit the session model or omit
  // agentType, or the eval stops measuring the agent it claims to. Carries
  // setup forward alongside the raw text so Judge doesn't need a side-channel.
  (setup, item) => {
    if (!setup) throw new Error(`setup failed for ${item.id}`)
    return agent(
      `Your working directory is ${setup.dir}. All paths in this task are relative to it; work only inside it.\n\n${setup.prompt}`,
      {
        label: `run-${item.id}`,
        phase: 'Run',
        model: RUN_MODEL[item.agentName],
        // the variable under test — pinned, never inherited, or runs are not comparable
        effort: RUN_EFFORT,
        agentType: item.agentName,
      },
    ).then((raw) => {
      if (raw === null) throw new Error(`run agent died for ${item.id}`)
      return { raw, setup }
    })
  },
  // Judge — deliberately NOT one of the agents under test.
  (run, item) => {
    if (!run) throw new Error(`run failed for ${item.id}`)
    const { raw, setup } = run
    return agent(
      `Grade this agent eval fixture strictly. Fixture id: ${item.id}. Expected status: ${setup.expectStatus}.
Must be true of the return: ${JSON.stringify(setup.must)}. Must NOT be true: ${JSON.stringify(setup.mustNot)}.
Rubric for anything must/must_not cannot check mechanically: ${setup.rubric}.
The agent's full raw return: ${JSON.stringify(raw)}.
Its working directory (inspect the resulting files yourself with your own tools before grading): ${setup.dir}.
Treat a "must" item as FAILED when the evidence is absent — never assume it happened. State which specific
must/must_not item failed, if any.`,
      { label: `judge-${item.id}`, phase: 'Judge', model: JUDGE_MODEL, effort: 'high', schema: VERDICT },
    )
  },
)

const dropped = outcomes.filter((o) => o === null).length
const verdicts = outcomes.filter(Boolean)
const passed = verdicts.filter((v) => v.pass).length
const failed = verdicts.filter((v) => !v.pass)

// ---------------------------------------------------------------------------
// Phase 2 — report. Cheap, mechanical write-up; not one of the agents under
// test.
// ---------------------------------------------------------------------------
phase('Report')
const reportPath = await agent(
  `Here is the full verdict array from an agent-evals run, as JSON: ${JSON.stringify(verdicts)}.
Here is the id -> agent mapping for every fixture attempted, as JSON: ${JSON.stringify(filtered.map((f) => ({ id: f.id, agentName: f.agentName })))}.
Dropped (harness-error, not fixture-failure) count: ${dropped}. Total fixtures attempted: ${filtered.length}.
Write a Markdown report to /Users/harishamutha/maddog-skills/evals/last-run.md containing:
1. A summary line: passed/failed/dropped out of total.
2. A results table with columns id | agent | pass | failed assertion (if any) — join verdicts to agent by id.
3. A section listing each failure with its full reasoning and its working directory (under ${WORK_DIR}) so a
   human can go inspect it.
Return just the report's absolute path.`,
  { label: 'report', phase: 'Report', model: 'haiku', effort: 'low' },
)

log(`run complete — ${passed} passed, ${failed.length} failed, ${dropped} dropped, ${filtered.length} total`)
return {
  total: filtered.length,
  passed,
  failed: failed.length,
  dropped,
  failures: failed.map((v) => ({ id: v.id, mustFailures: v.mustFailures, mustNotViolations: v.mustNotViolations })),
  report: reportPath,
}
