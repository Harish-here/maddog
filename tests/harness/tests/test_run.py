import subprocess

import pytest
import run
from harness.core.cases import TESTS_DIR, Case


def test_main_worktree_is_removed_when_a_case_crashes(monkeypatch):
    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: object())

    def crash(*args, **kwargs):
        raise RuntimeError("adapter died")

    monkeypatch.setattr(run, "run_case", crash)
    with pytest.raises(RuntimeError, match="adapter died"):
        run.main(["skills/advisor-mode", "--runtime", "rt", "--case", "list-flags"])
    listing = subprocess.run(["git", "-C", str(TESTS_DIR.parent), "worktree", "list"],
                             capture_output=True, text=True).stdout
    assert "maddog-baseline-" not in listing


def test_select_cases_filters_by_id_preserving_order():
    cases = [
        Case("c1", "p1", "Fast", "none", "skill", "fixture"),
        Case("c2", "p2", "Fast", "user", "skill", "fixture"),
        Case("c3", "p3", "Fast", "decision", "skill", "fixture"),
    ]
    result = run.select_cases(cases, ["c3", "c1"], None)
    assert [c.id for c in result] == ["c1", "c3"]


def test_select_cases_filters_by_pressure():
    cases = [
        Case("c1", "p1", "Fast", "none", "skill", "fixture"),
        Case("c2", "p2", "Fast", "user", "skill", "fixture"),
        Case("c3", "p3", "Fast", "decision", "skill", "fixture"),
    ]
    result = run.select_cases(cases, None, "decision")
    assert [c.id for c in result] == ["c3"]


def test_select_cases_combines_id_and_pressure():
    cases = [
        Case("c1", "p1", "Fast", "none", "skill", "fixture"),
        Case("c2", "p2", "Fast", "user", "skill", "fixture"),
        Case("c3", "p3", "Fast", "decision", "skill", "fixture"),
        Case("c4", "p4", "Fast", "decision", "skill", "fixture"),
    ]
    result = run.select_cases(cases, ["c1", "c3", "c4"], "decision")
    assert [c.id for c in result] == ["c3", "c4"]


def test_select_cases_raises_on_unknown_id():
    cases = [
        Case("c1", "p1", "Fast", "none", "skill", "fixture"),
    ]
    with pytest.raises(ValueError, match="unknown case ids: c2, c3"):
        run.select_cases(cases, ["c2", "c3"], None)
