import json
from harness.core.cases import Case
from harness.core.events import Event
from harness.core.score import Verdict
from harness.core.runner import CaseResult, RunRecord
from harness.core.report import render, write_results

LADDERS = {"rt": {"low": "l", "mid": "m", "high": "h"}, "expected_tier": {"none": "low", "user": "mid", "decision": "mid"}}


def rec(version, tier, result, i=1, reason="r"):
    return RunRecord("c1", version, tier, i, [Event("handoff", "Smart")], Verdict(result, reason))


def case_result(records, lowest, void_limited=False, only_tier=None):
    return CaseResult(Case("c1", "p", "Fast", "none", "advisor-mode", "todo-app"), records, lowest, void_limited, only_tier=only_tier)


def test_table_shows_branch_and_main_passes_per_tier():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)] + [rec("main", "low", "PASS", 1), rec("main", "low", "FAIL", 2), rec("main", "low", "PASS", 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt")
    assert "| c1 | Fast | low | 3/3 | 2/3 | low | low |" in text


def test_above_expected_is_flagged():
    recs = [rec("branch", "low", "FAIL", i) for i in (1, 2, 3)] + [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid")], LADDERS, "rt")
    assert "ABOVE EXPECTED" in text


def test_no_passing_tier_and_void_limit_are_flagged():
    assert "NO PASSING TIER" in render([case_result([rec("branch", "high", "FAIL")], None)], LADDERS, "rt")
    assert "VOID LIMIT" in render([case_result([rec("branch", "low", "VOID")], None, True)], LADDERS, "rt")


def test_only_tier_flag_when_no_pass():
    text = render([case_result([rec("branch", "mid", "FAIL")], None, only_tier="mid")], LADDERS, "rt")
    assert "NO PASS AT mid (only tier tried)" in text


def test_only_tier_no_flag_when_pass():
    recs = [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid", only_tier="mid")], LADDERS, "rt")
    assert "NO PASS AT" not in text and "VOID LIMIT" not in text and "NO PASSING TIER" not in text


def test_failed_runs_list_their_events():
    text = render([case_result([rec("branch", "low", "FAIL", reason="first handoff went to Smart")], None)], LADDERS, "rt")
    assert "first handoff went to Smart" in text and "handoff:Smart" in text


def test_write_results(tmp_path):
    write_results(tmp_path, [case_result([rec("branch", "low", "PASS")], "low")], "# report")
    lines = (tmp_path / "runs.jsonl").read_text().splitlines()
    assert json.loads(lines[0])["result"] == "PASS"
    assert (tmp_path / "report.md").read_text() == "# report"
