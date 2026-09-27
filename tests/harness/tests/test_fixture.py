import subprocess

import pytest
from harness.core import fixture
from harness.core.cases import TESTS_DIR

REPO = TESTS_DIR.parent


def git(workdir, *args):
    return subprocess.run(["git", "-C", str(workdir), *args], capture_output=True, text=True, check=True).stdout


def test_workdir_is_a_git_repo_outside_this_repo(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    try:
        assert not work.resolve().is_relative_to(REPO.resolve())
        assert git(work, "branch", "--show-current").strip() == "main"
        assert (work / "src" / "todo" / "store.py").exists()
        assert not list(work.glob("*.patch"))
    finally:
        fixture.remove_workdir(work)
    assert not work.exists()


def test_patch_becomes_a_branch(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    try:
        branches = git(work, "branch", "--format=%(refname:short)").split()
        assert "feature/export" in branches
        files = git(work, "diff", "--name-only", "main", "feature/export").split()
        assert "src/todo/export.py" in files
        assert not (work / "src" / "todo" / "export.py").exists()  # main stays checked out
    finally:
        fixture.remove_workdir(work)


def test_refuses_a_slot_inside_this_repo():
    with pytest.raises(RuntimeError, match="inside this repo"):
        fixture.make_workdir("todo-app", REPO / "tests")


def test_unknown_fixture_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        fixture.make_workdir("no-such-app", tmp_path)


def test_slot_path_is_identical_across_two_runs_in_one_slot(tmp_path):
    slot_dir = tmp_path / "slot"
    work1 = fixture.make_workdir("todo-app", slot_dir)
    path1 = str(work1)
    fixture.remove_workdir(work1)

    work2 = fixture.make_workdir("todo-app", slot_dir)
    try:
        assert str(work2) == path1
    finally:
        fixture.remove_workdir(work2)


def test_two_builds_produce_identical_commit_hashes(tmp_path):
    work1 = fixture.make_workdir("todo-app", tmp_path / "slot-a")
    sha1 = git(work1, "rev-parse", "HEAD").strip()
    fixture.remove_workdir(work1)

    work2 = fixture.make_workdir("todo-app", tmp_path / "slot-b")
    try:
        sha2 = git(work2, "rev-parse", "HEAD").strip()
        assert sha1 == sha2
    finally:
        fixture.remove_workdir(work2)
