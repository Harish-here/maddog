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

LIMITATION — DELEGATION IS UNTESTABLE HERE: an agent dispatched by this harness runs inside a
Workflow and cannot itself dispatch a subagent — evidence: a 12-fixture run produced 5 failures,
all executor-lead, each stating in its own words "no delegation channel available" / "Task
disabled session-wide", while the same maddog:executor-lead dispatched maddog:executor-fast
successfully moments later when invoked directly outside a workflow. Any fixture whose expect/
rubric depends on delegation happening (marked "requiresDelegation": true in the fixture) cannot
be graded here: a delegation-dependent fixture fails for the environment, not the agent, and a
fix-leak trap that depends on tempting an agent to delegate a repair passes vacuously — the
temptation cannot exist. Such fixtures are skipped, not graded, until this harness can dispatch.

Scope a run with args.only (specific fixture ids) or args.agents (one agent's fixtures only) — both take the
bare agent name (executor-fast), same as the fixture files. Fixtures ship bare; installed agents are
namespaced (maddog:executor-fast), so dispatch translates bare -> namespaced with args.agentPrefix (default
'maddog:') right before agentType is built — override it for a fork or a differently-named marketplace
entry. A Preflight phase resolves every distinct agent the run will dispatch to, once, before Setup or Run
spends a token; an unresolvable agent aborts the whole run immediately with the agent name it tried and why.
Fixture work happens in per-fixture directories under workDir; those directories are left in place on purpose
so a human can inspect a failure afterward.`,
  phases: [
    { title: 'Load', detail: 'read both fixture files, build a lightweight index', model: 'haiku' },
    { title: 'Preflight', detail: 'resolve every distinct agent under test once, before any Setup/Run spends a token' },
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
const WORK_DIR = args?.workDir ?? '/tmp/maddog-eval-runs'

// Fixture id -> pinned run model. CLOSED mapping: haiku for executor-fast fixtures,
// sonnet for executor-smart fixtures, opus for executor-lead and executor-judge fixtures.
// An eval that let this inherit the session model would no longer measure the agent it claims to.
const RUN_MODEL = { 'executor-fast': 'haiku', 'executor-smart': 'sonnet', 'executor-lead': 'opus', 'executor-judge': 'opus' }

// Fixtures and args.agents stay bare ('executor-fast') — that's what a human types and what
// evals/*.json carry. Plugin-only distribution installs agents namespaced (maddog:executor-fast),
// so dispatch must translate bare -> namespaced right before the agentType field is built. The
// prefix is overridable so a fork or a differently-named marketplace entry doesn't need an edit here.
const AGENT_PREFIX = args?.agentPrefix ?? 'maddog:'
const namespaced = (bareName) => `${AGENT_PREFIX}${bareName}`

// A dropped fixture (harness error at any stage) must carry WHY, not vanish into a bare null —
// that's how a mass-drop read as "no failures" last time. Each stage catches its own errors and
// returns one of these instead of throwing; downstream stages pass it through untouched.
const mkDropped = (id, stage, reason) => ({ __dropped: true, id, stage, reason })
const isDropped = (v) => Boolean(v && v.__dropped === true)

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
          requiresDelegation: { type: 'boolean' },
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
  `Read these four fixture files fully: evals/executor-fast.json,
evals/executor-smart.json, evals/executor-lead.json, and
evals/executor-judge.json. For EVERY fixture in all four files, return only
its id, the file's top-level "agent" field (which agent it targets), the absolute path of the file it came
from, its own "core" boolean field, and its own "requiresDelegation" boolean field if present (default false
when absent). Do NOT return prompts, setup.files, or expectations — those are read
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
const scoped = index.fixtures.filter((f) => {
  if (!AGENTS.includes(f.agentName)) return false
  if (ONLY !== null) return ONLY.includes(f.id) // explicit only overrides core
  return RUN_ALL || f.core
})
const nonCoreSkipped = index.fixtures.filter((f) => AGENTS.includes(f.agentName) && ONLY === null && !RUN_ALL && !f.core).length

// Fixtures marked requiresDelegation cannot be graded by this harness — see the LIMITATION
// note in meta.whenToUse: a Workflow-dispatched agent cannot itself dispatch. Pull them out
// before Setup/Run spend a token; they get their own report section, never a pass/fail row.
const filtered = scoped.filter((f) => !f.requiresDelegation)
const delegationSkipped = scoped.filter((f) => f.requiresDelegation)

log(`running ${filtered.length} of ${index.fixtures.length} fixtures (${nonCoreSkipped} skipped as non-core, ${delegationSkipped.length} skipped as delegation-dependent — pass args.all to run everything non-delegation)`)
if (filtered.length + delegationSkipped.length < index.fixtures.length) {
  log(`filtered out ${index.fixtures.length - filtered.length - delegationSkipped.length} fixture(s) via args.agents/args.only/core`)
}
if (delegationSkipped.length > 0) {
  log(`delegation-dependent, not graded: ${delegationSkipped.map((f) => f.id).join(', ')}`)
}

// ---------------------------------------------------------------------------
// Preflight — resolve every DISTINCT agent this run will dispatch to, ONCE,
// before any Setup or Run stage spends a token. Evidence: a bare-name mismatch
// against namespaced agents cost 1.66M tokens across 41 setup calls before the
// first Run stage exposed it. A run that cannot dispatch must cost one call.
// ---------------------------------------------------------------------------
const distinctAgents = [...new Set(filtered.map((f) => f.agentName))]
if (distinctAgents.length > 0) {
  phase('Preflight')
  for (const bareName of distinctAgents) {
    const resolvedName = namespaced(bareName)
    let reason = null
    try {
      const probe = await agent('Reply with exactly the word ok and stop.', {
        label: `preflight-${bareName}`,
        phase: 'Preflight',
        model: RUN_MODEL[bareName] ?? 'haiku',
        effort: 'low',
        agentType: resolvedName,
      })
      if (probe === null) reason = 'dispatch returned no result'
    } catch (err) {
      reason = String(err?.message ?? err)
    }
    if (reason) {
      log(`preflight aborted the run — agent '${resolvedName}' (bare '${bareName}', prefix '${AGENT_PREFIX}') did not resolve: ${reason}`)
      return { aborted: 'preflight-agent-resolution', agent: resolvedName, bareAgent: bareName, prefix: AGENT_PREFIX, reason }
    }
  }
  log(`preflight ok — resolved ${distinctAgents.length} distinct agent(s): ${distinctAgents.map(namespaced).join(', ')}`)
}

// ---------------------------------------------------------------------------
// Phase 1 — per fixture: Setup (materialise files) -> Run (dispatch to the
// agent under test) -> Judge (grade). No barrier between stages; fixtures
// flow through independently. Every stage catches its own errors into
// mkDropped(...) instead of throwing, so a drop always carries an id, a
// stage, and a reason all the way to the report.
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
  )
    .then((setup) => setup ?? mkDropped(item.id, 'Setup', 'setup agent returned no result'))
    .catch((err) => mkDropped(item.id, 'Setup', String(err?.message ?? err))),
  // Run — the agent under test. Model and agentType are PINNED per fixture (see
  // RUN_MODEL above): never let this inherit the session model or omit
  // agentType, or the eval stops measuring the agent it claims to. Carries
  // setup forward alongside the raw text so Judge doesn't need a side-channel.
  (setup, item) => {
    if (isDropped(setup)) return setup
    if (!setup) return mkDropped(item.id, 'Setup', 'setup returned no result')
    const resolvedName = namespaced(item.agentName)
    return agent(
      `Your working directory is ${setup.dir}. All paths in this task are relative to it; work only inside it.\n\n${setup.prompt}`,
      {
        label: `run-${item.id}`,
        phase: 'Run',
        model: RUN_MODEL[item.agentName],
        // the variable under test — pinned, never inherited, or runs are not comparable
        effort: RUN_EFFORT,
        agentType: resolvedName,
      },
    )
      .then((raw) => (raw === null
        ? mkDropped(item.id, 'Run', `agent '${resolvedName}' returned no result`)
        : { raw, setup }))
      .catch((err) => mkDropped(item.id, 'Run', String(err?.message ?? err)))
  },
  // Judge — deliberately NOT one of the agents under test.
  (run, item) => {
    if (isDropped(run)) return run
    if (!run) return mkDropped(item.id, 'Run', 'run returned no result')
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
      .then((verdict) => verdict ?? mkDropped(item.id, 'Judge', 'judge agent returned no result'))
      .catch((err) => mkDropped(item.id, 'Judge', String(err?.message ?? err)))
  },
)

// outcomes[i] corresponds 1:1 to filtered[i] — zip so a drop keeps its fixture id even in the
// (unexpected) case the harness itself hands back a bare null instead of our mkDropped(...).
const zipped = filtered.map((item, i) => ({ item, outcome: outcomes[i] }))
const droppedList = zipped
  .filter(({ outcome }) => outcome === null || isDropped(outcome))
  .map(({ item, outcome }) => ({
    id: item.id,
    agent: item.agentName,
    stage: isDropped(outcome) ? outcome.stage : 'unknown',
    reason: isDropped(outcome) ? outcome.reason : 'harness returned null with no captured reason',
  }))
const verdicts = zipped
  .filter(({ outcome }) => outcome && !isDropped(outcome))
  .map(({ outcome }) => outcome)
const passed = verdicts.filter((v) => v.pass).length
const failed = verdicts.filter((v) => !v.pass)
const dropped = droppedList.length

// ---------------------------------------------------------------------------
// Phase 2 — report. Cheap, mechanical write-up; not one of the agents under
// test.
// ---------------------------------------------------------------------------
phase('Report')
const delegationSkippedList = delegationSkipped.map((f) => ({ id: f.id, agent: f.agentName }))
const reportPath = await agent(
  `Here is the full verdict array from an agent-evals run, as JSON: ${JSON.stringify(verdicts)}.
Here is the id -> agent mapping for every fixture attempted, as JSON: ${JSON.stringify(filtered.map((f) => ({ id: f.id, agentName: f.agentName })))}.
Here is the list of DROPPED fixtures — harness errors that never produced a verdict, NOT fixture failures —
as JSON: ${JSON.stringify(droppedList)}.
Here is the list of DELEGATION-SKIPPED fixtures — marked requiresDelegation: true in their fixture file,
never dispatched to Setup/Run/Judge because this harness cannot test delegation (see the LIMITATION note in
this workflow's whenToUse) — as JSON: ${JSON.stringify(delegationSkippedList)}.
Dropped count: ${dropped}. Delegation-skipped count: ${delegationSkipped.length}. Total fixtures attempted:
${filtered.length}. Passed: ${passed}. Failed: ${failed.length}.
Write a Markdown report to evals/last-run.md containing:
1. A summary line: passed/failed/dropped out of total. If dropped > 0, that line MUST open with a
   line reading exactly "WARNING: ${dropped} fixture(s) DROPPED — did not run to completion, results below
   are incomplete." in its own paragraph before the summary line — a dropped fixture must never read like a
   pass or blend silently into the total. If delegation-skipped count > 0, add a second line reading exactly
   "NOTE: ${delegationSkipped.length} fixture(s) SKIPPED as delegation-dependent — this harness cannot
   dispatch from within a Workflow, so these were never run and carry no pass/fail." immediately after.
2. If dropped > 0, a "## Dropped" section BEFORE the results table, one bullet per dropped fixture: id,
   agent, the stage it dropped at, and the captured reason, verbatim from the JSON above.
3. If delegation-skipped count > 0, a "## Skipped — delegation-dependent" section BEFORE the results table
   (after Dropped, if both present), one bullet per skipped fixture: id and agent, plus one line stating
   these are not graded — neither pass nor fail — because the harness cannot test delegation, per the
   LIMITATION note in whenToUse.
4. A results table with columns id | agent | pass | failed assertion (if any) — join verdicts to agent by id.
   Dropped and delegation-skipped fixtures do not appear in this table at all (no pass/fail cell of any kind)
   — they only appear in their own sections above.
5. A section listing each failure with its full reasoning and its working directory (under ${WORK_DIR}) so a
   human can go inspect it.
Return just the report's absolute path.`,
  { label: 'report', phase: 'Report', model: 'haiku', effort: 'low' },
)

const dropWarning = dropped > 0 ? ` — WARNING: ${dropped} fixture(s) DROPPED (harness error, not a fixture failure), see droppedDetail` : ''
const skipNote = delegationSkipped.length > 0 ? ` — NOTE: ${delegationSkipped.length} fixture(s) skipped as delegation-dependent, see delegationSkippedDetail` : ''
log(`run complete — ${passed} passed, ${failed.length} failed, ${dropped} dropped, ${delegationSkipped.length} delegation-skipped, ${filtered.length} total${dropWarning}${skipNote}`)
return {
  total: filtered.length,
  passed,
  failed: failed.length,
  dropped,
  droppedDetail: droppedList,
  delegationSkipped: delegationSkipped.length,
  delegationSkippedDetail: delegationSkippedList,
  failures: failed.map((v) => ({ id: v.id, mustFailures: v.mustFailures, mustNotViolations: v.mustNotViolations })),
  report: reportPath,
}
