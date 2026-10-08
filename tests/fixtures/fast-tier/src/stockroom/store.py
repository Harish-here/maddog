"""Stock levels, kept in memory."""

_items: dict[int, dict] = {}


def add_item(name: str, qty: int, price: float) -> dict:
    item_id = len(_items) + 1
    item = {"id": item_id, "name": name, "qty": qty, "price": price}
    _items[item_id] = item
    return item


def get_item(item_id: int) -> dict:
    return _items[item_id]


def reset() -> None:
    _items.clear()
