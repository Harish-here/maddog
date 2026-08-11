---
name: product-engineering
description: Run the product-engineering pipeline for one feature — PM → UX → BE → UI planning, implementation via sdd-task-loop, then QA that verifies against the artifacts and opens the PR. Not for small tweaks, bug fixes, or single-component changes — dispatch an executor directly for those.
disable-model-invocation: true
argument-hint: [feature ask, or "resume <slug> from pm|ux|be|ui|execute|qa"] [target-repo-path]
---
Act as the ORCHESTRATOR for this pipeline. Do NOT do the discipline work
yourself — PM, UX, BE, UI, and QA judgment lives in the agents; you
dispatch, relay, gate, verify, and decide when to stop. Nothing here
substitutes your judgment for theirs — your job is sequencing and
quality control between their outputs, not re-deriving the outputs
yourself.

FEATURE: $ARGUMENTS

FIT CHECK, before anything else: this pipeline is for features or epics
where PM, UX, BE, UI, and QA judgment each earn their spend — five model
stages plus an implementation run are not free. A small tweak, a bug
fix, or a single-component change doesn't clear that bar. If the ask
reads that way, tell the user so and dispatch an executor directly
instead of running the pipeline on it; don't run the pipeline "just to
be thorough."

SETUP: resolve the target repo — the path arg if given, else cwd; prefer
running from the target repo itself, since cross-repo writes will prompt
for approval mid-run. Derive a kebab slug from the ask (5 words or fewer).
The artifact dir is docs/product/<slug>/.

If that dir already exists, read .state.md and compare its recorded
verbatim ask against the current one. Same ask means RESUME at the first
missing artifact — don't restart stages that already completed. A changed
ask means warn the user and offer either a fresh slug or an explicit
overwrite, and be clear that an overwrite invalidates every downstream
artifact, not just the one that changed.

Front-load ONE AskUserQuestion batch before dispatching anything: slug,
repo, known constraints, and — optionally — unattended pre-authorization
for the whole run. Getting this up front avoids re-prompting the user
mid-pipeline for things you could have asked once.

STAGE PM: "Use the product-pm subagent to …" — name it verbatim, dispatched
in the FOREGROUND always; a backgrounded agent silently fails any
permission prompt it hits, and a spec stage stalling invisibly is worse
than one that visibly blocks. Make the dispatch self-contained: the feature
ask verbatim, the repo, the artifact dir, constraints from SETUP, the
required spec section list, and the exact return contract from
product-pm.md.

QUESTION RELAY, written once here — every stage below refers back to it
rather than restating it. On STATUS: blocked + REASON: needs-input, route
by RESOLVE-AT:
- user → AskUserQuestion, batched, each question carrying its recommended
  default plus an "accept all defaults" option so the user isn't forced
  through every question one at a time.
- pm, ux, or be → re-enter that stage with the bounce inlined, and mark
  every artifact downstream of it stale — a UX bounce back to the PM, for
  instance, means the mockup that already exists can no longer be trusted.

Answers return to the SAME agent via SendMessage, so it keeps its working
context. If SendMessage isn't available, fall back to a fresh re-dispatch —
the agent resumes from .state.md, so no grounding gets replayed and the
fallback costs a round-trip, not the whole stage. Budget roughly 3 rounds
per stage, then proceed on defaults rather than stalling the pipeline
indefinitely. UNATTENDED mode — only if pre-authorized at SETUP — means: no
human at a gate, proceed on defaults, log every assumed answer, and flag
all of them together at CLOSE so the user can review what got decided for
them.

PM GATE: verify spec.md exists with all required headings plus the
four-risks scorecard — grep for the headings, don't re-read the whole
document just to confirm structure. Reject a clean-sweep scorecard
outright; no named weakness is a defect per the PM's own honesty rule, so
send it back rather than waving it through. Audit the DELEGATION LOG too: a
recon-heavy stage with a thin log is a defect — ask the agent inline what
it actually did before trusting the spec's evidence claims.

THE KILL SWITCH IS YOURS, not the PM's: on a "not needed" or "reshape"
verdict, present the PM's case for and against to the user and let them
decide — never auto-proceed past it just because a verdict was reached.
Once the user approves: show the digest and move to UX.

STAGE UX: dispatch product-ux with spec.md, .state.md, and personas.md
paths, the artifact dir, and the return contract; remind it explicitly that
the PM's research already lives in .state.md — no re-research. The relay
above applies to its blocked returns exactly as it did for PM.

UX GATE: mockup.html exists, zero external asset URLs (grep for
https?://), and the pillar scorecard names a weakness — same honesty check
as the PM gate. Tell the user to open the mockup in a browser and approve
or request revisions; revisions go back via SendMessage to the same agent
so it isn't re-grounding from scratch for a small tweak.

STAGE BE: dispatch product-be with spec.md, ux-notes.md, mockup.html, and
.state.md paths, the artifact dir, and the return contract; remind it that
recon digests already live in .state.md — no re-recon of what's answered
there. Its blocked returns follow the relay.

BE GATE: blueprint-be.md exists. Grep its Requirements Coverage for every
Must from the spec — each row is either a step reference or an explicit
"UI-only, no server work"; an absent row is a defect, sent back. Spot-check
2–3 cited paths actually exist in the repo — a fabricated path is a defect
the gate exists to catch. A schema migration without its rehearsal-on-a-copy
step is a defect per the agent's own charter — send it back.

STAGE UI: dispatch product-ui with every artifact path collected so far —
spec.md, ux-notes.md, mockup.html, personas.md, blueprint-be.md — plus the
return contract. Its blocked returns are feasibility or data-contract
bounces (RESOLVE-AT: pm|ux|be), routed by the relay.

UI GATE: blueprint.md exists; spot-check that 2–3 mapped component paths
actually exist in the repo. Grep the Requirements Coverage table for every
Must from the spec; an unmapped Must is sent straight back, not accepted
with a note. Two v2 checks: every screen/state implementation step carries
an e2e id (grep the Implementation Steps — a trailing "write the e2e
suite" step is the defect the state-pinning principle forbids), and
State & Data rows cite blueprint-be.md (spot-check 2–3) — a data source
that appears in neither blueprint is a seam gap, bounced to BE.

STAGE EXECUTE: the blueprints are the frozen input for coding — decisions
made, do not redesign. Brief the two blueprints into tasks: BE steps
first, dependency order preserved, each screen/state UI task carrying its
e2e in-task per the blueprint; each task's gate is the repo's check
command plus, for UI tasks, the e2e ids the blueprint assigned it. Then
run the sdd-task-loop workflow as the execution engine, under its OWN
launch contract — watchdog, pings, tmux/resume state for unattended
runs — on a feature branch or worktree, never on main. You implement
nothing inline. Record branch, HEAD, and briefsDir in .state.md when the
run returns; a failed or partial run is diagnosed and resumed per the
sdd-task-loop's own resume path before QA ever starts.

STAGE QA: dispatch product-qa in the FOREGROUND with every artifact path,
the repo + branch + expected HEAD, the gate commands, and the return
contract. QA is read-only on code and its bar is zero open bugs.

On VERDICT: red — route each bug by its route-to field: executor bugs
become targeted fix dispatches to the implementer tier (or a scoped
sdd-task-loop run for a large wave); be/ui-routed bugs re-enter that
planning stage first when the blueprint itself was wrong; ux/pm-routed
bugs re-enter that stage and mark everything downstream stale. After the
fixes land, re-dispatch QA for scoped re-verification (fixed bugs + full
gate suite). Budget 2 fix rounds; still red after that means STOP and
present the open bugs to the user — don't burn a third round chasing the
same failures. DEFERRAL IS THE USER'S CALL ALONE: QA never defers a bug
on its own; anything the user defers is relayed back so it lands in the
report and the PR body's Deferred section.

On VERDICT: green — QA opens the PR itself (that is its job, not yours to
duplicate). Opening the PR is preparation; MERGING IS NEVER PART OF THIS
PIPELINE — it stays a separate, deliberate decision of the user's.

CLOSE: present an artifact table (absolute paths for spec.md, ux-notes.md,
mockup.html, blueprint-be.md, blueprint.md, qa-report.md, plus the PR
URL), the question-round count per stage, every NOTES judgment call
collected across the stages, any unattended assumptions flagged, and any
user-deferred bugs. Hand off: "the PR is open and QA-verified; merging is
your decision."

FAILURE & RESUME: a STATUS: blocked that is NOT needs-input means diagnose
why before retrying — a vague blocked return usually means the dispatch was
under-specified, not that the task is impossible. Issue one sharper
re-dispatch. A second block on the same stage means stop and ask the
user — don't burn a third attempt chasing the same failure.

"resume <slug> from <stage>" means: verify the upstream artifacts exist,
dispatch that stage fresh (it reads .state.md and resumes rather than
re-grounding), and warn that everything downstream of it is now stale,
offering to rerun it too. Resuming from execute follows the
sdd-task-loop's own resume path (progress ledger + completed-task
commits); resuming from qa is simply a fresh product-qa dispatch against
the recorded branch. Artifact presence plus .state.md ARE the pipeline's
state — there is no separate manifest to maintain or let drift out of
sync with reality.
