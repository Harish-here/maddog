"""Every case's known answer is true in the fast-tier fixture. No model.

The case files (tests/agents/*/patterns.yaml) hold the answers; this file
reads them and checks the fixture against them, then runs the fixture's own
commands in a throwaway copy."""
import re
import shutil
import subprocess

import pytest
from harness.core.cases import TESTS_DIR, load_agent_cases

FIXTURE = TESTS_DIR / "fixtures" / "fast-tier"
FAST = {c.id: c for c in load_agent_cases(TESTS_DIR / "agents" / "executor-fast" / "patterns.yaml")}
READ = {c.id: c for c in load_agent_cases(TESTS_DIR / "agents" / "executor-fast-read" / "patterns.yaml")}
ALL = {**FAST, **READ}


def fixture_files() -> dict[str, str]:
    return {p.relative_to(FIXTURE).as_posix(): p.read_text() for p in sorted(FIXTURE.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


def files_matching(pattern: str) -> set[str]:
    return {name for name, text in fixture_files().items() if re.search(pattern, text)}


def lines_matching(pattern: str) -> set[str]:
    return {line.strip() for text in fixture_files().values() for line in text.splitlines() if re.search(pattern, line)}


@pytest.fixture
def work(tmp_path):
    target = tmp_path / "work"
    shutil.copytree(FIXTURE, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def sh(work, command):
    return subprocess.run(command, shell=True, cwd=work, capture_output=True, text=True, timeout=30)


def test_twelve_cases_six_per_agent():
    assert sorted(FAST) == ["F1", "F2", "F3", "F4", "F5", "F6"]
    assert sorted(READ) == ["R1", "R2", "R3", "R4", "R5", "R6"]


def test_every_expected_pattern_is_a_real_row_of_that_agents_table():
    for agent, cases in (("executor-fast", FAST), ("executor-fast-read", READ)):
        table = (TESTS_DIR.parent / "agents" / f"{agent}.md").read_text()
        for case in cases.values():
            for name in case.patterns:
                assert re.search(rf"^\| {name} \|", table, re.MULTILINE), f"{case.id}: {name} is not in {agent}'s table"


def test_every_quoted_line_and_edit_path_is_in_the_fixture():
    text = "\n".join(fixture_files().values())
    names = set(fixture_files())
    for case in ALL.values():
        for quote in case.checks.get("return_quotes", []) + case.checks.get("return_lacks", []):
            assert quote in text, f"{case.id}: not in the fixture: {quote}"
        for path in case.checks.get("edits_include", []) + case.checks.get("edits_exclude", []):
            if path != "var/crash.log":  # F6 creates it
                assert path in names, f"{case.id}: no such file: {path}"


def test_f1_the_rename_set_is_five_files_and_the_decoy_is_a_sixth_that_must_stay():
    assert files_matching(r"\badd_item\b") == set(FAST["F1"].checks["edits_include"])
    assert "add_items_bulk" in fixture_files()["src/stockroom/bulk.py"]
    assert not re.search(r"\badd_item\b", fixture_files()["src/stockroom/bulk.py"])
    assert "src/stockroom/bulk.py" in FAST["F1"].checks["edits_exclude"]


def test_f5_the_rename_set_is_three_files_and_no_test_names_it():
    assert files_matching(r"\bfmt_price\b") == set(FAST["F5"].checks["edits_include"])
    assert not any(name.startswith("tests/") for name in files_matching(r"fmt_price"))


def test_f2_and_f6_the_lock_blocks_start_until_it_is_removed(work):
    assert (work / "var" / "app.lock").exists() and (work / "var" / "service.log").exists()
    blocked = sh(work, "sh bin/start.sh")
    assert blocked.returncode == 1 and "locked" in blocked.stderr
    (work / "var" / "app.lock").unlink()
    started = sh(work, "sh bin/start.sh")
    assert started.returncode == 0 and started.stdout.strip() == "service started"


def test_f3_exactly_one_pricing_test_fails_and_the_other_modules_pass(work):
    failing = sh(work, FAST["F3"].checks["command_runs"])
    assert failing.returncode == 1 and "FAILED (failures=1)" in failing.stderr
    assert "test_fractional_price" in failing.stderr
    assert sh(work, "python3 -m unittest tests.test_labels tests.test_store").returncode == 0


def test_f4_the_bug_reproduces(work):
    out = sh(work, FAST["F4"].checks["command_runs"])
    assert out.returncode == 0 and out.stdout.strip() == "washer: 4 x 2.5 = 8"


def test_r1_there_are_exactly_three_calls_to_parse_money():
    calls = {line for line in lines_matching(r"parse_money\(") if not line.startswith("def ")}
    assert calls == set(READ["R1"].checks["return_quotes"])


def test_r2_and_r6_the_chain_runs_from_the_call_to_the_definition_to_the_key():
    files = fixture_files()
    assert 'return fetch_stock("warehouse-1")' in files["src/stockroom/cli.py"]
    assert "def fetch_stock(warehouse: str) -> list[dict]:" in files["src/stockroom/remote.py"]
    assert 'timeout = settings.get("remote", "timeout", 15)' in files["src/stockroom/remote.py"]
    assert "timeout = 30" in files["config/settings.toml"]
    assert "default for that key is 10" in READ["R6"].prompt  # the code says 15, so the claim is false


def test_r3_the_retry_line_is_odd_enough_to_catch_a_tidied_quote():
    line = READ["R3"].checks["return_quotes"][0]
    assert line in fixture_files()["config/settings.toml"]
    assert line != " ".join(line.split())  # extra spaces: a model that normalizes them fails


def test_r4_the_claim_is_false():
    assert "max_upload_mb = 25" in fixture_files()["config/settings.toml"]
    assert "10 MB" in READ["R4"].prompt and "= 10" not in fixture_files()["config/settings.toml"]


def test_r5_there_are_exactly_three_definitions_of_cache_ttl():
    defined = lines_matching(r"""cache_ttl["']?\s*[=:]""")
    assert defined == set(READ["R5"].checks["return_quotes"])


def test_the_workspace_stays_clean_after_the_fixture_is_exercised(work):
    from harness.core import fixture
    made = fixture.make_workdir("fast-tier", work.parent / "slot")
    sh(made, "python3 -m unittest tests.test_pricing; python3 bin/report.py --item 3")
    assert fixture.changed_files(made) == []  # __pycache__ is ignored by the fixture's own .gitignore
