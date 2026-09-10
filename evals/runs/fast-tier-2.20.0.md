# fast-tier 2.20.0 eval runs

date: 2026-09-10
candidate commits: `a6098c6..05b2e55` (`agents/executor-fast.md`, `agents/executor-fast-read.md`, `skills/advisor-mode/SKILL.md`, `docs/executor-family/mechanical-work.md`, fixture E1)
harness: `.claude/workflows/agent-evals.js` (Workflow tool), local-marketplace install `maddog-dev-fast` per plan D17
models pinned: run stage haiku (both fast hands); judge stage opus

## Run 1 — routing probes, candidate

- run id: routing probe run, `evals/executor-fast-routing.json`
- agent prefix: `maddog-dev-fast:` (runtime descriptions of the executor-fast agents)
- fixture set: 11 fixtures, all core
- report: `~/.claude/ledgers/fast-tier-postmortem/behavior-routing-2.20.0.md`

| id | result | failed assertion |
|---|---|---|
| fastread-route-01 | PASS (5/5) | — |
| fastread-route-02 | PASS (5/5) | — |
| fastread-route-03 | PASS (5/5) | — |
| fastread-route-04 | PASS (4/5) | one sample routed executor-smart, not executor-fast-read |
| fastread-route-05 | PASS (5/5) | — |
| fastread-route-06 | PASS (5/5) | — |
| fastread-route-07 | PASS (5/5) | — |
| fastread-route-08 | PASS (5/5) | — |
| fastread-route-09 | PASS (5/5) | — |
| fastread-route-10 | PASS (5/5) | — |
| fastread-route-11 | PASS (5/5) | — |

11/11 passed.

## Run 2 — write-hand, candidate body, run 1

- run id: `wf_706abc5c-aac` (dropped by session limit, resumed via resumeFromRunId per ledger E26)
- agent prefix: `maddog-dev-fast:executor-fast`
- fixture set: `evals/executor-fast.json`, 24 core fixtures
- report: `~/.claude/ledgers/fast-tier-postmortem/behavior-executor-fast-run1-2.20.0.md`

9/24 passed. Failures: `edit-03`, `transform-02`, `transform-03`, `gate-03`,
`operate-02`, `operate-03`, `operate-04`, `recover-02`, `diagnose-02`,
`misroute-01`, `gate-06`, `transform-04`, `andon-04`, `extract-01`,
`faithful-01` (short reason per fixture in the report above; not restated here).

## Run 3 — write-hand, shipped body (2.19.0), same day

- run id: `wf_e6055eaf-57d`
- agent prefix: `maddog:executor-fast` (shipped, no dev install)
- fixture set: `evals/executor-fast.json`, 24 core fixtures (identical fixture set to Run 2)
- report: `~/.claude/ledgers/fast-tier-postmortem/behavior-executor-fast-shipped-baseline-2.20.0.md`

10/24 passed. Failures: `edit-02`, `edit-03`, `transform-02`, `transform-03`,
`gate-03`, `operate-02`, `operate-04`, `diagnose-02`, `misroute-01`, `gate-06`,
`transform-04`, `andon-04`, `extract-01`, `extract-02`.

## Run 4 — noise re-run, candidate body, 5 differing fixtures

- run id: `wf_5269f9ad-cc6`
- agent prefix: `maddog-dev-fast:executor-fast`
- fixture set: `operate-03`, `recover-02`, `extract-02`, `edit-02`, `faithful-01`

| id | result | failed assertion |
|---|---|---|
| recover-02 | PASS | — (was FAIL in Run 2) |
| edit-02 | FAIL | (was PASS in Run 2) |
| extract-02 | FAIL | setup defect — `logs/app.log` on disk lacked the fixture's trailing spaces (ledger E30); grader traced this to the harness, not the agent |
| operate-03 | FAIL | 2/2 |
| faithful-01 | FAIL | 2/2 |

## Run 5 — noise re-run, shipped body, same 5 fixtures

- run id: `wf_7b142ad6-355`
- agent prefix: `maddog:executor-fast`
- fixture set: same 5 as Run 4

| id | result | failed assertion |
|---|---|---|
| operate-03 | FAIL | — |
| faithful-01 | FAIL | — |
| edit-02 | FAIL | — |
| recover-02 | PASS | — |
| extract-02 | PASS | — |

## Run 6 — read-hand absence fixtures, three measured wordings

The read hand's absence law (schema R3, THE NULL HYPOTHESIS) was measured
three times against `fastread-verify-01..05` as its wording changed. Each
row is a separate run against a separate body.

| wording | run id(s) | pass rate | per-fixture result |
|---|---|---|---|
| first law (pre-round-4) | `wf_0728b326-3f3`, `wf_058b3b3c-e68` | 2/5 | 01 PASS, 03 PASS, 02 FAIL (unscoped nothing-found resolved CONTRADICTED), 04 FAIL (no CONTRADICTED on the scoped absence), 05 FAIL (no verdict word at all) |
| round-4 law (Q17/QB2b, superseded, never shipped) | `wf_c72ca5f9-6fc` | 2/5 | 01 PASS, 03 PASS, 02 FAIL (CONTRADICTED on unscoped absence), 04 FAIL (no CONTRADICTED on the scoped absence), 05 FAIL (CONTRADICTED on an unscoped question) |
| D5' (Q18/QA1b, shipped at 05b2e55) | `wf_8dc52f7f-18b` | 2/5 | 01 PASS, 04 PASS, 02 FAIL (CONTRADICTED, unscoped), 03 FAIL (citation nit), 05 FAIL (CONTRADICTED, unscoped) |

Report for the shipped D5' run: `behavior-executor-fast-read-d5prime-2.20.0.md`.

### Shipped-body baseline for verify-02/05

Dispatched to attribute the D5' run's two failures to the law text rather
than the body. Run id `wf_95a23136-5b5`, copied to
`behavior-executor-fast-read-shipped-02-05-2.20.0.md` (the file was
previously only in the gitignored `evals/last-run.md`).

| id | result | failed assertion |
|---|---|---|
| fastread-verify-02 | FAIL | reports CONTRADICTED instead of NO EVIDENCE |
| fastread-verify-05 | FAIL | reports NO EVIDENCE (settled-negative framing, effectively CONTRADICTED) |

Both fail identically to the D5' candidate run above.

## Reading

- **Comparative conclusion:** candidate 9/24, shipped baseline 10/24 on
  identical fixtures, same day. Twelve fixtures fail on both bodies
  (ledger E28): `edit-03`, `transform-02`, `transform-03`, `gate-03`,
  `operate-02`, `operate-04`, `diagnose-02`, `misroute-01`, `gate-06`,
  `transform-04`, `andon-04`, `extract-01`. The write hand's laws largely do
  not hold on haiku on either body; this package neither fixes nor worsens
  that set.
- **Noise evidence:** the 5 fixtures that differed between Run 2 and Run 3
  each flipped on at least one body across Runs 4 and 5. No fixture held a
  stable regression signal across all four write-hand runs. Conclusion: no
  attributable regression at single-run resolution (ledger E31).
- **Harness defect (D-C):** `evals/executor-fast.json` fixtures `LOG-0055`,
  `LOG-0090`, `LOG-0112` carry two trailing spaces in the JSON source
  (lines 956, 986). `.claude/workflows/agent-evals.js:214-220` writes
  `setup.files` to disk without a byte-fidelity check — only the `prompt`
  field is marked VERBATIM. The on-disk `logs/app.log` in every eval run
  lacked the trailing spaces. `extract-01` and `extract-02` are UNVERIFIED
  as written, on either body (ledger E30).
- **Read-hand result:** `fastread-verify-04` (E1, scoped absence, the
  dispatch stating the mapping) passes under D5' — the headline fix
  measures. `fastread-verify-02` and `fastread-verify-05` (unscoped
  absence) fail identically on the candidate and the shipped body
  (`wf_8dc52f7f-18b`, `wf_95a23136-5b5`): both bodies return CONTRADICTED
  or a settled-negative NO EVIDENCE on an unscoped search. This is debt
  D-D, not a regression — the cheap tier overclaims a settled verdict on
  an unscoped absence regardless of law wording. Mitigation: advisor-mode
  now requires the dispatcher to state the scoped-search-counts-as-
  CONTRADICTED mapping (`skills/advisor-mode/SKILL.md:246-248`), so an
  unscoped dispatch should not reach the hand at all. `fastread-verify-03`
  fails on a citation nit (docs source named informally, not by exact
  path) that passed the two prior wordings' runs — grader strictness or
  noise, not a law defect.
- **Debts filed at close (ledger E31, E39, E41):** write-hand law campaign
  against the common 12 (D-A); a comparative, multi-run form for the
  release gate, GATE-INFRA, separate change (D-B); harness setup-fidelity
  fix at `.claude/workflows/agent-evals.js:214-220`, outside this
  package's file map (D-C); unscoped-absence overclaim on the cheap tier,
  mitigated structurally by the dispatch contract, not by law wording
  (D-D, ledger E39/E41).
