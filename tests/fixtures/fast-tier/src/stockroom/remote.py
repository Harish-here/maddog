"""Fetch stock levels from the warehouse service."""
from stockroom import settings


def fetch_stock(warehouse: str) -> list[dict]:
    timeout = settings.get("remote", "timeout", 15)
    return _request(warehouse, timeout)


def _request(warehouse: str, timeout: int) -> list[dict]:
    raise NotImplementedError("network access is not part of this fixture")
