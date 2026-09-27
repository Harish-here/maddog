import json
from harness.core.cases import Case
from harness.core.events import Event
from harness.core.score import Verdict
from harness.core.runner import CaseResult, RunRecord
from harness.core.report import render, write_results

LADDERS = {"rt": {"low": "l", "mid": "m", "high": "h"}, "expected_tier": {"none": "low", "user": "mid", "decision": "mid"}}


def rec(version, tier, result, i=1, reason="r", cost_usd=None, cached=False):
    return RunRecord("c1", version, tier, i, [Event("handoff", "Smart")], Verdict(result, reason), cost_usd=cost_usd, cached=cached)


def case_result(records, lowest, void_limited=False, only_tier=None):
    return CaseResult(Case("c1", "p", "Fast", "none", "advisor-mode", "todo-app"), records, lowest, void_limited, only_tier=only_tier)


def test_ladder_table_shows_branch_and_main_passes_per_tier():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)] + [rec("main", "low", "PASS", 1), rec("main", "low", "FAIL", 2), rec("main", "low", "PASS", 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "| c1 | Fast | low | 3/3 | 2/3 | n/a / n/a | low | low |" in text


def test_above_expected_is_flagged_only_in_ladder_mode():
    recs = [rec("branch", "low", "FAIL", i) for i in (1, 2, 3)] + [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid")], LADDERS, "rt", ladder=True)
    assert "ABOVE EXPECTED" in text


def test_no_passing_tier_and_void_limit_are_flagged_in_ladder_mode():
    assert "NO PASSING TIER" in render([case_result([rec("branch", "high", "FAIL")], None)], LADDERS, "rt", ladder=True)
    assert "VOID LIMIT" in render([case_result([rec("branch", "low", "VOID")], None, True)], LADDERS, "rt", ladder=True)


def test_non_ladder_repeated_failure_is_flagged_fail_at_tier():
    recs = [rec("branch", "mid", "FAIL", i) for i in (1, 2, 3)]
    text = render([case_result(recs, None, only_tier="mid")], LADDERS, "rt", ladder=False)
    assert "FAIL AT mid" in text


def test_non_ladder_pass_has_no_flag():
    recs = [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid", only_tier="mid")], LADDERS, "rt", ladder=False)
    assert "FAIL AT" not in text and "VOID LIMIT" not in text and "NO PASSING TIER" not in text


def test_non_ladder_table_has_no_lowest_or_expected_tier_columns():
    recs = [rec("branch", "mid", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "mid", only_tier="mid")], LADDERS, "rt", ladder=False)
    assert "Lowest passing tier" not in text
    assert "| Case | Expected role | Tier | Branch | Main | Cost | Flag |" in text


def test_ladder_table_has_lowest_and_expected_tier_columns():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "Lowest passing tier" in text and "Expected tier" in text


def test_failed_runs_list_their_events():
    text = render([case_result([rec("branch", "low", "FAIL", reason="first handoff went to Smart")], None)], LADDERS, "rt")
    assert "first handoff went to Smart" in text and "handoff:Smart" in text


def test_write_results(tmp_path):
    write_results(tmp_path, [case_result([rec("branch", "low", "PASS")], "low")], "# report")
    lines = (tmp_path / "runs.jsonl").read_text().splitlines()
    row = json.loads(lines[0])
    assert row["result"] == "PASS"
    assert row["cost_usd"] is None and row["cached"] is False
    assert (tmp_path / "report.md").read_text() == "# report"


def test_cost_column_reports_a_value_when_present():
    recs = [rec("branch", "low", "PASS", 1, cost_usd=0.01), rec("branch", "low", "PASS", 2, cost_usd=0.02),
            rec("branch", "low", "PASS", 3, cost_usd=0.005)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "$0.0350 / n/a" in text


def test_cost_column_is_null_not_zero_when_unavailable():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)]  # no cost_usd
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "n/a / n/a" in text
    assert "$0.0000" not in text


def test_total_cost_line_sums_every_row():
    recs = [rec("branch", "low", "PASS", 1, cost_usd=0.01)] + [rec("main", "low", "PASS", 1, cost_usd=0.02)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "**Total cost:** $0.0300" in text


def test_total_cost_line_is_na_when_nothing_recorded_a_cost():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "**Total cost:** n/a" in text


def test_cached_main_row_is_marked():
    recs = [rec("branch", "low", "PASS", i) for i in (1, 2, 3)] + [rec("main", "low", "PASS", i, cached=True) for i in (1, 2, 3)]
    text = render([case_result(recs, "low")], LADDERS, "rt", ladder=True)
    assert "3/3 (cached)" in text
