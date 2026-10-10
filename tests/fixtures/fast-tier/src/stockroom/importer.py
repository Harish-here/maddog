"""Load items from data/items.csv."""
import csv
from pathlib import Path

from stockroom import money, store

_CSV = Path(__file__).resolve().parents[2] / "data" / "items.csv"


def load_items() -> list[dict]:
    items = []
    with open(_CSV, newline="") as f:
        for row in csv.DictReader(f):
            price = money.parse_money(row["price"])
            items.append(store.add_item(row["name"], int(row["qty"]), price))
    return items
