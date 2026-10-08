import json

from harness.core.agent_score import score_agent
from harness.core.cases import AgentCase
from harness.core.events import Event
from harness.core.report import render
from harness.core.runner import CaseResult, RunRecord

LADDERS = {"rt": {"low": "l", "mid": "m", "high": "h"}, "expected_tier": {"none": "low", "user": "mid", "decision": "mid"}}
CASE = AgentCase("F1", "p", "Fast", "fast-tier", ("TRANSFORM",),
                 {"kind": ["read", "command"], "target": "add_item"}, {"edits_include": ["a.py"]})
GOOD = [Event("say", "PATTERNS: TRANSFORM"), Event("read", "add_item src"), Event("changed", "a.py")]
NO_DECLARATION = [Event("read", "add_item src"), Event("changed", "a.py")]


def rec(version, events, i=1):
    return RunRecord("F1", version, "low", i, events, score_agent(events, CASE))


def test_report_lists_each_check_branch_over_main():
    records = [rec("branch", GOOD, i) for i in (1, 2, 3)] + [rec("main", NO_DECLARATION, i) for i in (1, 2, 3)]
    text = render([CaseResult(CASE, records, "low", only_tier="low")], LADDERS, "rt")
    assert "## Checks (branch / main)" in text
    assert "| F1 | low | 3/3 / 0/3 | 3/3 / 0/3 | 3/3 / 3/3 | 3/3 / 3/3 |" in text


def test_a_failed_run_names_the_failed_check_in_the_report():
    records = [rec("branch", NO_DECLARATION, i) for i in (1, 2, 3)]
    text = render([CaseResult(CASE, records, None, only_tier="low")], LADDERS, "rt")
    assert "check 1 (PATTERNS line before the first call)" in text


def test_main_failures_list_a_reason_but_no_event_dump_and_branch_failures_keep_theirs():
    records = [rec("branch", NO_DECLARATION), rec("main", NO_DECLARATION)]
    text = render([CaseResult(CASE, records, None, only_tier="low")], LADDERS, "rt")
    failed = text.split("## Failed and void runs")[1]
    assert "F1** branch low #1" in failed and "F1** main low #1" in failed
    assert failed.count("events:") == 1  # the branch run's only


def test_skill_reports_have_no_checks_section():
    from harness.core.cases import Case
    from harness.core.score import Verdict
    skill_case = Case("c1", "p", "Fast", "none", "advisor-mode", "todo-app")
    record = RunRecord("c1", "branch", "low", 1, [Event("handoff", "Fast")], Verdict("PASS", "ok"))
    text = render([CaseResult(skill_case, [record], "low", only_tier="low")], LADDERS, "rt")
    assert "## Checks" not in text


def test_runs_jsonl_carries_checks_only_for_agent_runs():
    assert rec("branch", GOOD).to_dict()["checks"] == {"1": True, "2": True, "3": True, "4": True}
    from harness.core.score import Verdict
    plain = RunRecord("c1", "branch", "low", 1, [], Verdict("PASS", "ok"))
    assert "checks" not in json.loads(json.dumps(plain.to_dict()))
