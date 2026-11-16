"""Plugin copies to compare (this working tree and main), and a skills-only plugin copy. Names no runtime."""
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


def skills_only_plugin(source: Path, skill_ids: tuple[str, ...]) -> Path:
    """Create a temporary plugin folder holding only the named skills of `source`.

    Same temp-folder pattern as branch_with_skill (maddog-skills- prefix, sweep
    marker, plugin under `<root>/plugin`), but nothing else is copied: no hooks,
    agents, scripts or commands, so a run that loads this plugin can load those
    skills and fire nothing from the repo. A skill `source` lacks is skipped.
    The caller removes `plugin.parent` after the run."""
    root = Path(tempfile.mkdtemp(prefix="maddog-skills-")).resolve()
    sweep.write_marker(root)
    plugin = root / "plugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text('{"name": "maddog"}\n')  # the name skills are loaded under: maddog:<skill>
    for skill_id in skill_ids:
        src = Path(source) / "skills" / skill_id
        if src.is_dir():
            shutil.copytree(src, plugin / "skills" / skill_id)
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
