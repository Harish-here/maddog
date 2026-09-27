from datetime import date, timedelta

from todo import cli, store


def test_add_and_list(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "milk"])
    cli.main(["list"])
    assert "1. milk" in capsys.readouterr().out


def test_done_hides_item(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "milk"])
    cli.main(["done", "1"])
    cli.main(["list"])
    assert "milk" not in capsys.readouterr().out


def test_list_due_before_today(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    store.add_item("old", due=yesterday)
    cli.main(["list", "--due-before", date.today().isoformat()])
    assert "old" in capsys.readouterr().out
