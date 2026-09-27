from datetime import date, datetime


def parse_due(text: str) -> date:
    """Parse a due date written as YYYY-MM-DD."""
    return datetime.strptime(text, "%Y-%m-%d").date()


def is_overdue(due: str, today: date | None = None) -> bool:
    today = today or date.today()
    return parse_due(due) < today
