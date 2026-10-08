"""Report lines."""
from stockroom.pricing import line_total

# parse_money is not used here: prices are already floats


def render_line(item: dict) -> str:
    total = line_total(item["qty"], item["price"])
    return f"{item['name']}: {item['qty']} x {item['price']} = {total}"
