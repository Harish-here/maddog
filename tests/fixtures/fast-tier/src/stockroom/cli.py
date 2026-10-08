"""Command-line entry for stockroom."""
from stockroom import money, store
from stockroom.fmt import fmt_price
from stockroom.remote import fetch_stock
from stockroom.report import render_line


def cmd_add(name: str, qty: str, price_text: str) -> str:
    price = money.parse_money(price_text)
    item = store.add_item(name, int(qty), price)
    return f"added {item['name']} at {fmt_price(item['price'])}"


def cmd_report(item_id: int) -> str:
    return render_line(store.get_item(item_id))


def cmd_sync() -> list[dict]:
    return fetch_stock("warehouse-1")
