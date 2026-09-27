from datetime import date

import pytest
from todo.due import parse_due, is_overdue


def test_parse_due_reads_iso_dates():
    assert parse_due("2026-10-01") == date(2026, 10, 1)


def test_parse_due_rejects_garbage():
    with pytest.raises(ValueError):
        parse_due("next week")


def test_is_overdue():
    assert is_overdue("2026-01-01", today=date(2026, 2, 1))
