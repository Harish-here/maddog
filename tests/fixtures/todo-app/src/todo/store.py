import json
import os
from pathlib import Path


def _path() -> Path:
    return Path(os.environ.get("TODO_FILE", "todo.json"))


def load() -> list[dict]:
    path = _path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save(items: list[dict]) -> None:
    _path().write_text(json.dumps(items, indent=2))


def add_item(title: str, due: str | None = None, priority: int = 2) -> dict:
    items = load()
    item = {"id": len(items) + 1, "title": title, "due": due, "priority": priority, "done": False}
    items.append(item)
    save(items)
    return item


def mark_done(item_id: int) -> None:
    items = load()
    for item in items:
        if item["id"] == item_id:
            item["done"] = True
    save(items)
