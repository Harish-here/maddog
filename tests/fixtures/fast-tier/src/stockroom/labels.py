"""Shelf labels."""
from stockroom.fmt import fmt_price


def label_for(item: dict) -> str:
    return f"{item['name']}  {fmt_price(item['price'])}"
