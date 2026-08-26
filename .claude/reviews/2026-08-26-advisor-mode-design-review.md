# Design review — skills/advisor-mode/SKILL.md — 2026-08-26
Judge: maddog:executor-judge. Target: repo HEAD 01f57b4. Binding design artifact: none (spec-fidelity NOT EXECUTED).

VERDICT: CLEAR-WITH-FINDINGS

FINDINGS

F1 MAJOR — normative coherence — `skills/advisor-mode/SKILL.md:173-177` — the ledger's open trigger and its prohibition cancel each other in one sentence. "Open it the moment the user will not be present for a return — before that dispatch ... and never while the user is present"; the file's own disambiguator ("launching a dispatch whose return the user has said they will not be there for is") places that moment while the user is still present. Prohibition wins, so the ledger opens late or never — remedy is to state which half governs at the launch instant.

F2 MAJOR — behavioral realism — `SKILL.md:136-138` vs `56-58, 62` — BIND's verification is unperformable within Own Hands. The survey grants "list the agents and read their descriptions", while the bind contract says "the family's guarantees live in tool restrictions, not instructions" — descriptions are precisely the instruction-level evidence it rejects, and no `tools:` read or grep is permitted. The advisor silently binds `adversarial` on a self-claim; remedy is to widen the survey allowance to the evidence the contract demands, or weaken the contract.

F3 MAJOR — behavioral realism — `SKILL.md:51, 88` with `references/ledger.md:76-78` — the routing precondition can never be satisfied. Bind requires "a hand for every class"; `kept` is "Never for sale" and has no row in the Bind table; ledger.md gates routing on a statement "NAMING every class's hand". Remedy: exempt `kept` explicitly in the Bind table.

F4 MAJOR — behavioral realism — `SKILL.md:192-193` — "Where an efficient-md skill is installed, invoke it once at BIND" has no permitted discovery path: commands are delegated (`147-153`), routing is prohibited until BIND completes (`52-53`), and the survey covers agents only. Remedy: name how installation is detected, or move the invocation after BIND.

F5 MAJOR — normative coherence — `SKILL.md:133-135` vs `151` — the Read allowance ("this skill's references when a rule points to them") and the prohibition ("Any read done to write something, to 'get context'") collide on the two reads the file makes mandatory (`180`, `273`). The Survey line pre-resolves its own collision ("No other command is yours"); the Read line carries no equivalent. Remedy: add the same closing clause to Read.

F6 MAJOR — behavioral realism — `SKILL.md:176-177` — the unattended trigger keys on prediction at launch and explicitly excludes the user leaving mid-dispatch ("'Back in ten minutes' during a dispatch already running is not that moment"), so a run that becomes unsupervised gets no watchdog, resume record, or ledger — the exact 11.8-hour loss `references/absent.md:8-9` cites. Remedy: give the mid-flight departure its own disposition.

F7 MAJOR — normative coherence — `SKILL.md:250-254` vs `skills/plain-english/SKILL.md:18-20` — gate surfacing mandates "surface as finding IDs ... never re-emit the text", while plain-english requires spelling out "a label coined this session (a finding ID ...) at its first use in each message". The advisor emits undecodable IDs; remedy is to permit the gloss, since the prohibition currently forbids it.

F8 MINOR — normative coherence — `SKILL.md:5-6` vs `79` — the description names the family ("fast/smart/lead/judge/researcher") against the body's "This table names no agents; the hands come from the binding record."

F9 MINOR — routing/description standard — `SKILL.md:3-8` — three D-DESC failures: imperative second person "Act as the Advisor" (D-DESC-6); no "Use when …" trigger with 3-7 concrete situations (D-DESC-2); restated body norms — three budgets, routing, gates (D-DESC-5). 363 chars, inside both caps; no S3 redirect against sibling `product-engineering`.

F10 MINOR — token weight — `SKILL.md:117-120` — "Buy iterated only when the package must survive outside your own context — absence, parallelism with the main thread, context scarcity" near-verbatim duplicates `agents/executor-lead.md`'s description, which the registry already injects into every session. Remedy: cut or point.

F11 MINOR — token weight — `SKILL.md:113` vs `188-189` — same rule twice with divergent closure: "Serialize any two dispatches that touch the same file" versus "never dispatch two writes to the same path concurrently". The weaker copy teaches the wrong closure; keep one.

F12 MINOR — obligation weakness — `SKILL.md:52-53, 277-283` — BIND-before-routing and CLOSE's memory write are affirmative, silently skippable, and name no converting structure; contrast `167-168`, which at least records that none exists. An advisor-side hook is the available structure and is unnamed.

F13 MINOR — doc coherence — `README.md:9` ("Never does mechanical work") vs `SKILL.md:136-138`, which assigns the advisor one mechanical command.

DIMENSIONS
- 0 File hygiene: PASS
- 1 Spec fidelity: NOT EXECUTED — no binding design artifact supplied.
- 2 Routing partition / description standard: FAIL — F9.
- 3 Normative coherence: FAIL — F1, F5, F7, F8.
- 4 Behavioral realism: FAIL — F2, F3, F4, F6.
- 5 Obligation weakness: FAIL — F12.
- 6 Doc coherence: FAIL — F13.
- 7 Decoupling: PASS
- 8 Token weight: FAIL — F10, F11.

DELEGATION LOG
- executor-fast — verbatim extraction of frontmatter blocks, doc/manifest greps, CHANGELOG 2.4.0-2.7.0, references/ listing — evidence only.

NOTES
- Verified first-hand: executor-judge.md:26 and executor-lead.md:39 hold no Write/Edit; researcher.md:13 holds web tools.
- Not verified: whether the plugin install path ships skills/*/references/; F5's impact assumes it does.
- Gates WHEN vs WHEN NOT tested and pre-resolved at SKILL.md:234-237; not filed.
---
# Packet gate round 1 — 2026-08-26
P1 APPLY — G1 cosmetic: rationale says 589 chars; actual 585 (589 bytes). D-DESC pass; partition clean.
P2 REWORK — G2 load-bearing ledger.md:66-67 BINDING RECORD bullet still says "always NAMES each class's hand" (same F3 defect). G3 cosmetic SKILL.md:51 heading still "every class". G4 cosmetic: Replacement A duplicates Routing table kept row.
P3 REWORK — G5 load-bearing: replacement names `executor-lead` in a body that says "names no agents"; repo-own iterated hand has no such description. G6 cosmetic: "do not restate the condition here" addresses the author, not the advisor.
P4 REWORK — G7 load-bearing: "No other read is yours" forbids the mandated read of the filed gate ruling (SKILL.md:250-254) and reading back the ledger for surfacing. G8: also forbids Survey's reads in the other bullet.
P5 APPLY — G9 moderate: `tools:` lines are already in session context via the registry; "by whatever tool does it" authorizes a needless file read. Not gating.
P6 REWORK — G10 load-bearing: "both flipping USER PRESENCE to absent" at launch decision sets the bit while the user is present; DECISION STATE (SKILL.md:272) then settles open items by bounded judgment instead of dialogue, and CLOSE's surfacing prohibition evaporates. G11 moderate: absent.md has no in-flight disposition for a mid-flight departure (§1 pre-launch only, §5 return only).
P7 APPLY-WITH-CUTS — cut verbatim: " — see the Batching Law for the file-serialization rule that governs concurrent writes". G12: pointer to text already resident is pure rent.
P8 APPLY-WITH-CUTS — cuts verbatim: " — no command checks for it" and "already". Premise verified: efficient-md description is in every session.
P9 REWORK — G13 load-bearing: "first use in a message" vs plain-english "each message"; divergent closure reintroduces F7. G14 cosmetic: clause spliced inside a "+"-joined list.
P10 APPLY.
PACKET HEADER OK. NOTES: green light unverifiable by judge; P1 trigger sentence 38 words, description-standard governs over plain-english ≤25.
---
# Packet gate round 2 (re-gate, covered rework round spent) — 2026-08-26
P2 APPLY (G2/G3/G4 closed). P3 APPLY (G5/G6 closed; residual: a bound iterated hand with no buy-condition in its description makes the pointer inert; inherent to F10 remedy). P4 APPLY (G7/G8 closed). P7 APPLY (cut folded). P8 APPLY (G16 cosmetic: "Whether or not it is:" lost antecedent). P9 APPLY (G13/G14 closed).
P6 REWORK — G15 load-bearing: Replacement A opens the ledger at the launch decision; Replacement B (USER PRESENCE row) says the ledger "opens on either departure trigger and not before". B forbids the opening A mandates. Also absent.md:29-30 still says the ledger "opens now, at the flip". One consistent open moment must be stated across the Ledger paragraph, the State row, and absent.md §1.
P11 REWORK — G17 load-bearing: mid-flight section omits the heartbeat / run-start ping that §1 pairs with the watchdog; §5 closure ping then has no channel.
CLEARED: P1, P2, P3, P4, P5, P7, P8, P9, P10. BLOCKED: P6, P11 (entangled on one question: the ledger's open moment).
---
# Packet gate round 3 (second rework round, user green-lit) — 2026-08-26
P6 APPLY — G15 closed: Replacements A, B, C state one open moment (launch decision); ledger.md has no third copy; DECISION STATE not pre-empted. G18 cosmetic: B's parenthetical "before the first unattended dispatch" is imprecise on the mid-flight path; harmless.
P11 APPLY — G17 closed: run-start ping added via §1's channel wording. Residual non-gating: §1's no-watchdog fallback unreachable mid-flight.
ALL 11 ITEMS CLEARED. Verdict IDs: P1/P5/P10 round 1; P2/P3/P4/P7/P8/P9 round 2; P6/P11 round 3.
