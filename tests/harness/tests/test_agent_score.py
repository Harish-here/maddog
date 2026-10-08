import pytest
from harness.core.agent_score import (
    declared_patterns, normalize_command, result_field, score_agent, score_case,
)
from harness.core.cases import AgentCase, Case
from harness.core.events import Event


def make_case(patterns=("TRANSFORM",), first_call=None, **checks):
    first_call = first_call or {"kind": ["read", "command"], "target": "add_item"}
    return AgentCase("X1", "do it", "Fast", "fast-tier", tuple(patterns), first_call, checks)


DECLARE = Event("say", "PATTERNS: TRANSFORM\n- TRANSFORM: search src/ for add_item; the list shows in RESULT")
SEARCH = Event("read", "add_item src")


def run_with(*events):
    return list(events)


# ---- check 1: the PATTERNS line comes before the first call

def test_all_four_pass_on_a_clean_run():
    v = score_agent(run_with(DECLARE, SEARCH), make_case())
    assert v.result == "PASS" and v.checks == {"1": True, "2": True, "3": True, "4": True}


def test_check1_fails_when_the_line_comes_after_the_first_call():
    v = score_agent(run_with(SEARCH, DECLARE), make_case())
    assert v.result == "FAIL" and v.checks["1"] is False and "before the first tool call" in v.reason


def test_check1_fails_when_the_line_is_missing():
    v = score_agent(run_with(Event("say", "Let me look."), SEARCH), make_case())
    assert v.checks["1"] is False and v.checks["2"] is False and v.checks["3"] is True


def test_check1_accepts_markup_around_the_marker_and_check2_reads_the_names_on_its_line():
    v = score_agent(run_with(Event("say", "**PATTERNS:** TRANSFORM"), SEARCH), make_case())
    assert v.checks["1"] is True and v.checks["2"] is True


@pytest.mark.parametrize("text, counts", [
    ("PATTERNS: SWEEP", True),
    ("Starting.\nPATTERNS: SWEEP\n- SWEEP: x; y", True),
    ("   PATTERNS: SWEEP", True),
    ("**PATTERNS:** SWEEP", True),
    ("## PATTERNS: SWEEP", True),
    ("I will write PATTERNS: SWEEP soon", True),
    ("patterns: sweep", False),
    ("No marker in this text.", False),
])
def test_the_marker_rule_is_the_hooks_rule(text, counts):
    # Same cases as test_the_marker_rule_is_the_scorers_rule in tests/guard/test_pattern_declare_guard.py.
    assert (declared_patterns([text]) is not None) is counts


def test_line_in_the_same_text_as_other_words_counts():
    text = "I will start now.\nPATTERNS: TRANSFORM\n- TRANSFORM: x; y"
    assert declared_patterns([text]) == ["TRANSFORM"]


# ---- check 2: declared covers expected

def test_check2_passes_when_declared_is_a_superset():
    say = Event("say", "PATTERNS: CHANGE, TRANSFORM, VERIFY")
    assert score_agent(run_with(say, SEARCH), make_case()).checks["2"] is True


def test_check2_is_a_superset_test_so_naming_every_pattern_passes_it():
    say = Event("say", "PATTERNS: CHANGE, OPERATE, TRANSFORM, RECOVER, VERIFY, REPRODUCE")
    assert score_agent(run_with(say, SEARCH), make_case()).checks["2"] is True


def test_check2_fails_and_names_the_missing_pattern():
    say = Event("say", "PATTERNS: CHANGE")
    v = score_agent(run_with(say, SEARCH), make_case(patterns=("TRANSFORM", "VERIFY")))
    assert v.checks["2"] is False and "TRANSFORM" in v.reason and "VERIFY" in v.reason


# ---- check 3: first call

def test_check3_fails_on_the_wrong_target():
    v = score_agent(run_with(DECLARE, Event("read", "src/stockroom/store.py")), make_case())
    assert v.checks["3"] is False and "does not match" in v.reason


def test_check3_fails_on_the_wrong_kind():
    v = score_agent(run_with(DECLARE, Event("write", "add_item")), make_case())
    assert v.checks["3"] is False and "expected kind" in v.reason


def test_check3_fails_with_no_call_at_all():
    v = score_agent(run_with(DECLARE), make_case())
    assert v.checks["3"] is False and "no tool call" in v.reason


# ---- setup steps are not scored (cd, pushd, export, set -e, VAR=value)

@pytest.mark.parametrize("setup", ["cd /w", "pushd /w", "export PYTHONDONTWRITEBYTECODE=1", "set -e", "set -euo pipefail",
                                   "unset X", "PYTHONDONTWRITEBYTECODE=1"])
def test_check3_skips_a_setup_step_before_the_real_first_call(setup):
    v = score_agent(run_with(DECLARE, Event("command", setup), SEARCH), make_case())
    assert v.checks["3"] is True


def test_a_lone_cd_followed_by_an_edit_still_fails_check3():
    case = make_case(first_call={"kind": ["read", "command"], "target": "add_item"})
    v = score_agent(run_with(DECLARE, Event("command", "cd /w"), Event("write", "/w/src/stockroom/store.py")), case)
    assert v.checks["3"] is False and "write" in v.reason


def test_a_setup_step_does_not_count_as_a_call_for_before_or_command_runs():
    case = make_case(command_runs="python3 -m unittest tests.test_pricing",
                     first_call={"kind": ["command"], "target": "unittest"})
    events = run_with(DECLARE, Event("command", "cd /w"), Event("command", "python3 -m unittest tests.test_pricing"))
    assert score_agent(events, case).result == "PASS"
    # A command that merely starts with the letters cd is not a directory change.
    other = run_with(DECLARE, Event("command", "cdrecord x"), Event("command", "python3 -m unittest tests.test_pricing"))
    assert score_agent(other, case).checks["3"] is False


def test_a_leading_assignment_does_not_change_the_command():
    case = make_case(command_runs="python3 -m unittest tests.test_pricing", first_call={"kind": ["command"], "target": "."})
    events = run_with(DECLARE, Event("command", "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_pricing"))
    assert score_agent(events, case).checks["4"] is True


# ---- check 4: edits

def changed(*paths):
    return [Event("changed", p) for p in paths]


def test_edits_include_passes_and_fails():
    case = make_case(edits_include=["a.py", "b.py"])
    ok = score_agent(run_with(DECLARE, SEARCH, *changed("a.py", "b.py")), case)
    bad = score_agent(run_with(DECLARE, SEARCH, *changed("a.py")), case)
    assert ok.checks["4"] is True
    assert bad.checks["4"] is False and "b.py was not edited" in bad.reason


def test_edits_exclude_passes_and_fails():
    case = make_case(edits_exclude=["bulk.py"])
    assert score_agent(run_with(DECLARE, SEARCH, *changed("a.py")), case).checks["4"] is True
    bad = score_agent(run_with(DECLARE, SEARCH, *changed("a.py", "bulk.py")), case)
    assert bad.checks["4"] is False and "bulk.py was edited" in bad.reason


def test_no_edits_passes_and_fails():
    case = make_case(no_edits=True)
    assert score_agent(run_with(DECLARE, SEARCH), case).checks["4"] is True
    assert score_agent(run_with(DECLARE, SEARCH, *changed("a.py")), case).checks["4"] is False


# ---- check 4: call order

def test_before_passes_when_the_first_earlier_precedes_the_first_later():
    pair = [["service\\.log", "^write:.*\\brm\\b"]]
    any_first = {"kind": ["command", "write"], "target": "."}
    ok = run_with(DECLARE, Event("command", "cat var/service.log"), Event("write", "rm var/app.lock"))
    bad = run_with(DECLARE, Event("write", "rm var/app.lock"), Event("command", "cat var/service.log"))
    assert score_agent(ok, make_case(first_call=any_first, before=pair)).checks["4"] is True
    assert score_agent(bad, make_case(first_call=any_first, before=pair)).checks["4"] is False


def test_before_fails_when_a_side_never_happens():
    case = make_case(before=[["service\\.log", "^write:.*\\brm\\b"]])
    v = score_agent(run_with(DECLARE, SEARCH), case)
    assert v.checks["4"] is False and "no call matches" in v.reason


def test_before_with_the_same_call_on_both_sides_fails():
    # One `rm .../app.lock` call matches both patterns: it does not come before itself.
    case = make_case(before=[["app\\.lock", "^write:.*\\brm\\b.*app\\.lock"]],
                     first_call={"kind": ["write"], "target": "."})
    v = score_agent(run_with(DECLARE, Event("write", "rm var/app.lock")), case)
    assert v.checks["4"] is False


def test_then_compares_the_last_matches():
    case = make_case(then=[["^write:", "unittest"]], first_call={"kind": ["write", "command"], "target": "."})
    ok = run_with(DECLARE, Event("write", "a.py"), Event("command", "python3 -m unittest tests.test_labels"))
    edit_after_test = run_with(DECLARE, Event("command", "python3 -m unittest tests.test_labels"), Event("write", "a.py"))
    assert score_agent(ok, case).checks["4"] is True
    assert score_agent(edit_after_test, case).checks["4"] is False


# ---- check 4: command

def test_command_runs_accepts_a_stderr_redirect_and_a_pipeline_head_only():
    case = make_case(command_runs="python3 -m unittest tests.test_pricing", first_call={"kind": ["command"], "target": "."})
    exact = Event("command", "python3 -m unittest tests.test_pricing")
    redirected = Event("command", "python3 -m unittest tests.test_pricing 2>&1")
    piped = Event("command", "python3 -m unittest tests.test_pricing 2>&1 | tail -20")
    changed_cmd = Event("command", "python3 -m unittest tests.test_pricing -k fractional")
    assert score_agent(run_with(DECLARE, exact), case).checks["4"] is True
    assert score_agent(run_with(DECLARE, redirected), case).checks["4"] is True
    assert score_agent(run_with(DECLARE, piped), case).checks["4"] is True
    assert score_agent(run_with(DECLARE, changed_cmd), case).checks["4"] is False


def test_normalize_command():
    assert normalize_command("  ls -l 2>&1 | head ") == "ls -l"


# ---- check 4: the return

RETURN = """STATUS: done
RESULT: src/a.py:3 `price = money.parse_money(x)`
NOT DONE: misfit left: `def parse_money_cents(text: str) -> int:`
NOTES: none"""


def test_return_quotes_pass_and_fail():
    case = make_case(first_call={"kind": ["read"], "target": "."}, return_quotes=["price = money.parse_money(x)"])
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", RETURN)), case).checks["4"] is True
    bad = score_agent(run_with(DECLARE, SEARCH, Event("final", "RESULT: none")), case)
    assert bad.checks["4"] is False and "return lacks" in bad.reason


def test_return_lacks_reads_the_result_field_only():
    case = make_case(return_lacks=["def parse_money_cents(text: str) -> int:"])
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", RETURN)), case).checks["4"] is True  # it is in NOT DONE
    leaked = RETURN.replace("RESULT: src/a.py:3", "RESULT: def parse_money_cents(text: str) -> int:\nsrc/a.py:3")
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", leaked)), case).checks["4"] is False


def test_label_passes_only_when_it_is_the_one_label_in_result():
    case = make_case(label="CONTRADICTED")
    good = "RESULT: CONTRADICTED `max_upload_mb = 25`\nNOT DONE: none"
    wrong = "RESULT: CONFIRMED `max_upload_mb = 25`\nNOT DONE: none"
    both = "RESULT: CONTRADICTED then CONFIRMED\nNOT DONE: none"
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", good)), case).checks["4"] is True
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", wrong)), case).checks["4"] is False
    assert score_agent(run_with(DECLARE, SEARCH, Event("final", both)), case).checks["4"] is False
    assert score_agent(run_with(DECLARE, SEARCH), case).checks["4"] is False  # no return at all


def test_no_label_check_ignores_labels_in_not_done():
    assert result_field("RESULT: a\nNOT DONE: NO EVIDENCE for b").strip() == "a"


# ---- whole-run behaviour

def test_an_empty_run_fails_every_check_without_raising():
    v = score_agent([], make_case(edits_include=["a.py"], return_quotes=["q"]))
    assert v.result == "FAIL" and v.checks == {"1": False, "2": False, "3": False, "4": False}


def test_a_refusal_voids_the_run():
    v = score_agent(run_with(DECLARE, Event("refused", "Permission denied")), make_case())
    assert v.result == "VOID" and v.checks is None


def test_score_case_keeps_skill_scoring_for_a_skill_case():
    skill_case = Case("c", "p", "Fast", "none", "advisor-mode", "todo-app")
    assert score_case([Event("handoff", "Fast")], skill_case).result == "PASS"
    assert score_case([Event("handoff", "Fast")], skill_case).checks is None
