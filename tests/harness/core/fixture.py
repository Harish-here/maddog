"""Build a fresh practice repo for one run, outside this repo. Names no
runtime.

Workdir paths are stable per job slot (`SlotPool`), not randomized per run:
the same path, the same fixture content, and the same commit dates
(`FIXED_GIT_DATE`) make a session's system prompt byte-identical run to
run, which is what lets the runtime's prompt cache actually hit."""
import fcntl
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR
from harness.core import sweep

FIXTURES_DIR = TESTS_DIR / "fixtures"
REPO_ROOT = TESTS_DIR.parent

# One fixed instant for every commit make_workdir creates, so identical
# fixture content always hashes to the identical commit, run after run.
FIXED_GIT_DATE = "2020-01-01T00:00:00+0000"

# Keep the user's git config (hooks, signing, identity) out of fixture repos.
GIT = ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
       "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"]


def _git(workdir: Path, *args: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_DATE": FIXED_GIT_DATE, "GIT_COMMITTER_DATE": FIXED_GIT_DATE}
    subprocess.run([*GIT, "-C", str(workdir), *args], check=True, capture_output=True, env=env)


def make_workdir(name: str, slot_path: Path) -> Path:
    """Empty and rebuild `<slot_path>/<name>` as a fresh copy of fixture
    `name`, with its branch patches applied. `slot_path` is reused across
    every run in one job slot (see `SlotPool`), so the returned path -- and,
    with `FIXED_GIT_DATE`, every commit hash inside it -- is identical run
    to run."""
    source = FIXTURES_DIR / name
    if not source.is_dir():
        raise FileNotFoundError(f"no fixture named {name!r} in {FIXTURES_DIR}")

    slot_path = Path(slot_path).resolve()
    if slot_path.is_relative_to(REPO_ROOT.resolve()):
        raise RuntimeError(f"slot folder {slot_path} is inside this repo; a repo CLAUDE.md would leak into the session")

    workdir = slot_path / name
    shutil.rmtree(workdir, ignore_errors=True)
    slot_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, workdir, ignore=shutil.ignore_patterns("*.patch", "__pycache__"))
    _git(workdir, "init", "-q", "-b", "main")
    _git(workdir, "add", "-A")
    _git(workdir, "commit", "-q", "-m", "initial")

    for patch in sorted(source.glob("*.patch")):
        branch = patch.stem.replace("-", "/", 1)  # feature-export.patch → feature/export
        _git(workdir, "switch", "-q", "-c", branch)
        _git(workdir, "apply", str(patch))
        _git(workdir, "add", "-A")
        _git(workdir, "commit", "-q", "-m", f"work on {branch}")
        _git(workdir, "switch", "-q", "main")
    return workdir


def _git_out(workdir: Path, *args: str) -> str:
    return subprocess.run([*GIT, "-c", "core.quotepath=off", "-C", str(workdir), *args],
                          check=True, capture_output=True, text=True).stdout


def changed_files(workdir: Path) -> list[str]:
    """Paths (relative to `workdir`, sorted) that differ from the fixture's
    first commit when a session ends: modified, deleted, or new files, whether
    the agent left them uncommitted, staged, or committed. Agent mode records
    these as `changed` events, so a check sees an edit made by any means (an
    edit tool, sed -i, a redirect, git commit) and an untouched file.
    Git-ignored files (the fixture's own __pycache__) never count."""
    root = _git_out(workdir, "rev-list", "--max-parents=0", "HEAD").split()[0]
    changed = set(_git_out(workdir, "diff", "--name-only", "--no-renames", root).splitlines())
    changed |= set(_git_out(workdir, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(changed)


def remove_workdir(workdir: Path) -> None:
    shutil.rmtree(Path(workdir), ignore_errors=True)


class SlotPool:
    """Hands out `jobs` stable slot directories under the system temp dir
    (or `base`), one per concurrent job, named `maddog-run-<n>`. Each is
    held with an exclusive advisory lock (`flock`) for this process's life,
    so two processes never share a slot: if slot `n` is already locked
    elsewhere, the next free number is tried. Locking, not a marker file, is
    what prevents the collision, because an `flock` disappears the instant
    its owning process dies or exits -- no stale-lock detection is needed
    for this part. A marker file is still written in every slot, for the
    startup sweep (`sweep.py`) to use if this process is later killed
    without a chance to release its lock or remove its folders.

    A slot's directory is reused, never recreated, across every run this
    process makes -- that stability is what lets the workdir path (and, via
    `FIXED_GIT_DATE`, its commit hashes) stay identical run to run, for the
    prompt cache."""

    def __init__(self, jobs: int, base: Path | None = None):
        self.base = Path(base) if base is not None else Path(tempfile.gettempdir())
        self._locks: list = []
        self.paths: list[Path] = []
        candidate = 0
        while len(self.paths) < jobs:
            path = self.base / f"{sweep.RUN_SLOT_PREFIX}{candidate}"
            path.mkdir(parents=True, exist_ok=True)
            lock_file = open(path / ".lock", "w")
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                lock_file.close()
                candidate += 1
                continue
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            sweep.write_marker(path)
            self._locks.append(lock_file)
            self.paths.append(path)
            candidate += 1

    def path(self, slot: int) -> Path:
        return self.paths[slot]

    def close(self) -> None:
        for fh in self._locks:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            fh.close()
        for path in self.paths:
            shutil.rmtree(path, ignore_errors=True)
        self._locks = []
        self.paths = []
