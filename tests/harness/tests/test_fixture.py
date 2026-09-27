import subprocess
from pathlib import Path

import pytest
from harness.core import fixture
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def git(workdir, *args):
    return subprocess.run(["git", "-C", str(workdir), *args], capture_output=True, text=True, check=True).stdout


def test_workdir_is_a_git_repo_outside_this_repo():
    work = fixture.make_workdir("todo-app")
    try:
        assert not work.resolve().is_relative_to(REPO.resolve())
        assert git(work, "branch", "--show-current").strip() == "main"
        assert (work / "src" / "todo" / "store.py").exists()
        assert not list(work.glob("*.patch"))
    finally:
        fixture.remove_workdir(work)
    assert not work.exists()


def test_patch_becomes_a_branch():
    work = fixture.make_workdir("todo-app")
    try:
        branches = git(work, "branch", "--format=%(refname:short)").split()
        assert "feature/export" in branches
        files = git(work, "diff", "--name-only", "main", "feature/export").split()
        assert "src/todo/export.py" in files
        assert not (work / "src" / "todo" / "export.py").exists()  # main stays checked out
    finally:
        fixture.remove_workdir(work)


def test_refuses_a_temp_dir_inside_this_repo(monkeypatch):
    monkeypatch.setenv("TMPDIR", str(REPO / "tests"))
    import tempfile
    monkeypatch.setattr(tempfile, "tempdir", None)
    with pytest.raises(RuntimeError, match="inside this repo"):
        fixture.make_workdir("todo-app")


def test_unknown_fixture_is_an_error():
    with pytest.raises(FileNotFoundError):
        fixture.make_workdir("no-such-app")
