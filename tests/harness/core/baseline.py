"""Plugin copies to compare: this working tree and main. Names no runtime."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness.core.cases import TESTS_DIR
from harness.core import sweep

REPO_ROOT = TESTS_DIR.parent


def branch_with_skill(skill_file: Path, skill_id: str) -> Path:
    """Create a temporary plugin copy with a replaced skill file.

    Creates a temp folder with maddog-skillfile- prefix, writes the sweep PID
    marker, copies the repo's plugin surface (agents, skills, commands, hooks,
    scripts, workflows, .mcp.json, .claude-plugin), and overwrites the named
    skill's SKILL.md with the given file's contents. Returns the plugin path.
    """
    root = Path(tempfile.mkdtemp(prefix="maddog-skillfile-")).resolve()
    sweep.write_marker(root)
    plugin = root / "plugin"
    plugin.mkdir(parents=True, exist_ok=True)

    # Copy plugin surface: everything except .git, tests, docs, and git-ignored files.
    # Minimal set: .claude-plugin, agents, skills, commands, hooks, scripts, workflows, .mcp.json
    for item_name in [".claude-plugin", "agents", "skills", "commands", "hooks", "scripts", "workflows", ".mcp.json"]:
        src = REPO_ROOT / item_name
        if src.exists():
            dst = plugin / item_name
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)

    # Overwrite the skill's SKILL.md with the given file.
    skill_md = plugin / "skills" / skill_id / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_file, skill_md)

    return plugin


def plugin_versions(ref: str = "main") -> dict[str, Path]:
    # resolve(): on macOS the temp dir sits under the /var symlink, and git
    # worktree list prints the real /private/var path.
    root = Path(tempfile.mkdtemp(prefix="maddog-baseline-")).resolve()
    sweep.write_marker(root)  # lets a later startup sweep tell this folder is ours
    worktree = root / "plugin"
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "worktree", "add", "--detach", "-q", str(worktree), ref],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        shutil.rmtree(root, ignore_errors=True)
        raise RuntimeError(f"could not check out {ref!r} for the baseline: {result.stderr.strip()}")
    return {"branch": REPO_ROOT, "main": worktree}


def main_sha(ref: str = "main") -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", ref],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"could not resolve {ref!r} to a commit: {result.stderr.strip()}")
    return result.stdout.strip()


def remove_baseline(versions: dict[str, Path]) -> None:
    worktree = versions.get("main")
    if worktree is None or worktree == REPO_ROOT:
        return
    subprocess.run(["git", "-C", str(REPO_ROOT), "worktree", "remove", "--force", str(worktree)],
                   capture_output=True)
    shutil.rmtree(worktree.parent, ignore_errors=True)
