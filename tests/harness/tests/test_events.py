import pytest
from harness.core.events import Event, KINDS


def test_kinds_are_the_six_from_the_spec():
    assert KINDS == ("handoff", "write", "read", "command", "skill_load", "refused")


def test_event_rejects_unknown_kind():
    with pytest.raises(ValueError):
        Event("edit")


def test_event_to_dict():
    assert Event("handoff", "Fast").to_dict() == {"kind": "handoff", "detail": "Fast"}
