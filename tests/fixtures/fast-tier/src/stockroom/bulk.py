"""Bulk helpers."""


def add_items_bulk(rows: list[tuple[str, int, float]]) -> int:
    """Count the rows a bulk load would add. Writes nothing."""
    return len(rows)
