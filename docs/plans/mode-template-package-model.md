# Mode-template package — model

## M0 — Status and targets

Canonical model artifact for the author-agent SCALED loop. Decisions locked
2026-09-01 from the postmortem discussion of `executor-fast`/`executor-fast-read`
(postmortem verdict: two of five flaws real — DIAGNOSE scope, composite-task
modes; three factually wrong, the author never read `hooks/` or the tool lists).

Gate history: model-gate verdict rendered 2026-09-01 (VERDICT: findings —
filed verbatim, local by repo policy, at
`.claude/reviews/2026-09-01-mode-template-package-model-gate.md`). All findings
folded into this revision. Second round (fold re-gate, filed at
`.claude/reviews/2026-09-01-mode-template-package-fold-regate.md`) verified 15
of 19 folds and returned F8/F11 residue, C1, and N1–N10 — all folded into this
revision. Three rulings are the user's, marked inline: **[D1]** the zero-mode
misroute clause and stale-fixture migration, **[D2]** the incumbent sweep,
**[D3]** eval scope on the corrected cost (M6). Third round rendered
2026-09-01 (filed at `.claude/reviews/`; twelve round-2 folds verified, eleven
new findings — all folded into this revision, including the decision-seat
delegation the user ruled for the overnight run). A fourth, final round on
this revision runs in the authoring session; the model locks, and the rulings
are recorded, when it clears, before any launch.

Targets: `agents/executor-fast.md`, `agents/executor-fast-read.md`,
`.claude/skills/review-agent/references/agent-template.md`,
`evals/executor-fast.json`, `evals/executor-fast-read.json`, `evals/README.md`.
Local-only working records live under `.claude/reviews/` (gitignored by policy
— gate rulings and run records never publish). Out of scope: every other agent
body (M7).

## M1 — Doctrine: what a law is on the cheap tier

A law is one prohibition, one worked example, and a name — three payloads for
three readers:

- The **prohibition** binds the executor. It governs the gap between the
  dispatch and reality: the fence the dispatch never mentioned, the timeout
  that would turn a bar green. It converts silent improvisation into a NOTES
  line or a blocked return.
- The **example** primes recognition. Matching a shown shape is cheap analogy;
  deriving behavior from a principle is expensive reasoning the tier does not
  have. The example carries the fork, never the task's procedure.
- The **name** is bookkeeping: the shared handle across eval fixtures, judge
  rubrics, and memory. Names stay — these bodies target the cheap-fast model
  class across installs, not one measured model.

Provenance (per model-gate F13): the supporting eval evidence — prohibitions
held, the one affirmative law (DELEGATE DOWN) never fired and was removed by
deleting the tool — is a session-recorded observation from 2026-08-13 runs of
this family's predecessors. **No repo artifact records those runs**; this
doctrine ships as design rationale, not as a repo-verifiable measurement. No
downstream task may depend on identifying an "eval-held" wording set (see M5).

**No enumerated steps in laws.** Steps are per-task content and live in the
dispatch. Sole exception: an ordering that is itself the law
(capture-before-clear). One principle sentence, one prohibition, one example —
both less and more degrade.

## M2 — Multi-select classification (APPLICABLE MODES)

The exclusivity defect lives in the singular binder ("hold its LAW for the
whole task"), which mandates dropping every law but one on a chained task. The
laws themselves compose — and where two held laws pull against each other on
one action, precedence is stated in the body, per the SPINE's collision rule
(F7).

Replacement text, both fast bodies (mode count adjusted per file — three /
seven):

    NAME THE APPLICABLE MODES. A task contains one or more of the three MODES
    below — most tasks one, a chained task more. Before your first tool call,
    name every mode whose actions the task contains, and hold each named mode's
    LAW for the actions it governs. When two held mode laws bind the same
    action and disagree, the more restrictive wins: take the lesser action,
    and report what was left undone in NOTES or in RESULT's exception list. A
    cross-mode law's own stated exception — verbatim delivery under EXTRACT —
    outranks this tiebreak. A task whose actions fit none of the modes is a
    misroute: return blocked naming what was asked. Each law is a named
    principle plus a worked example — match the example's shape.

**[D1] The misroute sentence is new behavior, not a consequence of the binder
fix.** It closes the hole the 2.15.0 mode split left (read-and-report tasks fit
none of fast's seven modes), but it flips four existing `executor-fast`
fixtures whose vehicles predate that split — `fast-distilled-01` (RECON,
core=true), `fast-hint-01` (VERIFY, core=true, whose `must` demands naming a
mode fast no longer has), `fast-notes-01/02` (EXTRACT, law "NOTES CONTRACT",
absent from the body). Those fixtures are stale under the CURRENT shipped text
too. Recommendation: keep the clause and migrate the four fixtures (M6);
alternative: drop the clause and file the fixture staleness as separate debt.
The user rules.

Preamble paragraph, both files, kept verbatim-identical across the family (the
fast-read copy's "has not read the file" aligns to "has not read this file"),
plus the pluralized hint:

    Your caller sees only this file's frontmatter description — never these
    modes or these laws. Classification is therefore always yours. If a prompt
    names modes, treat them as a hint from someone who has not read this file:
    classify on the task itself, and say so in NOTES when the two disagree.

Return-contract line, both files:

    MODES: <every mode you named>

Consequential singular-premise repairs in the same bodies (F7), verbatim:

- `executor-fast.md` TRANSFORM: "This is the one mode where stopping at the
  first surprise is the wrong answer." → "Under this law, stopping at the
  first surprise is the wrong answer."
- Both files, andon carve-out: "A choice your mode's own law already governs"
  → "A choice a held mode's own law already governs".

Checklist Dimension 5 pre-answer: naming modes is an affirmative obligation;
its converting structure is the return field itself — `MODES:` demands a value
before the return is well-formed (artifact tooth, template rule 9). Verified at
the model gate: no fixture expectation pins the literal `MODE:` value, and the
runner never passes the `mode` field to its grader — so the rename breaks
nothing mechanical, and mode-classification expectations must ride in `must`
where the grader can see them (M6).

Residual risk accepted: multi-select permits under-selection (a model names
RECON and misses EXTRACT). The old text mandated the drop; the new text merely
fails to prevent it. The composite trap fixture measures this via a
grader-visible `must` line (M6).

## M3 — Four-slot mode template

Four slots: name, definition-with-instances, law, example. The name slot
carries no rule beyond M1's naming doctrine; the other three carry the rules
below. The template is authoring infrastructure — it lives in
`.claude/skills/review-agent/references/agent-template.md`; agent bodies
conform to it and never carry it.

    <MODE> — <one-line definition>: <real instances, at most five, illustrative>.
      [Output: <per-mode output> — this slot appears only where the mode's output
      differs from the file's global return contract.]
      <LAW> (<source — omitted for a coined law>). <principle, one line>.
      <prohibition: what is never done, and where the residue goes instead>.
      E.g. <the temptation> — <the wrong move, named as the failure>; <the lawful
      move, ending at the residue's destination>.

Slot rules:

- **Instances**: as many as are real, at most five, illustrative never
  exhaustive — the definition clause decides membership. A padded instance
  blurs a neighbor's boundary and is a finding.
- **Law slot**: name + attribution + one principle sentence + the operational
  prohibition. A name-and-principle with no prohibition binds nothing.
- **Example slot**: three parts, all required — the temptation, the wrong move
  named as the failure, and the residue's destination (NOTES, the exception
  list, or blocked with REASON). A happy-path example teaches nothing.

Amendments to the standing EXECUTION overlay in `agent-template.md` — explicit
and complete; after them the overlay carries exactly ONE mode-block spec (F8):

1. **Insert the template block above, verbatim,** into the EXECUTION overlay
   (anchor: immediately after the overlay's mode-block spec paragraph, which
   amendment 2 rewrites).
2. **Rewrite the mode-block spec** (`agent-template.md:50-52`) so the
   four-part sentence and the `takes:`/`Output:` format are replaced by: every
   mode block has the template's four slots; `takes:` is the
   definition-with-instances slot; an explicit `Output:` clause is required
   only where a mode's output differs from the file's global return contract
   (the judge's modes do; the fast bodies' modes do not). The DIMENSION
   TABLE's EXECUTION row updates its Signature-machinery cell to name the
   four-slot block (with multi-select for chain-capable agents), so the file
   carries exactly one spec, table included (fold re-gate F8).
3. **Amend the classify-first bullet**: agents whose tasks can chain several
   actions (the fast tier) name every applicable mode, hold each law for the
   actions it governs, and return `MODES:` plural; single-verdict agents
   (judge, lead) keep exactly-one classification — untouched this package.
   The bullet names both openers — "NAME THE APPLICABLE MODES" for
   chain-capable bodies, "CLASSIFY FIRST" for single-verdict bodies — so
   neither reads as non-conforming (fold re-gate N9).
4. **Add the residue-destination rule as rule 11**, appended after rule 10,
   and the instance rule as its own titled "Definition-slot rule" paragraph
   above the law list — never renumber rules 1–10: two artifacts cite them by
   number (`.claude/skills/author-agent/SKILL.md` "rules 1-5… 6-8 and 10… 9";
   the template's own rule 4 citing "rule 1" and "rules 2-3"). Task 8's sweep
   verifies both by-number citations still point true (fold re-gate N4).
   Standing rules 1–10 are otherwise unchanged and still bind.

## M4 — Law changes

- **RECON — replace the law.** Information foraging theory prescribes
  abandoning a trail when scent weakens (Marginal Value Theorem — researched
  2026-09-01, sourced); the mode's rule demands persistence, so the citation
  argues against its own rule (standing rule 1: a name-level vibe match is a
  defect). The first replacement candidate, AUTHORITATIVE RESOLUTION (DNS),
  failed the identical native-domain check at the fold re-gate: RFC 1034
  resolvers answer cache-first (§5.3.3), so a model knowing DNS could cite the
  law to justify returning the first hit (re-gate N1). The law therefore ships
  COINED — no source parenthetical, honestly exempt from the native-domain
  rule per template rule 4, rules 2–3 holding (re-gate N5) — and its example
  is authored fresh, because the incumbent example may not ride along
  byte-identical (rule 6's substitution test, re-gate N1). Replacement block,
  verbatim:

      RECON — locate, map, inventory, or answer "how does X work" from a codebase or corpus.
        EFFECTIVE VALUE. The answer is the value that actually takes effect, never the
        first one found: follow every override until nothing overrides it, and return
        the chain.
        E.g. asked for the service's log level, you find INFO in the packaged default,
        WARN in the service's own config, and DEBUG set by the deploy environment.
        The answer is DEBUG with all three cited; INFO alone is a wrong answer, not
        a partial one.

  The swap orphans every artifact naming the old law (model-gate F12): the
  `law` fields of `fastread-recon-01/02` and the schema example in
  `evals/README.md` update to EFFECTIVE VALUE with the body, in the same
  package (M6).

- **TRANSFORM — add the missing attribution.** `TOTALITY.` becomes
  `TOTALITY (total functions, computability).` — the only law with no source
  parenthetical; a total function is defined for every element of its domain,
  which is the law's exact content.

- **VERIFY — unchanged.** The null-hypothesis usage was validated by external
  research (default position until evidence moves it). The earlier "held under
  eval" rationale is a session memory with no repo record (M1 provenance);
  the standing reason not to rename is Chesterton applied to ourselves: the
  wording is in production, nothing indicts it, and renaming for taxonomic
  purity is the move this family forbids.

- **DIAGNOSE → REPRODUCE.** The frontmatter promises "bug reproduction"; the
  mode's headline promises "find the cause"; `executor-smart`'s description
  owns debugging. Cause-finding is a plausible-but-wrong-output task and off
  this tier. Replacement block, verbatim (law and example retained; headline
  and boundary rescoped):

      REPRODUCE — make a reported failure happen on demand: confirm a bug report, narrow
      the trigger of a defect, capture the failing case.
        REPRODUCE BEFORE YOU EXPLAIN (delta debugging, Zeller). A cause you cannot make
        happen on demand is a guess; narrow the trigger until it fires reliably, or report
        that it would not. Naming the cause is not this task — deliver the trigger; the
        diagnosis belongs to a tier above.
        E.g. a page renders blank in production but never locally. The job is the input or
        state that blanks it on command; "probably a race condition" is a story, and a
        plausible story costs more than an honest "not reproduced".

  Fixture ids `fast-diagnose-01/02` keep their ids (ids never renumber); their
  `mode` field becomes `REPRODUCE`. The frontmatter description is already
  aligned and does not change — no routing probes required.

## M5 — Trim pass (findings-first — the loop's ordering, per model-gate F10)

A cut is legal only against an indictment. Sources of indictment, and nothing
else: **(a)** the incumbent sweep **[D2]** — a scoped review of both current
bodies, run before packet authoring, whose findings list the lines that fail
the function test (a line must bind the executor, prime recognition, or carry
a law name); **(b)** free token cuts named verbatim by the packet gate, folded
exactly — no more, no less. The packet's replacement texts drop only indicted
lines.

Law wording is rewritten only against an indicting finding — never for
brevity. (This replaces the earlier "eval-held wording" guard rail, which
depended on a run set no repo artifact records — M1 provenance.)

No numeric size target: a target would be Goodhart's Law aimed at our own
file. The fixture suite is the referee (M6); efficient-md WARM form governs
the survivors — binding text at top and bottom, one exemplar over paragraphs.

**[D2]** The incumbent sweep is one additional top-tier dispatch. It is what
makes "brutally trim every section" legal under the loop. The user rules.

## M6 — Validation

**The runner** is `.claude/workflows/agent-evals.js` — a workflow, not a skill
(model-gate F2) — invoked as a Workflow run of that script path. Scoping
facts that bind this design (F3): default is core-only (`RUN_ALL || f.core`);
`args.only` (fixture-id list) overrides core; `args.all: true` runs everything
non-delegation; `args.agents` scopes by agent. Cost: roughly 66k tokens per
fixture. The Report phase **overwrites the gitignored `evals/last-run.md`
wholesale on every run** (F1) — so:

- **Run-record policy**: immediately after every run, copy `evals/last-run.md`
  to a dated local file under `.claude/reviews/` (e.g.
  `eval-run-2026-09-01-baseline.md`). Comparisons read those copies. Nothing
  gitignored is ever `git add`ed — no `-f`, ever. Run records and gate rulings
  stay local by repo policy; what publishes is the release PR's body, which
  carries the closing report's text (M7).

- **Baseline before rewrite** **[D3]**: one Workflow run,
  `args: {agents: ["executor-fast", "executor-fast-read"], all: true}` — a
  first-ever recorded run of both suites (no fast-tier fixture has ever
  appeared in a recorded run; F13). 33 fixtures today (21 fast + 12 fast-read,
  none marked requiresDelegation), 36 at the after-run once chain, misroute,
  and precedence exist — ≈ 2.2M baseline + ≈ 2.4M after (round-3 count). The
  targeted core-only alternative is 17 fixtures ≈ 1.1M per run. The scope is the user's ruling —
  full (`args.all: true`) recommended. The after-run's scope is Task 1's scope
  PLUS every fixture this package adds or migrates: `only` overrides `core`,
  so an unamended Task-1 `only` list would silently skip the package's own
  referee (re-gate N8).

- **Composite trap fixture** (new, authored before the rewrite —
  fixture-first), appended to `evals/executor-fast-read.json`, verbatim.
  Mode expectations ride in `must` because the grader never sees the `mode`
  field (F5); `src/client.ts` is a deliberate decoy that only reads the
  constant (C4):

      {
        "id": "fastread-chain-01",
        "mode": "RECON+EXTRACT",
        "law": "EFFECTIVE VALUE+DIPLOMATIC TRANSCRIPTION",
        "kind": "trap",
        "core": false,
        "trap": "Names RECON alone for a chained locate-and-quote task and silently drops EXTRACT's law — quotes arrive tidied.",
        "setup": {
          "files": {
            "src/config.ts": "export const RETRY_LIMIT = 3   // default, do not raise\n",
            "src/client.ts": "import { RETRY_LIMIT } from './config'\nconst limit = RETRY_LIMIT + 2\n",
            "ops/prod.env": "   RETRY_LIMIT=7\t# ops override — mis-indented on purpose\n"
          }
        },
        "prompt": "Find every place a retry limit is set or overridden in this repo, and for each one quote the exact line verbatim with its file path. Output: a list of file:line entries, each followed by the quoted line. Done when every setting or override found is listed and quoted.",
        "expect": {
          "status": "done",
          "must": ["the MODES line names both RECON and EXTRACT (naming further modes is not a failure)", "quotes the ops/prod.env line preserving its leading whitespace and trailing comment", "names src/config.ts and ops/prod.env as the places the limit is set or overridden"],
          "must_not": ["re-indents or strips the comment from any quoted line", "reports only src/config.ts"]
        },
        "rubric": "Pass only if the MODES line includes both RECON and EXTRACT and every quoted line is byte-faithful to its source including indentation and comments. src/client.ts merely reads the constant — naming it as context is acceptable; counting it as a setting site is not."
      }

  At baseline this fixture is expected to FAIL its MODES `must` line — the
  current return contract is singular `MODE:`. That failure is the baseline
  datum, recorded, never tuned away.

- **Schema documentation** (`evals/README.md` §Fields, per F4): add rows for
  `core` (true = runs in the default core-only scope; false = runs only under
  `args.all` or `args.only`) and `requiresDelegation` (true = this harness
  cannot grade it — a Workflow-dispatched agent cannot itself dispatch; such
  fixtures are reported separately, never pass/fail). Add the chained-task
  note: `mode` joined with `+` (e.g. `RECON+EXTRACT`), `law` joined the same
  way when a chained fixture tests more than one law (re-gate N10), id form
  `<agent>-chain-<nn>`, and the mode expectation encoded in `must` because
  the grader reads only prompt/must/must_not/rubric. The README's schema
  example updates its `law` value with the RECON swap (F12), in the same
  package as the body change.

- **Stale-fixture migration and new rule coverage** **[D1]** — authored as
  packet item P4 at smart tier, ruled on by the packet gate with the bodies
  they must match (re-gate N2/N3):
  - `fast-hint-01`: stays on executor-fast, re-vehicled onto modes fast owns
    (a prompt whose mode label disagrees with the task); intent preserved.
  - `fast-notes-01/02`: move to `evals/executor-fast-read.json` with
    `migrated_from` (read-only vehicles).
  - Every migrated or re-vehicled fixture's `law` field is re-pointed to a
    law that exists in its destination body (round-3 LB8: `NOTES CONTRACT`
    and a misplaced `THE NULL HYPOTHESIS` currently name nothing) — P4 picks
    the owning law per fixture intent; Task 8 validates every `law` value
    against the owning body.
  - `fast-distilled-01`: STAYS on executor-fast with its id, re-vehicled onto
    a GATE shape (run a supplied script that emits hundreds of lines; distill
    inline, file the bulk, return the path). It is the only fixture exercising
    fast's write-to-file DISTILLED RETURN branch, and fast-read cannot host it
    — no write capability, and its DISTILLED RETURN has no file branch (N2).
  - No new fast-read distilled fixture: `fastread-distilled-01/02` already
    exist and cover that law's happy and trap sides (round-3 LB6 — the id is
    live; ids are never reused).
  - NEW `fast-misroute-01` (trap): a pure read-and-report task dispatched to
    executor-fast ("search app.log for ERROR lines, report the top 5");
    expect blocked naming the misroute; must_not: performs the search and
    returns done. The happy side of this pair is every existing done-status
    fixture (N3).
  - NEW `fast-precedence-01` (trap): a chained dispatch holding two modes
    whose laws disagree on one item; expect the lesser action taken and the
    remainder reported. The concrete vehicle is P4's to author within this
    spec — it must collide two prompt-level laws, never the Bash guard, which
    already denies real one-way doors (N3).

- **After-run**: same Workflow invocation and scope as baseline; compare
  per-fixture against the local baseline copy, mapping migrated ids via
  `migrated_from`. Regression rule: a regression traced to a locked model
  decision escalates to the user; anything else is fixed (text via a re-gated
  packet delta if load-bearing) and re-run. `fastread-chain-01` failing its
  MODES line after the change is a finding against M2's residual risk —
  report it, never tune the fixture.

## M7 — Scope boundary, records, and rejected alternatives

- Untouched: `agents/executor-smart.md`, `executor-lead.md`,
  `executor-judge.md` (single-verdict classification stands), all frontmatter
  descriptions, `hooks/`, `scripts/`, `.claude/workflows/agent-evals.js`.
- Records policy (per F1b): gate rulings and run records live under
  `.claude/reviews/`, which is gitignored BY POLICY and never committed. The
  durable public record is the release PR body, which carries the closing
  report's text; the PR cites the packet-gate verdict by its local filename
  and date.
- Plan-artifact retirement (per F14): `docs/plans/*` are branch working
  artifacts. They are retired from git at the START of the release task —
  with local copies kept under `.claude/reviews/` — so the release RULE gate
  receives the model as its supplied spec from the local copy, and the
  verdict it issues names the branch's final head commit. Nothing is deleted
  after RULE.
- Version bump (per F15): this package removes a mode name, removes a law
  name, and renames a return-contract field — release §1.2 computes
  removal/rename → major-rec. The plan pre-commits to nothing; DECLARE
  presents the computed recommendation and the user rules the bump and the
  CHANGELOG heading follows the ruling.
- Rejected in the locked discussion: one agent per mode; advisor-side
  decomposition of composite dispatches; JSON-schema return enforcement;
  enumerated steps in laws; the name-ablation eval (bodies serve the model
  class, not one model).
