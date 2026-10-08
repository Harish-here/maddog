"""Money parsing."""


def parse_money(text: str) -> float:
    return round(float(text.replace("$", "").replace(",", "")), 2)


def parse_money_cents(text: str) -> int:
    return int(round(parse_money(text) * 100))
