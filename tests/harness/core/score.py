"""Score one run from its event log. Pure logic; names no runtime."""
from dataclasses import dataclass

from harness.core.cases import AgentCase
from harness.core.events import Event


@dataclass(frozen=True)
class Verdict:
    result: str  # PASS | FAIL | VOID
    reason: str
    checks: dict | None = None  # agent cases: {"1": bool, "2": bool, "3": bool, "4": bool}; skill cases: None


def score_case(events: list[Event], case) -> Verdict:
    """The one entry point the runner calls: agent cases get four checks,
    skill cases keep the handoff score."""
    if isinstance(case, AgentCase):
        from harness.core.agent_score import score_agent  # agent_score imports Verdict from here
        return score_agent(events, case)
    return score(events, case.expect)


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


def settled(events: list[Event]) -> bool:
    """True once the run's score can no longer become PASS: mirrors score()'s
    own PASS path. Settled after a write, after any handoff, or once a
    second read/command event arrives before a handoff (score() would then
    return FAIL regardless of what follows). Ignores refused/skill_load
    events, same as score() does when counting calls before a handoff.

    The adapter uses this to end a session early. It checks settled() only
    after a tool call's result has been observed, so a refusal on the very
    call that settles the run is still recorded as VOID rather than missed."""
    calls = 0
    for event in events:
        if event.kind in ("write", "handoff"):
            return True
        if event.kind in ("read", "command"):
            calls += 1
            if calls > 1:
                return True
    return False
