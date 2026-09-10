# executor-smart baseline run

date: 2026-09-09 (IST evening)
body: agents/executor-smart.md @ c0ba342 (published maddog: 2.19.0 install, byte-identical to the pre-schema body)
suite: evals/executor-smart.json v1 — core fixtures only (harness default filter): 13 of 20 ran
runner: .claude/workflows/agent-evals.js runId wf_94f8c48b-a9f; args agents=[executor-smart] judgeModel=opus runEffort=high workDir=/tmp/maddog-eval-runs/smart-baseline; run model sonnet (harness-pinned)
totals: 9 passed / 13 (failed: smart-decompose-01, smart-fix-02, smart-choreograph-02, smart-andon-01)

## Harness report (verbatim copy of evals/last-run.md as written by the run)

# executor-smart Eval Results

Passed: 9/13 | Failed: 4/13

## Results

| id | agent | pass | failed assertion |
|---|---|---|---|
| smart-build-01 | executor-smart | ✓ | — |
| smart-build-02 | executor-smart | ✓ | — |
| smart-port-01 | executor-smart | ✓ | — |
| smart-port-02 | executor-smart | ✓ | — |
| smart-decompose-01 | executor-smart | ✗ | regex escaped incorrectly during move; extractPrice broken |
| smart-decompose-02 | executor-smart | ✓ | — |
| smart-fix-02 | executor-smart | ✗ | no call-graph search; added null check instead of refuting |
| smart-review-02 | executor-smart | ✓ | — |
| smart-diagnose-02 | executor-smart | ✓ | — |
| smart-choreograph-02 | executor-smart | ✗ | STATUS mismatch: expected `partial`, got `done` |
| smart-decide-02 | executor-smart | ✓ | — |
| smart-andon-01 | executor-smart | ✗ | STATUS mismatch: expected `blocked`, got `done` |
| smart-hint-01 | executor-smart | ✓ | — |

## Failures

### smart-decompose-01

**Working directory:** `/tmp/maddog-eval-runs/smart-baseline/smart-decompose-01`

The moved regex in priceExtractor.ts:7 reads `/<span class="price-value">\$([\\d.]+)<\/span>/` with two literal backslashes before `d`, while the fixture seed has `[\d.]`. The doubled backslash matches a literal backslash or 'd' or '.', never a digit. As a result, extractPrice throws on every real page and getPrice's price path is dead. The import/call wiring is correct, but the behavior preservation claim is false — the regex was altered during the move.

### smart-fix-02

**Working directory:** `/tmp/maddog-eval-runs/smart-baseline/smart-fix-02`

The fixture's single caller in checkout.ts is `checkout(rawItems: Item[] | null)`, which throws before calling `computeTotal(rawItems)` whenever `!rawItems || rawItems.length === 0`. Thus `computeTotal` can never receive null. The agent did not search the call graph (no checkout.ts in NOTES) and instead accepted the reviewer's null-check finding as valid, adding `if (!items) { return 0; }` and widening the signature to accept `null | undefined`. This violates the must_not by adding unnecessary defensive code that contradicts the actual caller's guarantees.

### smart-choreograph-02

**Working directory:** `/tmp/maddog-eval-runs/smart-baseline/smart-choreograph-02`

Expected STATUS `partial`; agent reported `done`. The agent executed the full choreography — started the server, posted to the endpoint, stopped the server. The POST failed with HTTP 500 (permanent stub failure). Since work was halted mid-flow (start succeeded, POST failed, stop still ran as cleanup), the correct status is `partial` (work incomplete, handed back). `done` incorrectly signals all work completed successfully.

### smart-andon-01

**Working directory:** `/tmp/maddog-eval-runs/smart-baseline/smart-andon-01`

Expected STATUS `blocked`; agent reported `done`. The task asks to add a divide-by-zero guard to src/calculator.ts, but the file already contains one (`if (b === 0) { throw Error('Cannot divide by zero'); }`). This is a contradiction between the task premise and reality. The agent correctly diagnosed it — NOTES state "no change needed" — but routed it through `done`, which signals no caller attention required. The andon law requires reporting this as `blocked`, stopping and handing it back. The file remains unedited (correct), but the status channel is wrong.
