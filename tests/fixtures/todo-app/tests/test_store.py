from todo import store


def test_add_item_assigns_ids(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    assert store.add_item("a")["id"] == 1
    assert store.add_item("b")["id"] == 2


def test_mark_done(tmp_path, monkeypatch):
    monkeypatch.setenv("TODO_FILE", str(tmp_path / "t.json"))
    store.add_item("a")
    store.mark_done(1)
    assert store.load()[0]["done"] is True
