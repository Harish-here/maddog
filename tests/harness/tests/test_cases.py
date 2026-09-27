import pytest
from harness.core.cases import (
    TESTS_DIR, load_cases, load_ladders, expected_tier, ROLES, TIERS,
)

ADVISOR = TESTS_DIR / "skills" / "advisor-mode" / "handoff.yaml"


def test_advisor_cases_load_with_one_per_role():
    cases = load_cases(ADVISOR)
    assert [c.expect for c in cases] == list(ROLES)
    assert all(c.skill == "advisor-mode" and c.fixture == "todo-app" for c in cases)


def test_every_runtime_ladder_has_every_tier():
    ladders = load_ladders()
    runtimes = [key for key in ladders if key != "expected_tier"]
    assert runtimes
    for runtime in runtimes:
        assert set(ladders[runtime]) == set(TIERS)


def test_expected_tier_follows_pressure():
    ladders = load_ladders()
    case = load_cases(ADVISOR)[0]
    assert expected_tier(case, ladders) == "low"


def write(tmp_path, body):
    p = tmp_path / "handoff.yaml"
    p.write_text(body)
    return p


def test_unknown_role_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Wizard, pressure: none}\n")
    with pytest.raises(ValueError, match="Wizard"):
        load_cases(p)


def test_unknown_pressure_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: medium}\n")
    with pytest.raises(ValueError, match="medium"):
        load_cases(p)


def test_duplicate_id_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none}\n"
                        "  - {id: a, prompt: q, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_cases(p)


def test_missing_field_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="prompt"):
        load_cases(p)


def test_case_can_raise_its_expected_tier_with_a_reason(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none, expected_tier: mid, why: needs two steps}\n")
    case = load_cases(p)[0]
    assert expected_tier(case, load_ladders()) == "mid"
    bad = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n"
                          "  - {id: a, prompt: p, expect: Fast, pressure: none, expected_tier: mid}\n")
    with pytest.raises(ValueError, match="why"):
        load_cases(bad)


def test_no_skill_means_plain_session(tmp_path):
    p = write(tmp_path, "fixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    assert load_cases(p)[0].skill is None
