import json
from harness.core.agent_score import score_agent
from harness.core.cases import AgentCase, Case
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


def test_non_ladder_7_of_10_passes_not_flagged():
    # 7 passes: 7 * 2 = 14, not < 10, so not failed
    recs = [rec("branch", "low", "PASS", i) for i in range(1, 8)] + [rec("branch", "low", "FAIL", i) for i in range(8, 11)]
    text = render([case_result(recs, "low", only_tier="low")], LADDERS, "rt", ladder=False)
    assert "FAIL AT" not in text


def test_non_ladder_4_of_10_flagged():
    # 4 passes: 4 * 2 = 8 < 10, so failed
    recs = [rec("branch", "low", "PASS", i) for i in range(1, 5)] + [rec("branch", "low", "FAIL", i) for i in range(5, 11)]
    text = render([case_result(recs, None, only_tier="low")], LADDERS, "rt", ladder=False)
    assert "FAIL AT low" in text


def test_non_ladder_5_of_10_exactly_half_not_flagged():
    # 5 passes: 5 * 2 = 10, not < 10, so not failed (exactly half counts as pass)
    recs = [rec("branch", "low", "PASS", i) for i in range(1, 6)] + [rec("branch", "low", "FAIL", i) for i in range(6, 11)]
    text = render([case_result(recs, "low", only_tier="low")], LADDERS, "rt", ladder=False)
    assert "FAIL AT" not in text


def test_non_ladder_1_of_3_flagged():
    # 1 pass: 1 * 2 = 2 < 3, so failed
    recs = [rec("branch", "mid", "PASS", 1), rec("branch", "mid", "FAIL", 2), rec("branch", "mid", "FAIL", 3)]
    text = render([case_result(recs, None, only_tier="mid")], LADDERS, "rt", ladder=False)
    assert "FAIL AT mid" in text


def test_non_ladder_2_of_3_not_flagged():
    # 2 passes: 2 * 2 = 4 not < 3, so not failed
    recs = [rec("branch", "mid", "PASS", i) for i in (1, 2)], [rec("branch", "mid", "FAIL", 3)]
    recs = [r for sublist in recs for r in (sublist if isinstance(sublist, list) else [sublist])]
    text = render([case_result(recs, "mid", only_tier="mid")], LADDERS, "rt", ladder=False)
    assert "FAIL AT" not in text


# --- agent mode: the checks section ---

AGENT_CASE = AgentCase("F1", "p", "Fast", "fast-tier", ("TRANSFORM",),
                 {"kind": ["read", "command"], "target": "add_item"}, {"edits_include": ["a.py"]})
AGENT_GOOD = [Event("say", "PATTERNS: TRANSFORM"), Event("read", "add_item src"), Event("changed", "a.py")]
AGENT_NO_DECLARATION = [Event("read", "add_item src"), Event("changed", "a.py")]


def agent_rec(version, events, i=1):
    return RunRecord("F1", version, "low", i, events, score_agent(events, AGENT_CASE))


def test_report_lists_each_check_branch_over_main():
    records = [agent_rec("branch", AGENT_GOOD, i) for i in (1, 2, 3)] + [agent_rec("main", AGENT_NO_DECLARATION, i) for i in (1, 2, 3)]
    text = render([CaseResult(AGENT_CASE, records, "low", only_tier="low")], LADDERS, "rt")
    assert "## Checks (branch / main)" in text
    assert "| F1 | low | 3/3 / 0/3 | 3/3 / 0/3 | 3/3 / 3/3 | 3/3 / 3/3 |" in text


def test_a_failed_run_names_the_failed_check_in_the_report():
    records = [agent_rec("branch", AGENT_NO_DECLARATION, i) for i in (1, 2, 3)]
    text = render([CaseResult(AGENT_CASE, records, None, only_tier="low")], LADDERS, "rt")
    assert "check 1 (PATTERNS line before the first call)" in text


def test_main_failures_list_a_reason_but_no_event_dump_and_branch_failures_keep_theirs():
    records = [agent_rec("branch", AGENT_NO_DECLARATION), agent_rec("main", AGENT_NO_DECLARATION)]
    text = render([CaseResult(AGENT_CASE, records, None, only_tier="low")], LADDERS, "rt")
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
    assert agent_rec("branch", AGENT_GOOD).to_dict()["checks"] == {"1": True, "2": True, "3": True, "4": True}
    from harness.core.score import Verdict
    plain = RunRecord("c1", "branch", "low", 1, [], Verdict("PASS", "ok"))
    assert "checks" not in json.loads(json.dumps(plain.to_dict()))
