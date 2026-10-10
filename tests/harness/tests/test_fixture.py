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


def test_nothing_changed_lists_nothing(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    assert fixture.changed_files(work) == []


def test_modified_deleted_and_new_files_are_listed_relative_and_sorted(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    (work / "src" / "todo" / "store.py").write_text("# edited\n")
    (work / "CHANGELOG.md").unlink()
    (work / "notes").mkdir()
    (work / "notes" / "new.txt").write_text("x")
    assert fixture.changed_files(work) == ["CHANGELOG.md", "notes/new.txt", "src/todo/store.py"]


def test_a_committed_edit_and_a_staged_new_file_are_still_listed(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    (work / "src" / "todo" / "store.py").write_text("# edited\n")
    (work / "staged.txt").write_text("x")
    subprocess.run([*fixture.GIT, "-C", str(work), "add", "-A"], check=True)
    subprocess.run([*fixture.GIT, "-C", str(work), "commit", "-q", "-m", "agent commit"], check=True)
    (work / "later.txt").write_text("y")
    subprocess.run([*fixture.GIT, "-C", str(work), "add", "later.txt"], check=True)
    assert fixture.changed_files(work) == ["later.txt", "src/todo/store.py", "staged.txt"]


def test_a_git_ignored_file_does_not_count(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    (work / ".gitignore").write_text("*.pyc\n")
    (work / "a.pyc").write_text("x")
    assert fixture.changed_files(work) == [".gitignore"]


def test_a_file_changed_by_a_shell_edit_is_listed(tmp_path):
    work = fixture.make_workdir("todo-app", tmp_path)
    subprocess.run(["sed", "-i.bak", "s/add_item/create_item/", "src/todo/store.py"], cwd=work, check=True)
    assert "src/todo/store.py" in fixture.changed_files(work)
