# Pattern 5 — More than one verdict applies; skill gives one

### 01c6d363-L384
- pattern: 5
- target: skills/section-by-section/SKILL.md
- section: S5c — Discuss (template)
- session: 01c6d363-6d06-4cdb-ba4e-f3de42f3931f
- lines: proposal L381, catch L384

Proposal:
`````text
Here is the section with the template carrying its own fill instructions.

````text
### Discuss

Post the diagnosis, not replacement prose:

```text
Section:  <id — title (line range in the target)>
Does:     <what the section makes an agent do, one line>
Fails:    <axis — the reason, or `nothing` for a KEEP>
Verdict:  <the verdict, with the MERGE partner, MOVE destination or SPLIT
           boundaries where it carries one>
Evidence: <observation ids bearing on it, or —>
```
````

[...]

**Approve, or tell me what to change.**
`````

Catch:
`````text
Wait can't we return the axes level anyways that is the lens we're reviewing right - why another template - Does this make sense ?
`````


### ec3c9100-L105
- pattern: 5
- target: agents/executor-smart.md
- section: DESC — frontmatter description
- session: ec3c9100-fc97-4101-93d2-3c244bd44ced
- lines: proposal L97, catch L105

Proposal:
`````text
# DESC: proposed RESHAPE to match the sibling descriptions

The ledger is open. The first section in file order is the frontmatter description.

```text
Section:   DESC — frontmatter description (lines 5–14)
Does:      Tells the caller when to pick Smart and which sibling takes each
           task that Smart should not take.
Elsewhere: S1 Role (what Smart owns), S3 law 3 (no product or architectural
           decisions), S7 Work (closed slices go to the Fast tiers). All three
           agree with the description.
Fails:     clarity — the four "Do NOT use" cases are one run-on list:
           "closed, mechanical work — executor-fast; read-only search —
           executor-fast-read; …". The list has four em-dashes and no verb in
           each case. Lead and Judge give each case its own sentence:
           "Do NOT use for X — that is executor-Y."
Verdict:   RESHAPE — one "Do NOT use for … — that is executor-…" sentence per
           sibling, in the Lead and Judge form. The routing content stays the
           same.
Evidence:  O1
```

## Other points I found and left out of the verdict

- **Fast's description overlaps with Smart's.** Fast's description sends "design choices" to Smart, and Smart's description says it makes no architectural decisions. The two can be read together: a local design choice goes to Smart, and an architectural one goes to the caller. I left Fast's text alone because it is outside this file.
- **One term appears only here.** "The fast hands" is used in this description and nowhere else. The body says "the Fast tiers" or "Fast-Read and Fast". I would fix this inside the reshape by writing "executor-fast-read and executor-fast", which is how the Lead description names them.

Do you close DESC as RESHAPE? If you do, I'll write the replacement text with its test results for you to approve.
`````

Catch:
`````text
Does any other verdict applies to this? going forward i the his each sectionslets not restrict yourself tp single verdict if mulitple verdict applies to it tell that too
`````


### f09ade50-L113
- pattern: 5
- target: agents/executor-fast-read.md
- section: S1 — Role opening
- session: f09ade50-46a3-4137-938b-80a10f28fa69
- lines: proposal L111, catch L113

Proposal:
`````text
## S1: proposed verdict is REWORD, adding "run anything" to the limits

DESC is recorded in the ledger. S1's opening leaves out the limit the constitution assigns to it. It also has one word that can be read two ways.

```text
Section:   S1 — Role opening (lines 17–20)
Does:      names the role, gives it one question answerable as found, leaves meaning with the dispatcher, states its limits
Elsewhere: DESC now routes any run, "even a read-only command", to Fast; law 2 (S6) returns blocked when "a capability is missing"; law 1 (S5) forbids conclusions. Constitution: OPENING pattern (name, own, edge, limits); P30 says Fast-Read's OPENING limit carries "holds no shell and can change nothing"; P13 lists "cannot ask" and "you finish by returning".
Fails:     clarity — the limits line omits "run", which P30 places here; "wait" can be read as "wait on a process", and it traces to no property (P13 is covered by "ask")
Also:      nothing
Verdict:   REWORD
Evidence:  —
```

Do you close S1 as REWORD with this text? Or do you want a different verdict or different wording?
`````

Catch:
`````text
Through this session check every section for all the vericctds one ore several may apply. not bound to one. Now give me the text again
`````
