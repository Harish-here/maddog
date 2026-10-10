"""Pick model tests by changed files. Names no runtime.

A test file lists repo-relative globs under a top-level `covers:` key
(see cases.load_covers). A test is selected when any changed file matches
any of its globs. `*` stays inside one folder; `**` crosses folders.

Release selection (`select_for_base`) is stricter: files under `tests/` and
`.claude/` never select, and a test file's globs are the union of its
`covers:` in the base tree and in the working tree.
"""
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from harness.core.cases import load_covers, parse_covers

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


# --- release selection: base tree and working tree; tests/ and .claude/ never select ---

NON_SELECTING = ("tests/", ".claude/")  # tests-only and repo-internal changes carry no version


def selecting_files(changed) -> list[str]:
    """The changed files that may select a test: not under tests/ or .claude/."""
    return [f for f in changed if not f.startswith(NON_SELECTING)]


@dataclass(frozen=True)
class SelectedTest:
    path: str            # repo-relative case file
    agent_mode: bool
    base_covers: tuple   # covers: in the base tree, () when the file is new
    head_covers: tuple   # covers: in the working tree, () when the file is gone
    in_head: bool        # False: the file was deleted on this branch

    @property
    def covers(self) -> tuple:
        return tuple(dict.fromkeys(self.base_covers + self.head_covers))


@dataclass(frozen=True)
class Selection:
    changed: list        # every changed file
    selecting: list      # those allowed to select
    selected: list       # [SelectedTest]: base and working-tree files together, in TEST_KINDS order

    @property
    def deleted(self) -> list[str]:
        return [t.path for t in self.selected if not t.in_head]


def _git_text(repo_root: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def _kind_of(path: str):
    """(index into TEST_KINDS, agent_mode) when `path` is a case file by layout, else None."""
    for i, (folder_glob, name, agent_mode) in enumerate(TEST_KINDS):
        if glob_to_regex(f"tests/{folder_glob}/{name}").match(path):
            return i, agent_mode
    return None


def base_tests(repo_root: Path, ref: str) -> dict:
    """{repo-relative case file: (kind index, agent_mode, covers)} as committed at `ref`."""
    found = {}
    for path in _git_text(repo_root, "ls-tree", "-r", "--name-only", ref, "--", "tests").splitlines():
        kind = _kind_of(path)
        if kind is not None:
            covers = parse_covers(f"{ref}:{path}", _git_text(repo_root, "show", f"{ref}:{path}"))
            found[path] = (kind[0], kind[1], covers)
    return found


def head_tests(repo_root: Path) -> dict:
    """The same map for the working tree."""
    found = {}
    for path, _ in discover(repo_root / "tests"):
        rel = path.relative_to(repo_root).as_posix()
        kind = _kind_of(rel)
        found[rel] = (kind[0], kind[1], load_covers(path))
    return found


def select_for_base(repo_root: Path, base: str, changed) -> Selection:
    """The case files a release must have tested: those whose base-or-head
    `covers:` match a changed file that is allowed to select. `tests/releases/**`
    is under tests/, so it never selects."""
    selecting = selecting_files(changed)
    old, new = base_tests(repo_root, base), head_tests(repo_root)
    selected = []
    for path in sorted(set(old) | set(new), key=lambda p: ((new.get(p) or old[p])[0], p)):
        agent_mode = (new.get(path) or old[path])[1]
        t = SelectedTest(path, agent_mode, old[path][2] if path in old else (),
                         new[path][2] if path in new else (), path in new)
        if any(matches(t.covers, f) for f in selecting):
            selected.append(t)
    return Selection(list(changed), selecting, selected)
