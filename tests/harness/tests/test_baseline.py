import subprocess
import pytest
from harness.core import baseline
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def worktrees():
    return subprocess.run(["git", "-C", str(REPO), "worktree", "list"], capture_output=True, text=True).stdout


def test_versions_are_branch_and_main():
    versions = baseline.plugin_versions()
    try:
        assert versions["branch"] == REPO
        assert (versions["main"] / "skills" / "advisor-mode" / "SKILL.md").exists()
        assert str(versions["main"]) in worktrees()
    finally:
        baseline.remove_baseline(versions)
    assert str(versions["main"]) not in worktrees()
    assert REPO.exists()


def test_unknown_ref_is_a_clear_error():
    with pytest.raises(RuntimeError, match="no-such-ref"):
        baseline.plugin_versions("no-such-ref")
