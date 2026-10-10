"""Pick model tests by changed files. Names no runtime.

A test file lists repo-relative globs under a top-level `covers:` key
(see cases.load_covers). A test is selected when any changed file matches
any of its globs. `*` stays inside one folder; `**` crosses folders.
"""
import re
import subprocess
from pathlib import Path

from harness.core.cases import load_covers

# (folder pattern under tests/, case file name, runs in agent mode)
TEST_KINDS = (
    ("skills/*", "handoff.yaml", False),
    ("agents/*", "patterns.yaml", True),
)


def glob_to_regex(glob: str) -> re.Pattern:
    """`**/` matches zero or more folders, a trailing or lone `**` matches
    anything below, `*` matches within one path part, `?` one character."""
    out, i = [], 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif glob.startswith("**", i):
            out.append(".*")
            i += 2
        elif glob[i] == "*":
            out.append("[^/]*")
            i += 1
        elif glob[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches(globs, path: str) -> bool:
    return any(glob_to_regex(g).match(path) for g in globs)


def discover(tests_dir: Path):
    """Every (case file, agent_mode) the repo's layout defines, sorted."""
    found = []
    for folder_glob, name, agent_mode in TEST_KINDS:
        for folder in sorted(tests_dir.glob(folder_glob)):
            f = folder / name
            if f.is_file():
                found.append((f, agent_mode))
    return found


def select_tests(tests, changed):
    """tests: [(path, agent_mode)]. Keeps those whose covers match a changed file."""
    return [(path, agent_mode) for path, agent_mode in tests
            if any(matches(load_covers(path), f) for f in changed)]


def changed_files(repo_root: Path, base: str) -> list[str]:
    """Files changed on this branch since it left `base`, plus uncommitted
    changes to tracked files. Repo-relative, sorted, deduplicated."""
    def git(*args):
        r = subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return r.stdout.splitlines()

    return sorted(set(git("diff", "--name-only", f"{base}...HEAD")) | set(git("diff", "--name-only", "HEAD")))
