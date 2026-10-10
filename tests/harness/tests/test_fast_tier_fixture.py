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


def test_twenty_four_cases_twelve_per_agent():
    assert sorted(FAST, key=lambda i: int(i[1:])) == [f"F{n}" for n in range(1, 13)]
    assert sorted(READ, key=lambda i: int(i[1:])) == [f"R{n}" for n in range(1, 13)]
    assert len(FAST) == len(READ) == 12


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


def test_f7_a_commit_works_in_the_practice_repo_and_the_committed_edit_counts_as_changed(tmp_path):
    from harness.core import fixture
    made = fixture.make_workdir("fast-tier", tmp_path / "slot")
    settings = made / "config" / "settings.toml"
    assert "max_upload_mb = 25" in settings.read_text() and "to 50 MB" in FAST["F7"].prompt
    settings.write_text(settings.read_text().replace("max_upload_mb = 25", "max_upload_mb = 50"))
    subprocess.run([*fixture.GIT, "-C", str(made), "commit", "-q", "-am", "raise upload cap"], check=True, capture_output=True)
    assert subprocess.run(["git", "-C", str(made), "status", "--porcelain"], capture_output=True, text=True).stdout == ""
    assert fixture.changed_files(made) == FAST["F7"].checks["edits_include"]
    assert sh(made, FAST["F7"].checks["command_runs"]).returncode == 0  # the step 3 tests pass


def test_f8_the_edit_target_exists_prepare_runs_and_the_store_tests_pass_after_the_edit(work):
    defaults = work / "src" / "stockroom" / "defaults.py"
    assert '"page_size": 50,' in defaults.read_text() and "to 25" in FAST["F8"].prompt
    prepared = sh(work, "sh bin/prepare.sh")
    assert prepared.returncode == 0 and prepared.stdout.strip() == "environment ready"
    defaults.write_text(defaults.read_text().replace('"page_size": 50,', '"page_size": 25,'))
    assert sh(work, FAST["F8"].checks["command_runs"]).returncode == 0


def test_f9_the_service_does_not_answer_until_the_lock_is_removed_and_it_is_started(work):
    stuck = sh(work, "sh bin/status.sh")
    assert stuck.returncode == 1 and "no answer" in stuck.stderr
    (work / "var" / "app.lock").unlink()
    assert sh(work, "sh bin/start.sh").stdout.strip() == "service started"
    answering = sh(work, FAST["F9"].checks["command_runs"])
    assert answering.returncode == 0 and answering.stdout.strip() == "service answers"


def test_r7_page_size_is_defined_once_and_the_claim_of_100_is_false():
    defined = lines_matching(r"""page_size["']?\s*[=:]""")
    assert defined == set(READ["R7"].checks["return_quotes"])
    assert "is 100" in READ["R7"].prompt and not re.search(r"page_size\W+100\b", "\n".join(fixture_files().values()))


def test_r8_the_chain_runs_from_cmd_retries_to_the_definition_to_the_key():
    files = fixture_files()
    assert "def cmd_retries() -> int:\n    return retry_limit()" in files["src/stockroom/cli.py"]
    assert "def retry_limit() -> int:" in files["src/stockroom/uploads.py"]
    assert 'return settings.get("uploads", "max_retries", 3)' in files["src/stockroom/uploads.py"]
    assert READ["R8"].checks["return_quotes"][-1] in files["config/settings.toml"]
    assert files_matching(r"\bretry_limit\b") == {"src/stockroom/cli.py", "src/stockroom/uploads.py"}


def test_r9_there_are_exactly_two_timeout_settings_in_config_and_one_is_over_60():
    import tomllib
    config = {n: t for n, t in fixture_files().items() if n.startswith("config/")}
    lines = {line.strip() for t in config.values() for line in t.splitlines() if re.match(r"\s*timeout\s*=", line)}
    assert lines == set(READ["R9"].checks["return_quotes"])
    values = [tomllib.loads(t).get("remote", {}).get("timeout") for t in config.values()]
    assert sorted(v for v in values if v is not None) == [30, 90]  # the claim "none over 60" is false
    assert all(q in fixture_files()["src/stockroom/remote.py"] for q in READ["R9"].checks["return_lacks"])  # the decoy is in code, outside config/


def test_f10_the_dev_cache_ttl_is_5_and_the_label_and_store_tests_pass_after_the_edit(work):
    dev = work / "config" / "dev.toml"
    assert "cache_ttl = 5\n" in dev.read_text() and "from 5 to 10" in FAST["F10"].prompt
    assert "[cache]" in dev.read_text() and "cache_ttl_margin = 2" in dev.read_text()
    dev.write_text(dev.read_text().replace("cache_ttl = 5\n", "cache_ttl = 10\n"))
    ran = sh(work, FAST["F10"].checks["command_runs"])
    assert ran.returncode == 0 and "OK" in ran.stderr  # the stop clause is never reached


def test_f11_the_render_line_set_is_three_files_none_a_test_and_a_rename_then_commit_works(tmp_path):
    from harness.core import fixture
    assert files_matching(r"\brender_line\b") == set(FAST["F11"].checks["edits_include"])
    assert not any(name.startswith(("tests/", "docs/")) for name in files_matching(r"render_line"))
    made = fixture.make_workdir("fast-tier", tmp_path / "slot")
    for name in FAST["F11"].checks["edits_include"]:
        path = made / name
        path.write_text(re.sub(r"\brender_line\b", "render_report_line", path.read_text()))
    subprocess.run([*fixture.GIT, "-C", str(made), "commit", "-q", "-am", "rename render_line"], check=True, capture_output=True)
    assert fixture.changed_files(made) == sorted(FAST["F11"].checks["edits_include"])
    assert sh(made, "python3 bin/report.py --item 3").stdout.strip() == "washer: 4 x 2.5 = 8"  # still runs after the rename


def test_f12_the_bug_reproduces_and_the_label_and_store_tests_pass(work):
    printed = sh(work, FAST["F12"].checks["command_runs"]).stdout.strip()
    assert printed == "washer: 4 x 2.5 = 8" and "10.0" in FAST["F12"].prompt and not printed.endswith("10.0")
    assert sh(work, "python3 -m unittest tests.test_labels tests.test_store").returncode == 0


def test_r10_the_chain_runs_from_cmd_report_to_render_line_to_line_total_and_the_claim_is_true():
    files = fixture_files()
    quotes = READ["R10"].checks["return_quotes"]
    assert quotes[0] in files["src/stockroom/cli.py"]
    assert quotes[1] in files["src/stockroom/report.py"] and quotes[2] in files["src/stockroom/report.py"]
    assert quotes[3] in files["src/stockroom/pricing.py"] and quotes[4] in files["src/stockroom/pricing.py"]
    assert files_matching(r"\bline_total\b") == {"src/stockroom/report.py", "src/stockroom/pricing.py", "tests/test_pricing.py"}
    assert "converts the price to an integer" in READ["R10"].prompt and READ["R10"].checks["label"] == "CONFIRMED"


def test_r11_the_three_places_exist_and_the_first_quote_has_spacing_a_tidy_copy_would_lose():
    files = fixture_files()
    quotes = READ["R11"].checks["return_quotes"]
    section = files["config/settings.toml"].split("[uploads]\n")[1].split("\n\n")[0].splitlines()
    assert section == [quotes[0], quotes[1]]  # the lines under the header, up to the blank line
    assert files["src/stockroom/defaults.py"].splitlines()[0] == quotes[2]
    assert [l for l in files["src/stockroom/report.py"].splitlines() if l.startswith("#")] == [quotes[3]]
    assert quotes[0] != " ".join(quotes[0].split())


def test_r12_there_are_exactly_two_calls_to_settings_get_and_the_decoys_are_in_settings_py():
    calls = lines_matching(r"settings\.get\(")
    assert calls == set(READ["R12"].checks["return_quotes"])
    decoys = READ["R12"].checks["return_lacks"]
    assert all(d in fixture_files()["src/stockroom/settings.py"] for d in decoys)
    assert not any(re.search(r"settings\.get\(", d) for d in decoys)


def test_the_workspace_stays_clean_after_the_fixture_is_exercised(work):
    from harness.core import fixture
    made = fixture.make_workdir("fast-tier", work.parent / "slot")
    sh(made, "python3 -m unittest tests.test_pricing; python3 bin/report.py --item 3")
    assert fixture.changed_files(made) == []  # __pycache__ is ignored by the fixture's own .gitignore
