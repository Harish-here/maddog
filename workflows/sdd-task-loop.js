export const meta = {
  name: 'sdd-task-loop',
  description: 'Execute frozen plan briefs: lint gate, implementer per task (deps-aware), flagged reviews, end-of-plan review wave + one fix round, optional ship tail',
  whenToUse: `Advisor-mode plan execution once briefs are frozen and all design decisions are closed.
NOT for packages needing mid-flight design judgment — those go to executor-lead.
LAUNCH CONTRACT (advisor duties the script cannot do itself):
  1. BEFORE launching an unattended run, create the heartbeat/watchdog cron (progress ping +
     stall detection), send the run-start ping, and send the run-complete/aborted ping when
     the workflow returns — all via the same notifyCmd script the in-loop checkpoints use
     (default: ~/.claude/channels/telegram/notify.sh).
     Evidence: 2026-08-05 lost 11.8h to a host restart with no watchdog.
  2. Persist scriptPath + runId the moment the launch returns; on harness error or restart,
     try ONE resumeFromRunId (cached replay is free) before paging the human.
  3. Doc-sync stays advisor-supervised dispatch (it touches .claude/**, protected here).
  4. CI watch is a cron; merge is a separate deliberate invocation. Never bundle them.
  5. Unattended runs are hosted in the jobbunny-resume tmux session. At run START write
     ~/.claude/watchdogs/resume.state with mode=standing, resume_at=0, cwd, and a generic
     resume prompt pointing at the run-state memory file — a host restart then self-heals
     within 10 min of login (the watchdog-resume LaunchAgent relaunches; while the session
     lives, has-session keeps it silent). On a session-limit pause: bump resume_at to the
     reset epoch (plus the in-session wake cron); bump back to 0 on resume. DELETE the file
     at run close-out. Runs hosted outside that tmux session must NOT write a standing file
     (invisible to the has-session guard → duplicate sessions); they get the pause-time
     one-shot only.
  6. Verbatim-brief file artifacts: when a brief's steps CREATE new files with fully-specified
     source, the lead saves that source as real files under <briefsDir>/task-N-files/<repo-relative-path>
     and the brief's steps say copy-then-verify (TDD/gate/deviation steps unchanged). Modification
     edits keep fenced-block style (drift tolerance). Copy-then-verify briefs are prime haiku
     candidates via tasks[].model.`,
  phases: [
    { title: 'Brief lint', detail: 'cheap preflight: reject unfrozen briefs before any work', model: 'haiku' },
    { title: 'Implement', detail: 'one fresh implementer per brief; parallel where deps allow' },
    { title: 'Flagged review', detail: 'immediate gate for pipeline/security-flagged tasks' },
    { title: 'End review', detail: 'whole-plan review wave', model: 'opus' },
    { title: 'Fix wave', detail: 'one fix round + scoped re-review' },
    { title: 'Ship', detail: 'optional: push branch + raise PR (never merge)' },
  ],
}

// args: {
//   worktree:  absolute repo path (branch already checked out)
//   briefsDir: absolute path containing task-<n>-brief.md files + progress.md
//   tasks:     [{ n: 1, flagged: false, deps: [], model: 'haiku'|'sonnet' (optional) }, ...]
//              model = implementer tier for THIS task, decided by the plan/lead at
//              brief-authoring time. Default sonnet. Allowed set is closed (never
//              inherited); haiku is for briefs with ZERO deviation surface — fully
//              embedded source, no interface judgment. Flagged tasks refuse haiku.
//              deps = task numbers that must be DONE first. Omitted deps = depends on
//              every earlier task (the v1 sequential behavior, always safe).
//   gate:      shell command that must exit 0 after every task (e.g. 'bash -c "npm run check"')
//   baseRef:   git ref to diff against for the end review (e.g. 'main-everything-db')
//   parallelize: optional bool (default false) — run dependency-free tasks concurrently in
//              isolated worktrees, cherry-picked back in task order. Only enable when tasks
//              are file-disjoint by design; the merge gate re-runs after every pick.
//   ship:      optional { prTitle, prBase } — push the branch and raise a PR at the end.
//              Merge is NEVER part of this workflow.
//   protectedPaths: optional string[] — paths agents must never edit (default: CLAUDE.md + .claude**)
//   runName:   optional short label for checkpoint pings (default 'sdd-loop'), e.g. 'phase4'
//   notifyCmd: optional shell command for checkpoint pings (default:
//              bash "$HOME/.claude/channels/telegram/notify.sh"). The script is
//              fire-and-forget and always exits 0 — a dead network never fails the loop.
//              Pings ride on agents already running (they all have Bash): zero extra agents.
//              Template: 🔁 <run> · <emoji> <event> · <detail>
//                ✅ 7/11 task-7 done (a1b2c3d) · gate ✓     ⚠️ BLOCKED task-8 — <reason>
//                🔍 review: needs-fixes (1 critical, 3 important)   🔧 fix wave: 4 findings
//                🏁 PR raised <url>
//              Run-start / run-complete / stall pings are the LAUNCHER's job (see contract).
// }
//
// MODEL BUDGET (pinned here, never inherited — the 2026-08-05 session burned ~538k
// top-tier tokens because unpinned agents inherited the session model):
//   haiku  — brief lint, dossier, ship mechanics
//            + implementers explicitly pinned per task via tasks[].model (see above)
//   sonnet — implementers, fix rounds, task reviews, dimension reviews
//   opus   — adversarial synthesis, whole-plan review, scoped re-reviews (the only
//            places top intelligence is spent inside the loop)

const A = typeof args === 'string' ? JSON.parse(args) : args
if (!A || !Array.isArray(A.tasks)) throw new Error('bad args: tasks missing after normalization')

const TASK_RESULT = {
  type: 'object',
  required: ['task', 'status', 'commit', 'gateSummary', 'notes'],
  properties: {
    task: { type: 'number' },
    status: { enum: ['done', 'blocked'] },
    commit: { type: 'string' },
    gateSummary: { type: 'string' },
    deviations: { type: 'string' },
    notes: { type: 'string' },
  },
}

const REVIEW = {
  type: 'object',
  required: ['verdict', 'findings'],
  properties: {
    verdict: { enum: ['approved', 'needs-fixes'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'summary'],
        properties: {
          severity: { enum: ['critical', 'important', 'minor'] },
          file: { type: 'string' },
          summary: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
  },
}

const NOTIFY = A.notifyCmd ?? 'bash "$HOME/.claude/channels/telegram/notify.sh"'
const RUN = A.runName ?? 'sdd-loop'
// Agents send these themselves — keep messages free of quotes/backticks.
const ping = (msg) => `${NOTIFY} "${msg}"`

const discipline = `Worktree: ${A.worktree}. Run npm via bash -c wrappers; verify exits with echo EXIT:$?.
TDD per the brief's steps. Commit per the brief's message — NO co-author/attribution trailers.
Append your ledger line to ${A.briefsDir}/progress.md and write ${A.briefsDir}/task-<n>-report.md yourself (no separate bookkeeping).
If reality contradicts the brief (wrong line numbers are fine to resolve; contract/security/user-data mismatches are not), STOP and return status blocked with what you found.
NEVER edit these paths — if a finding or brief demands it, leave them untouched and put the proposed text in your report/notes instead: ${(A.protectedPaths ?? ['CLAUDE.md', '.claude/**', '**/AGENTS.md']).join(', ')}.`

// Per-task implementer tier: explicit, bounded, never inherited. Flagged
// (pipeline/security) tasks always get sonnet — the STOP-on-contradiction
// judgment is the whole point of the tier.
const TASK_MODELS = new Set(['haiku', 'sonnet'])
function taskModel(t) {
  if (t.model === undefined) return 'sonnet'
  if (!TASK_MODELS.has(t.model)) throw new Error(`task ${t.n}: model '${t.model}' not in [haiku, sonnet]`)
  if (t.flagged && t.model === 'haiku') throw new Error(`task ${t.n}: flagged tasks cannot run on haiku`)
  return t.model
}

// ---------------------------------------------------------------------------
// Phase 0 — brief lint. The loop's entry contract is FROZEN BRIEFS; this is the
// mechanical check that they actually are. Cheap model: it reads and pattern-
// matches, it does not judge design.
// ---------------------------------------------------------------------------
phase('Brief lint')
const LINT = {
  type: 'object',
  required: ['briefs'],
  properties: {
    briefs: {
      type: 'array',
      items: {
        type: 'object',
        required: ['task', 'frozen', 'problems'],
        properties: {
          task: { type: 'number' },
          frozen: { type: 'boolean' },
          problems: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}
const lint = await agent(
  `Lint these task briefs for execution-readiness — read each file fully: ${A.tasks.map((t) => `${A.briefsDir}/task-${t.n}-brief.md`).join(', ')}.
A brief is frozen ONLY if ALL hold: (1) self-contained — global constraints + the task, no reference to unstated decisions; (2) has an explicit DONE-WHEN; (3) states the gate command; (4) states the commit message; (5) contains NO open questions — flag any "TBD", "decide later", "TODO(decide)", unresolved "?" or "or maybe" phrasing, or placeholder text. Briefs may ship verbatim source as real files under ${A.briefsDir}/task-<n>-files/ referenced by copy-then-verify steps — verify every referenced artifact file EXISTS (list the directory); a missing referenced artifact file makes the brief NOT frozen. Do NOT judge design quality — only readiness. Return one entry per task.`,
  { label: 'brief-lint', phase: 'Brief lint', model: 'haiku', effort: 'low', schema: LINT },
)
const unfrozen = (lint?.briefs ?? []).filter((b) => !b.frozen)
if (unfrozen.length > 0) {
  log(`brief lint rejected ${unfrozen.length} brief(s) — aborting before any implementation`)
  return { aborted: 'brief-lint', unfrozen }
}

function implementerPrompt(t, worktree) {
  return `You are a fresh implementer for ONE task. Your brief: ${A.briefsDir}/task-${t.n}-brief.md — read it fully; it is self-contained (global constraints + your task).
${worktree === A.worktree ? discipline : discipline.replaceAll(A.worktree, worktree)}
DONE-WHEN: every step's expected result achieved, "${A.gate}" exits 0, commit exists.
CHECKPOINT PING (last action, fire-and-forget, ignore failures): on success run ${ping(`🔁 ${RUN} · ✅ ${t.n}/${A.tasks.length} task-${t.n} done (<short-sha>) · gate ✓`)} with <short-sha> replaced; on blocked run ${ping(`🔁 ${RUN} · ⚠️ BLOCKED task-${t.n} — <reason, ten words max>`)}.
Return: task=${t.n}, status, commit hash, gateSummary (test counts + exits), deviations, notes (judgment calls).`
}

function taskReviewPrompt(t, r) {
  return `Task-level review (this task is flagged pipeline/security). Worktree ${A.worktree}.
Brief: ${A.briefsDir}/task-${t.n}-brief.md. Implementer report: ${A.briefsDir}/task-${t.n}-report.md. Diff: git show ${r.commit}.
Check spec compliance, blast radius, failure modes, test honesty (no mocks-asserting-mocks). Verdict approved or needs-fixes with concrete findings.`
}

function fixPrompt(t, rev, scope) {
  return `Fix round (${scope}). Worktree ${A.worktree}. Apply ONLY these findings, nothing else:
${rev.findings.map((f) => `- [${f.severity}] ${f.file ?? ''}: ${f.summary}${f.fix ? ' — fix: ' + f.fix : ''}`).join('\n')}
For [critical] findings: FIRST write a failing test that reproduces the failure against the REAL components/code path (red), then fix it (green). A test built on synthetic fixtures the app never actually produces does not count as verification.
${discipline}
DONE-WHEN: findings addressed, "${A.gate}" exits 0, one commit.
CHECKPOINT PING (last action, ignore failures): ${ping(`🔁 ${RUN} · 🔧 fix (${scope}): <k> findings addressed (<short-sha>)`)} with placeholders filled.`
}

async function flaggedGate(t, r, results) {
  const rev = await agent(taskReviewPrompt(t, r), {
    label: `review-task-${t.n}`, phase: 'Flagged review', schema: REVIEW,
    agentType: 'executor-smart', model: 'sonnet',
  })
  if (rev.verdict !== 'approved') {
    const fix = await agent(fixPrompt(t, rev, `task ${t.n}`), {
      label: `fix-task-${t.n}`, phase: 'Flagged review', schema: TASK_RESULT,
      agentType: 'executor', model: 'sonnet',
    })
    const rerev = await agent(taskReviewPrompt(t, fix), {
      label: `rereview-task-${t.n}`, phase: 'Flagged review', schema: REVIEW,
      agentType: 'executor-smart', model: 'sonnet',
    })
    if (rerev.verdict !== 'approved') return { failed: rerev }
    results.push(fix)
  }
  return { failed: null }
}

// ---------------------------------------------------------------------------
// Phase 1 — implement. Default: strictly sequential (v1 behavior). With
// parallelize:true, tasks whose deps are all done run concurrently in isolated
// worktrees; a merge agent cherry-picks their commits back onto A.worktree in
// task order, re-running the gate after every pick (worktrees share the object
// store, so picking by hash works).
// ---------------------------------------------------------------------------
phase('Implement')
const results = []
const done = new Set()
const spentAtStart = budget.spent()

async function runSequential(t) {
  const tier = taskModel(t)
  let r = await agent(implementerPrompt(t, A.worktree), {
    label: `task-${t.n}`, phase: 'Implement', schema: TASK_RESULT,
    agentType: 'executor', model: tier,
  })
  if ((!r || r.status !== 'done') && tier === 'haiku') {
    // Escalation-on-red: one shot, haiku -> sonnet, same brief verbatim. Sequential path
    // only (the parallel branch keeps static tiers). A sonnet failure aborts as before.
    log(`task ${t.n}: haiku implementer blocked — escalating to sonnet`)
    const reason = (r && r.notes ? String(r.notes) : 'no result').slice(0, 200)
    r = await agent(
      `${implementerPrompt(t, A.worktree)}
ESCALATION CONTEXT: a cheaper prior attempt at this exact brief returned blocked/failed (reason, possibly truncated: ${reason}). Before Step 1: run git status in the worktree; if it is dirty with that attempt's uncommitted partials, reset to the last commit (git reset --hard + a git clean -fd scoped to the brief's own paths) and start from the last good commit. Include the word ESCALATED in your checkpoint ping.`,
      { label: `task-${t.n}-escalated`, phase: 'Implement', schema: TASK_RESULT, agentType: 'executor', model: 'sonnet' },
    )
  }
  if (!r || r.status !== 'done') return { blocked: r ?? null }
  results.push(r)
  done.add(t.n)
  log(`task ${t.n} done (${r.commit.slice(0, 8)}) — ${Math.round((budget.spent() - spentAtStart) / 1000)}k tokens spent this run`)
  if (t.flagged) {
    const g = await flaggedGate(t, r, results)
    if (g.failed) return { failedReview: g.failed }
  }
  return {}
}

if (!A.parallelize) {
  for (const t of A.tasks) {
    const out = await runSequential(t)
    if (out.blocked !== undefined) { log(`task ${t.n} blocked — aborting to advisor`); return { aborted: `task ${t.n}`, results, blocked: out.blocked } }
    if (out.failedReview) return { aborted: `task ${t.n} failed re-review`, results, review: out.failedReview }
  }
} else {
  const pending = [...A.tasks]
  while (pending.length > 0) {
    const ready = pending.filter((t) => (t.deps ?? pending.filter((p) => p.n < t.n).map((p) => p.n)).every((d) => done.has(d)))
    if (ready.length === 0) throw new Error(`dependency cycle or unsatisfiable deps among tasks ${pending.map((t) => t.n).join(',')}`)
    if (ready.length === 1) {
      const out = await runSequential(ready[0])
      if (out.blocked !== undefined) return { aborted: `task ${ready[0].n}`, results, blocked: out.blocked }
      if (out.failedReview) return { aborted: `task ${ready[0].n} failed re-review`, results, review: out.failedReview }
    } else {
      log(`running tasks ${ready.map((t) => t.n).join(', ')} in parallel (isolated worktrees)`)
      const batch = await parallel(ready.map((t) => () =>
        agent(implementerPrompt(t, '<your isolated worktree — you are checked out on a private copy>'), {
          label: `task-${t.n}`, phase: 'Implement', schema: TASK_RESULT,
          agentType: 'executor', model: taskModel(t), isolation: 'worktree',
        }).then((r) => ({ t, r }))))
      for (const b of batch.filter(Boolean).sort((x, y) => x.t.n - y.t.n)) {
        if (!b.r || b.r.status !== 'done') return { aborted: `task ${b.t.n}`, results, blocked: b.r ?? null }
        const merged = await agent(
          `In ${A.worktree}: git cherry-pick ${b.r.commit} (the commit exists in a sibling worktree sharing this repo's object store). Resolve NOTHING silently — if the pick conflicts, git cherry-pick --abort and return status blocked with the conflict summary. Then run "${A.gate}" and verify exit 0. Return task=${b.t.n}, status, the NEW commit hash on this branch, gateSummary, notes.`,
          { label: `merge-task-${b.t.n}`, phase: 'Implement', schema: TASK_RESULT, agentType: 'executor-fast', model: 'haiku' },
        )
        if (!merged || merged.status !== 'done') return { aborted: `merge of task ${b.t.n} conflicted — lower parallelism or fix deps`, results, blocked: merged ?? null }
        results.push(merged)
        done.add(b.t.n)
        if (b.t.flagged) {
          const g = await flaggedGate(b.t, merged, results)
          if (g.failed) return { aborted: `task ${b.t.n} failed re-review`, results, review: g.failed }
        }
      }
    }
    for (const t of [...pending]) if (done.has(t.n)) pending.splice(pending.indexOf(t), 1)
  }
}

// ---------------------------------------------------------------------------
// Phase 2 — end review (unchanged shape; dossier pinned to haiku)
// ---------------------------------------------------------------------------
phase('End review')
const DOSSIER = {
  type: 'object',
  required: ['files', 'insertions', 'deletions'],
  properties: {
    files: { type: 'number' },
    insertions: { type: 'number' },
    deletions: { type: 'number' },
  },
}
const dossier = await agent(
  `Build a review dossier for the branch in ${A.worktree}. Run: git diff --stat ${A.baseRef}...HEAD (capture the shortstat totals), git diff --name-status ${A.baseRef}...HEAD, git log --oneline ${A.baseRef}..HEAD. Read task-*-report.md and progress.md in ${A.briefsDir}. Write ${A.briefsDir}/review-dossier.md containing: the commit list, changed files grouped by area, per-task one-line summaries with commit shas, all judgment-ledger entries, and every deviation implementers reported. Do NOT review or judge — dossier only. When done, send a checkpoint ping (ignore failures): ${ping(`🔁 ${RUN} · 🔍 end review starting — <files> files, +<ins>/−<del>`)} with the real numbers. Return files/insertions/deletions as numbers from the shortstat.`,
  { label: 'review-dossier', phase: 'End review', agentType: 'executor-fast', model: 'haiku', effort: 'low', schema: DOSSIER },
)
// Fan-out criteria: one Opus reviewer reads everything up to ~60 files / ~8k changed
// lines — past that, single-context review goes shallow, so split into dimension
// readers (sonnet) and keep Opus for adversarial verify + synthesis only.
const isBig = dossier ? dossier.files > 60 || dossier.insertions + dossier.deletions > 8000 : false
let review
if (isBig) {
  const DIMENSIONS = [
    'contract fidelity: does the code match the briefs/spec, task by task',
    'repo invariants, security, and user-data safety',
    'test honesty: tests that pass against synthetic fixtures or mocks-asserting-mocks',
    'failure modes and blast radius: error paths, fail-soft vs fail-loud, silent degradation',
  ]
  const candidates = await parallel(
    DIMENSIONS.map((d, i) => () =>
      agent(
        `Dimension review #${i + 1} (${d}). Worktree ${A.worktree}; review git diff ${A.baseRef}...HEAD. Start from the dossier at ${A.briefsDir}/review-dossier.md, then read the real code — never judge from the dossier alone. Report findings ONLY for your dimension.`,
        { label: `review-dim-${i + 1}`, phase: 'End review', model: 'sonnet', schema: REVIEW },
      )),
  )
  const merged = candidates.filter(Boolean).flatMap((r) => r.findings)
  review = await agent(
    `Adversarially verify and synthesize these candidate findings against the actual code in ${A.worktree} (diff vs ${A.baseRef}): ${JSON.stringify(merged)}. Confirm each by reading the real code/tests — kill anything you cannot reproduce, especially findings whose only evidence is a test built on synthetic fixtures. Add anything critical the candidates missed in the seams BETWEEN dimensions. Verdict approved or needs-fixes; findings bucketed critical/important/minor with file + concrete fix. Last action (ignore failures): ${ping(`🔁 ${RUN} · 🔍 review: <verdict> (<n-critical> critical, <n-important> important, <n-minor> minor)`)} with the real verdict and counts.`,
    { label: 'review-synthesize', phase: 'End review', model: 'opus', effort: 'high', schema: REVIEW },
  )
} else {
  review = await agent(
    `Whole-plan review. Worktree ${A.worktree}; review git diff ${A.baseRef}...HEAD plus git log --oneline ${A.baseRef}..HEAD.
Start from the dossier at ${A.briefsDir}/review-dossier.md (commit map, per-task summaries, judgment ledger) so tool calls go to reading code, not discovering structure. Gates are already green — spend effort reading code: contract fidelity, invariants, security, test honesty.
Verdict approved or needs-fixes; findings bucketed critical/important/minor with file + concrete fix. Last action (ignore failures): ${ping(`🔁 ${RUN} · 🔍 review: <verdict> (<n-critical> critical, <n-important> important, <n-minor> minor)`)} with the real verdict and counts.`,
    { label: 'whole-plan-review', phase: 'End review', model: 'opus', effort: 'high', schema: REVIEW },
  )
}

phase('Fix wave')
let fixWave = null
let reReview = null
const actionable = review.findings.filter((f) => f.severity !== 'minor')
if (review.verdict !== 'approved' || actionable.length > 0) {
  fixWave = await agent(fixPrompt({ n: 'wave' }, { findings: actionable }, 'whole-plan fix wave'), {
    label: 'fix-wave', schema: TASK_RESULT, agentType: 'executor', model: 'sonnet',
  })
  reReview = await agent(
    `Scoped re-review: verify ONLY that these findings are correctly fixed in ${fixWave?.commit} (worktree ${A.worktree}), no new defects:
${actionable.map((f) => `- ${f.summary}`).join('\n')}`,
    { label: 'scoped-rereview', model: 'opus', schema: REVIEW },
  )
}

// ---------------------------------------------------------------------------
// Phase 3 — optional ship tail: push + PR only. Doc-sync is deliberately NOT
// here (it edits .claude/**, protected for workflow agents — advisor dispatches
// it). Merge is NEVER here.
// ---------------------------------------------------------------------------
let ship = null
const approved = (reReview ?? review).verdict === 'approved'
if (A.ship && approved) {
  phase('Ship')
  ship = await agent(
    `In ${A.worktree}: push the current branch to origin (git push -u origin HEAD), then raise a PR with gh: base ${A.ship.prBase}, title ${JSON.stringify(A.ship.prTitle)}. Body: summarize from ${A.briefsDir}/review-dossier.md (commits, areas touched, review outcome) — NO co-author or attribution lines. Do NOT merge, do NOT watch CI. Last action (ignore failures): ${ping(`🔁 ${RUN} · 🏁 PR raised <url> — awaiting CI + merge decision`)} with the real URL. Return task=0, status, commit=PR URL in the commit field, gateSummary='pr raised', notes.`,
    { label: 'ship-pr', phase: 'Ship', schema: TASK_RESULT, agentType: 'executor-fast', model: 'haiku' },
  )
} else if (A.ship && !approved) {
  log('ship tail skipped — final review not approved')
}

log(`run complete — ${Math.round((budget.spent() - spentAtStart) / 1000)}k output tokens this workflow`)
return { results, review, fixWave, reReview, ship }
