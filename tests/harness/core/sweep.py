"""Startup cleanup for leftover run/test/baseline temp folders (and their
registered git worktrees) that a killed or crashed process left behind.

Never sweeps on prefix alone: a folder is removed only when its ownership
marker names a PID that is no longer alive, or it carries no marker and is
older than 24 hours -- so a live sibling process's own folders are always
left alone. Names no runtime."""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

MARKER_NAME = ".maddog-owner-pid"
RUN_SLOT_PREFIX = "maddog-run-"
PREFIXES = (RUN_SLOT_PREFIX, "maddog-test-", "maddog-baseline-")
STALE_AGE_SECONDS = 24 * 60 * 60


def write_marker(folder: Path) -> None:
    """Record this process's pid as the owner of a temp folder it just
    created, so a later sweep (in this process or another) can tell a live
    folder from an abandoned one."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / MARKER_NAME).write_text(str(os.getpid()))


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True  # exists, just not owned by us
    return True


def _abandoned(folder: Path) -> bool:
    marker = folder / MARKER_NAME
    if marker.exists():
        try:
            pid = int(marker.read_text().strip())
        except (ValueError, OSError):
            return True  # unreadable marker: treat as abandoned
        return not _pid_alive(pid)
    age = time.time() - folder.stat().st_mtime
    return age > STALE_AGE_SECONDS


def _deregister_worktree(repo_root: Path, folder: Path) -> None:
    # A worktree may live directly at `folder` (baseline.py's own root) or
    # one level under it (baseline.py nests the checkout at `folder/plugin`).
    # `git worktree remove` on a path that isn't a registered worktree just
    # fails harmlessly; we swallow that either way.
    for candidate in (folder, folder / "plugin"):
        subprocess.run(["git", "-C", str(repo_root), "worktree", "remove", "--force", str(candidate)],
                       capture_output=True)


def sweep(repo_root: Path, base: Path | None = None) -> list[Path]:
    """Removes every abandoned `maddog-run-*` / `maddog-test-*` /
    `maddog-baseline-*` folder directly under `base` (default: the system
    temp dir), deregistering any git worktree registered at it first.
    Returns the folders removed, so the caller can report them."""
    base = Path(base) if base is not None else Path(tempfile.gettempdir())
    removed: list[Path] = []
    if not base.is_dir():
        return removed
    for entry in sorted(base.iterdir()):
        if not entry.is_dir() or not entry.name.startswith(PREFIXES):
            continue
        if not _abandoned(entry):
            continue
        _deregister_worktree(repo_root, entry)
        shutil.rmtree(entry, ignore_errors=True)
        removed.append(entry)
    if removed:
        subprocess.run(["git", "-C", str(repo_root), "worktree", "prune"], capture_output=True)
    return removed
