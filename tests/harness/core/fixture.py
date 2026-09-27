"""Build a fresh practice repo for one run, outside this repo. Names no runtime."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR

FIXTURES_DIR = TESTS_DIR / "fixtures"
REPO_ROOT = TESTS_DIR.parent

# Keep the user's git config (hooks, signing, identity) out of fixture repos.
GIT = ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
       "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"]


def _git(workdir: Path, *args: str) -> None:
    subprocess.run([*GIT, "-C", str(workdir), *args], check=True, capture_output=True)


def make_workdir(name: str) -> Path:
    source = FIXTURES_DIR / name
    if not source.is_dir():
        raise FileNotFoundError(f"no fixture named {name!r} in {FIXTURES_DIR}")

    root = Path(tempfile.mkdtemp(prefix=f"maddog-test-{name}-"))
    if root.resolve().is_relative_to(REPO_ROOT.resolve()):
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError(f"temp folder {root} is inside this repo; a repo CLAUDE.md would leak into the session")

    workdir = root / name
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


def remove_workdir(workdir: Path) -> None:
    shutil.rmtree(Path(workdir).parent, ignore_errors=True)
