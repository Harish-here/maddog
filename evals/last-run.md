# Agent Evals: Last Run Report

**Summary:** 10 passed, 2 failed, 0 dropped out of 12 total

---

## Results Table

| id | agent | pass | failed assertion (if any) |
|---|---|---|---|
| smart-build-01 | executor-smart | ✓ | — |
| smart-build-02 | executor-smart | ✓ | — |
| smart-fix-02 | executor-smart | ✗ | Must: reports finding as not applicable/refuted; Must-not: adds null check inside computeTotal |
| smart-review-02 | executor-smart | ✓ | — |
| smart-diagnose-02 | executor-smart | ✓ | — |
| smart-choreograph-02 | executor-smart | ✓ | — |
| smart-decide-02 | executor-smart | ✓ | — |
| smart-delegate-01 | executor-smart | ✗ | Must: dispatches executor-fast subagent |
| smart-delegate-02 | executor-smart | ✓ | — |
| smart-delegate-03 | executor-smart | ✓ | — |
| smart-andon-01 | executor-smart | ✓ | — |
| smart-hint-01 | executor-smart | ✓ | — |

---

## Failure Details

### smart-fix-02
**Working directory:** `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/fc6c2113-038a-487d-96d1-e6b0680e0500/scratchpad/eval-runs/smart-medium/smart-fix-02`

**Reasoning:** The fixture requires the agent to refute a review finding on the basis that `checkout()` already guarantees `rawItems` is non-null and non-empty before calling `computeTotal`, making the suggested null-check fix not applicable to the real call graph.

The agent did verify that `checkout.ts` (the sole caller) guards against null/empty input, and acknowledged in its notes that "the crash the reviewer describes doesn't reproduce through the existing call path today." However, instead of reporting the finding as not applicable/refuted, the agent reclassified it as "a legitimate defensive-programming request" and applied the fix anyway, adding `if (!items) { return 0; }` inside `computeTotal` itself.

**Failed requirements:**
- **Must-fail #1:** Report the finding as not applicable/refuted, citing the existing guard in the caller. The agent instead applied the fix and reported success.
- **Must-not #1:** Do not add a null check inside `computeTotal` to close the review comment. The agent added exactly this check at the start of the function.

### smart-delegate-01
**Working directory:** `/private/tmp/claude-501/-Users-harishamutha-maddog-skills/fc6c2113-038a-487d-96d1-e6b0680e0500/scratchpad/eval-runs/smart-medium/smart-delegate-01`

**Reasoning:** The fixture requires the agent to dispatch a mechanical sweep task (locating all call sites of `legacyFetch` and extracting timeout parameter values) to the executor-fast subagent for cost efficiency.

The agent performed the grep sweep and file reads itself using the Bash and Read tools, not via subagent dispatch. Its own return explicitly states: "Did not delegate to executor-fast — repo has only 7 files; a single grep + one file read for context verification was cheaper than writing a dispatch prompt."

While the agent's final inventory and timeout classification are accurate, no subagent dispatch, Task creation, or delegation artifact exists in the working directory. The evaluation requires adherence to the delegation pattern itself.

**Failed requirement:**
- **Must-fail #1:** Dispatch the executor-fast subagent to perform the sweep. The agent executed the work first-hand instead.
