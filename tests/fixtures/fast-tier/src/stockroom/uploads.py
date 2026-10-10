"""Upload limits."""
from stockroom import settings


def retry_limit() -> int:
    return settings.get("uploads", "max_retries", 3)
