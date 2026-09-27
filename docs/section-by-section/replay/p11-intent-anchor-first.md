# Pattern 11 — Intent anchor drawn from the file before asking the user

### 06ab03e5-L103
- pattern: 11
- target: .claude/skills/release/SKILL.md
- section: Intent anchor (Start)
- session: 06ab03e5-76bf-4f9a-ad64-8b5df2ef06b2
- lines: proposal L81, catch L103

Proposal:
`````text
Using `section-by-section` to review `.claude/skills/release/SKILL.md`. Here is the setup. I have not judged anything yet.

## Intent anchor

This file exists to make an agent gate every publish to main, and never merge one itself.

- The marketplace installs from main HEAD, so each merge to main ships to users.
- The file forces six phases for changes to shipped or gate-enforcing surfaces, and one phase for internal or docs-only changes.
- It stops every hand at "push and open the pull request". The user's hand is the only merge.
- Tell me if that line is wrong, and I will fix it before we start. Everything below gets tested against it.

## Your observation

I recorded one observation, and it has two halves.

- **O1** — the release procedure drags, and it does not feel bullet-proof. You want it overhauled so it stays lean and drops ceremony that earns nothing.

The two halves can pull against each other. "Drags" asks me to cut steps. "Not bullet-proof" asks me to make the remaining steps harder to fake or skip. I will read O1 as: cut the steps that produce no evidence, and harden the ones that do.
[...]
`````

Catch:
`````text
Before proceedinhg My mental model of release: A branch woth all changes done -> Release ceremony - changelong. version bump, any readmea changes required, marketplace reelated ceremony (this should be modular since we might add new marketplace too)
`````
