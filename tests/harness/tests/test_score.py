from harness.core.events import Event
from harness.core.score import score, settled


def test_right_helper_first_passes():
    assert score([Event("handoff", "Fast")], "Fast").result == "PASS"


def test_skill_load_and_one_read_before_handoff_pass():
    events = [Event("skill_load", "efficient-md"), Event("read", "Read"), Event("handoff", "Fast")]
    assert score(events, "Fast").result == "PASS"


def test_two_tool_calls_before_handoff_fail():
    events = [Event("read", "Read"), Event("command", "ls"), Event("handoff", "Fast")]
    v = score(events, "Fast")
    assert v.result == "FAIL" and "more than one" in v.reason


def test_wrong_helper_fails_and_names_it():
    v = score([Event("handoff", "Smart")], "Fast")
    assert v.result == "FAIL" and "Smart" in v.reason


def test_unknown_agent_fails_and_names_it():
    v = score([Event("handoff", "other:general-purpose")], "Fast")
    assert v.result == "FAIL" and "general-purpose" in v.reason


def test_write_before_handoff_fails():
    v = score([Event("write", "src/todo/store.py")], "Fast")
    assert v.result == "FAIL" and "wrote" in v.reason


def test_no_handoff_fails():
    v = score([Event("read", "Read")], "Fast")
    assert v.result == "FAIL" and v.reason == "no handoff"


def test_empty_log_fails_as_no_handoff():
    assert score([], "Fast").reason == "no handoff"


def test_any_refusal_voids_even_with_a_right_handoff():
    events = [Event("command", "git log"), Event("refused", "git log"), Event("handoff", "Fast")]
    assert score(events, "Fast").result == "VOID"


def test_settled_after_a_write():
    assert settled([Event("write", "src/todo/store.py")]) is True


def test_settled_after_a_handoff():
    assert settled([Event("handoff", "Fast")]) is True


def test_settled_after_two_read_or_command_events():
    assert settled([Event("read", "Read"), Event("command", "ls")]) is True


def test_not_settled_after_one_read_or_command_event():
    assert settled([Event("read", "Read")]) is False
    assert settled([Event("command", "ls")]) is False


def test_a_refusal_alone_does_not_settle_the_run():
    # score() still VOIDs a run with a refusal anywhere in it; settled()
    # only tracks whether PASS is still reachable, which a lone refused
    # event (with no write/handoff/second call) does not rule out.
    assert settled([Event("refused", "git log")]) is False


def test_settled_agrees_with_score_on_the_pass_boundary():
    # One skill_load plus one read before a handoff still passes; settled()
    # must not fire before that handoff.
    events = [Event("skill_load", "efficient-md"), Event("read", "Read")]
    assert settled(events) is False
    events.append(Event("handoff", "Fast"))
    assert settled(events) is True
    assert score(events, "Fast").result == "PASS"
