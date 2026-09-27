import pytest
from harness.core.cases import (
    TESTS_DIR, load_cases, load_ladders, expected_tier, ROLES, TIERS,
)

ADVISOR = TESTS_DIR / "skills" / "advisor-mode" / "handoff.yaml"


def test_advisor_cases_load_with_one_per_role():
    cases = load_cases(ADVISOR)
    assert set(c.expect for c in cases) == set(ROLES)
    assert all(c.skill == "advisor-mode" and c.fixture == "todo-app" for c in cases)


def test_every_runtime_ladder_has_every_tier():
    ladders = load_ladders()
    runtimes = [key for key in ladders if key not in ("expected_tier", "max_tier")]
    assert runtimes
    for runtime in runtimes:
        assert set(ladders[runtime]) == set(TIERS)


def test_expected_tier_follows_pressure(tmp_path):
    # The real handoff.yaml now carries a file-level override (below), so
    # exercise the pressure fallback on a file that doesn't set one.
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    case = load_cases(p)[0]
    assert expected_tier(case, load_ladders()) == "low"


def test_advisor_file_level_tier_is_inherited_by_every_case():
    # tests/skills/advisor-mode/handoff.yaml sets expected_tier: mid at the
    # file level (O9); no case there sets its own, so all inherit it.
    ladders = load_ladders()
    cases = load_cases(ADVISOR)
    assert all(expected_tier(case, ladders) == "mid" for case in cases)


def test_user_pressure_maps_to_mid_tier(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: user}\n")
    case = load_cases(p)[0]
    assert expected_tier(case, load_ladders()) == "mid"


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


def test_file_level_expected_tier_is_inherited(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\nexpected_tier: mid\nwhy: file reason\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    case = load_cases(p)[0]
    assert case.expected_tier == "mid" and case.why == "file reason"
    assert expected_tier(case, load_ladders()) == "mid"


def test_case_level_expected_tier_overrides_the_file_level_one(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\nexpected_tier: mid\nwhy: file reason\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none, expected_tier: high, why: case reason}\n")
    case = load_cases(p)[0]
    assert case.expected_tier == "high" and case.why == "case reason"


def test_file_level_expected_tier_without_why_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\nexpected_tier: mid\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="why"):
        load_cases(p)


def test_file_level_why_without_expected_tier_is_rejected(tmp_path):
    p = write(tmp_path, "skill: x\nfixture: todo-app\nwhy: file reason\ncases:\n"
                        "  - {id: a, prompt: p, expect: Fast, pressure: none}\n")
    with pytest.raises(ValueError, match="expected_tier"):
        load_cases(p)
