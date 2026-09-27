"""Plugin copies to compare: this working tree and main. Names no runtime."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR

REPO_ROOT = TESTS_DIR.parent


def plugin_versions(ref: str = "main") -> dict[str, Path]:
    # resolve(): on macOS the temp dir sits under the /var symlink, and git
    # worktree list prints the real /private/var path.
    root = Path(tempfile.mkdtemp(prefix="maddog-baseline-")).resolve()
    worktree = root / "plugin"
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "worktree", "add", "--detach", "-q", str(worktree), ref],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError(f"could not check out {ref!r} for the baseline: {result.stderr.strip()}")
    return {"branch": REPO_ROOT, "main": worktree}


def remove_baseline(versions: dict[str, Path]) -> None:
    worktree = versions.get("main")
    if worktree is None or worktree == REPO_ROOT:
        return
    subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "remove", "--force", str(worktree)],
                   capture_output=True)
    shutil.rmtree(worktree.parent, ignore_errors=True)
