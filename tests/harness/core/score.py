"""Score one run from its event log. Pure logic; names no runtime."""
from dataclasses import dataclass

from harness.core.events import Event


@dataclass(frozen=True)
class Verdict:
    result: str  # PASS | FAIL | VOID
    reason: str


def score(events: list[Event], expect: str) -> Verdict:
    for event in events:
        if event.kind == "refused":
            return Verdict("VOID", f"a command was refused: {event.detail}")

    calls_before_handoff = 0
    for event in events:
        if event.kind == "handoff":
            if event.detail == expect:
                return Verdict("PASS", f"handed to {expect}")
            return Verdict("FAIL", f"first handoff went to {event.detail}, expected {expect}")
        if event.kind == "write":
            return Verdict("FAIL", f"advisor wrote before handing off: {event.detail}")
        if event.kind in ("read", "command"):
            calls_before_handoff += 1
            if calls_before_handoff > 1:
                return Verdict("FAIL", "more than one tool call before the handoff")
    return Verdict("FAIL", "no handoff")
