---
name: release
description: >
  Releases this plugin. Prepares a finished branch with the version bump,
  the CHANGELOG entry and any text the change made stale; runs the repo's
  own checks; has one independent reviewer clear anything users receive;
  opens the pull request; and publishes to every marketplace target once the
  user has merged. Merging to main publishes, because the marketplace
  installs from main HEAD. Use when a branch is finished and ready to become
  a release. Do NOT use for work staying off main. Do NOT use to merge: every
  hand stops at the open pull request, and the user merges.
metadata:
  internal: true
---

## 1. Prepare the branch

Start from a branch whose changes are finished. Every step below runs against
that branch's committed tree, never against uncommitted edits.

1. Run `git fetch origin` and rebase the branch onto `origin/main`.
2. Commit any README, manifest or docs text this change made stale.
3. Decide whether the change reaches anyone who installs the plugin. A change
   confined to `.claude/` or to documentation does not, and carries no
   version.
4. Compute the bump against `origin/main` HEAD: a removal or rename is major,
   an addition is minor, a fix is patch. Show the user the computed bump; the
   user rules the actual one.
5. Confirm the ruled version is unused: it appears in no CHANGELOG heading on
   `origin/main`, and no existing git tag matches it.
6. Commit the version in `.claude-plugin/plugin.json` and the new CHANGELOG
   entry.

## 2. Run the checks

Run checks 1 to 4 against the branch's committed tree and record each result.

1. **CI, locally.** Extract the Python script between `<< 'VALIDATE'` and
   `VALIDATE` in `.github/workflows/validate.yml`, and run it verbatim with
   `python3` and `pyyaml` installed. If those markers are gone, stop and
   report it. Never substitute a remembered copy of the checks.
2. **Shell.** Run `bash -n` on every `.sh` file in `scripts/`. Parse
   `hooks/hooks.json` and confirm every command path in it exists. Run
   `scripts/executor-guard.sh` twice, piping it a PreToolUse JSON payload on
   stdin with `agent_type` set to `executor-fast`, `cwd` set to the repo root,
   and `tool_input.command` set to the command under test. Send `ls` on the
   first run and `git reset --hard` on the second. It exits 0 either way, so
   read its output, not its status: `ls` must print nothing, and
   `git reset --hard` must print a `hookSpecificOutput` block carrying a deny
   decision.
3. **Manifests.** List `agents/`, `skills/` and `workflows/` from disk and
   diff them against `.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json`. Grep the repo for by-name references to
   anything added, renamed or removed in this release.
4. **Changelog.** Skip this when the change carries no version. Otherwise
   the new entry is present and follows the style of the entries above it.
5. If `origin/main` moved while you were working, rebase onto it and run
   these checks and the review again against the new head commit.

## 3. Get it cleared

| What the change touches | Reviewer |
|---|---|
| `agents/`, `skills/`, `workflows/`, `.claude-plugin/` — what users receive | required |
| `.github/`, `hooks/`, `scripts/` — what runs the checks and the guard | required |
| `.claude/` except this skill; README, CHANGELOG, CLAUDE.md, CONTRIBUTING.md, SECURITY.md, LICENSE, .gitignore, PHILOSOPHY.md, DESIGN.md, assets/, skills.sh.json | not required |
| any path not listed above | required — an unclassified path fails closed |

This skill sits in `.claude/skills/release/` and counts as running the checks,
so a change to it needs a reviewer.

When the table says a reviewer is required, dispatch one independent
reviewer holding the diff, the check results from section 2, and the table
above. The reviewer must have no ability to edit the repository, and whoever
authored the release never clears it.

Ask for one verdict: CLEAR or BLOCKED, with findings, naming the exact head
commit it covers. When the release changes a frontmatter description, the
reviewer also rules on whether the new wording routes the way the change
intends.

BLOCKED sends the work back. After a fix, the next verdict names the new head
commit.

## 4. Open the pull request

1. Push the branch to origin.
2. Open or update the pull request against main. The body carries the
   verdict and the commit it names, and every check from section 2 with its
   result.
3. Stop there. Never merge — the user merges, always.
4. Tell the user, when handing over: merge only while the verdict names the
   pull request's current head commit. A force-push replaces that commit and
   voids the verdict.

## 5. Publish

Runs after the user merges, never before: a tag belongs on a merge commit.
Skip this section when the change carries no version — there is nothing to
tag, and nothing new for anyone to install.

1. Pin the merge commit. Read it with
   `gh pr view <number> --json mergeCommit`. Check out main, pull, and
   confirm that commit is on it. Tag that SHA. Never tag local HEAD.
2. Tag it `vX.Y.Z` and push the tag.
3. Publish to every target in the table below.
4. Confirm CI is green on main for that commit.
5. Comment on the merged pull request with the tag, each target's proof, and
   the CI result.

| Target | What publishes it | Proof it published |
|---|---|---|
| The maddog marketplace (`Harish-here/maddog`) | The merge itself — `marketplace.json` points at the repo root, so main HEAD is what installs. | A fresh install reports the new version. |
| Plugins that depend on maddog | `claude plugin tag --push`, run on the pinned merge commit, creating `maddog--vX.Y.Z`. | Both output lines: `Created tag maddog--vX.Y.Z` and `Pushed to origin`. |

Adding a marketplace adds a row. No step above it changes.

When `claude plugin tag --push` refuses: a tag already on this commit is the
end state you wanted, so record it and carry on. A dirty tree gets committed
or stashed, never discarded, and if the changes are not yours, hand back to
the user. A version disagreement between the manifests is a failure — stop
and report it. A tag created but not pushed is not done: run the `git push`
it prints.

## If a published release breaks users

Revert it on a fresh branch, then run this procedure again as a patch
release. Never revert a revert — fix forward instead.

## Never

- Report a release as done while a check is unrun and unmentioned. A check
  that cannot run here is named in the pull request, with the reason.
- Publish half of a multi-part change. Stage every part on one branch until
  the whole change is ready.
- Narrow `.github/workflows/validate.yml` to selected paths, or delete it
  while pull requests still require it.
- Add a step to this file without removing one.
