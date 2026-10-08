import subprocess

from harness.core import fixture


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
