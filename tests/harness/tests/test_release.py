"""Release gate: selection (R0), recording (R1) and the offline gate check (R2).
No model runs: run.py's file runner is replaced by fake run records, and every
repo is a throwaway git repo."""
import json
import subprocess
from pathlib import Path

import pytest
import run
from harness.core.cases import Case, load_agent_cases, load_cases, load_ladders
from harness.core.changed import select_for_base, selecting_files
from harness.core.release import (case_verdict, check_gate, dirty_covered, entry_for, file_verdict, fingerprint_paths,
                                  plugin_version, slug_of)
from harness.core.runner import CaseResult, RunRecord
from harness.core.score import Verdict
from harness.tests.test_cases import AGENT_FILE

SKILL_COVERS = '["skills/s1/**", "agents/a.md"]'
SKILL_FILE = ("covers: " + SKILL_COVERS + "\nskill: s1\nfixture: todo-app\ncases:\n"
              "  - {id: a, prompt: p, expect: Fast, pressure: none}\n"
              "  - {id: b, prompt: p, expect: Smart, pressure: none}\n")
AGENT_COVERS = '["scripts/g.sh"]'


def write(root, name, body):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout


def commit(repo, message="c"):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path):
    """main holds version 1.0.0; the checkout is on branch `feat` with nothing changed yet."""
    git(tmp_path, "init", "-q", "-b", "main")
    write(tmp_path, ".claude-plugin/plugin.json", json.dumps({"version": "1.0.0"}))
    write(tmp_path, "agents/a.md", "v1")
    write(tmp_path, "skills/s1/SKILL.md", "v1")
    write(tmp_path, "scripts/g.sh", "echo g")
    write(tmp_path, "README.md", "r")
    write(tmp_path, "tests/skills/s1/handoff.yaml", SKILL_FILE)
    write(tmp_path, "tests/agents/a1/patterns.yaml", f"covers: {AGENT_COVERS}\n" + AGENT_FILE)
    commit(tmp_path, "base")
    git(tmp_path, "checkout", "-q", "-b", "feat")
    return tmp_path


def names(selection):
    return [t.path for t in selection.selected]


def select(repo, base="main"):
    from harness.core.changed import changed_files
    return select_for_base(repo, base, changed_files(repo, base))


# --- R0: selection ---

def test_selecting_files_drops_tests_and_claude_folders_only():
    files = ["tests/run.py", "tests/releases/1.0.0/manifest.json", ".claude/plans/x.md", ".claude-plugin/plugin.json",
             "agents/a.md", "testsuite.md"]
    assert selecting_files(files) == [".claude-plugin/plugin.json", "agents/a.md", "testsuite.md"]


def test_a_changed_covered_file_selects_skill_before_agent_tests(repo):
    write(repo, "agents/a.md", "v2"), write(repo, "scripts/g.sh", "echo h")
    commit(repo)
    assert names(select(repo)) == ["tests/skills/s1/handoff.yaml", "tests/agents/a1/patterns.yaml"]


def test_tests_only_changes_select_nothing(repo):
    write(repo, "tests/run.py", "x"), write(repo, "tests/skills/s1/handoff.yaml", SKILL_FILE + "# edit\n")
    commit(repo)
    assert names(select(repo)) == []


def test_claude_folder_changes_select_nothing_even_when_covered(repo):
    write(repo, "tests/skills/s1/handoff.yaml", SKILL_FILE.replace(SKILL_COVERS, '["**"]'))
    commit(repo, "widen covers on base")
    git(repo, "branch", "-f", "main"), git(repo, "checkout", "-q", "main"), git(repo, "checkout", "-q", "-B", "feat")
    write(repo, ".claude/plans/p.md", "x")
    commit(repo)
    assert names(select(repo)) == []


def test_releases_folder_never_selects(repo):
    write(repo, "tests/skills/s1/handoff.yaml", SKILL_FILE.replace(SKILL_COVERS, '["**"]'))
    commit(repo)
    git(repo, "branch", "-f", "main"), git(repo, "checkout", "-q", "main"), git(repo, "checkout", "-q", "-B", "feat")
    write(repo, "tests/releases/1.0.1/manifest.json", "{}")
    commit(repo)
    assert names(select(repo)) == []


def test_covers_are_the_union_of_base_and_head(repo):
    # head narrows covers away from agents/a.md and widens them to README.md
    write(repo, "tests/skills/s1/handoff.yaml", SKILL_FILE.replace(SKILL_COVERS, '["skills/s1/**", "README.md"]'))
    write(repo, "agents/a.md", "v2")
    commit(repo)
    assert names(select(repo)) == ["tests/skills/s1/handoff.yaml"]  # base covers still match the changed agent
    write(repo, "README.md", "r2")
    commit(repo)
    (test,) = select(repo).selected
    assert test.covers == ("skills/s1/**", "agents/a.md", "README.md")
    assert test.base_covers == ("skills/s1/**", "agents/a.md") and test.head_covers == ("skills/s1/**", "README.md")


def test_a_new_test_file_selects_by_its_head_covers(repo):
    write(repo, "tests/skills/s2/handoff.yaml", SKILL_FILE.replace("s1", "s2"))
    write(repo, "skills/s2/SKILL.md", "x")
    commit(repo)
    (test,) = select(repo).selected
    assert (test.path, test.base_covers, test.in_head) == ("tests/skills/s2/handoff.yaml", (), True)


def test_a_selected_test_file_deleted_on_head_is_reported(repo):
    write(repo, "agents/a.md", "v2")
    (repo / "tests/skills/s1/handoff.yaml").unlink()
    commit(repo)
    selection = select(repo)
    assert selection.deleted == ["tests/skills/s1/handoff.yaml"]
    assert names(selection) == ["tests/skills/s1/handoff.yaml"]


def test_an_unselected_deleted_test_file_is_not_reported(repo):
    write(repo, "README.md", "r2")
    (repo / "tests/skills/s1/handoff.yaml").unlink()
    commit(repo)
    assert select(repo).deleted == []


def test_an_unknown_base_raises(repo):
    with pytest.raises(ValueError):
        select_for_base(repo, "nope", [])


# --- D1: the case verdict ---

CASE = Case("c1", "p", "Fast", "none", "s1", "todo-app")


def fake_case_result(branch_pass, branch_fail, main_pass, main_fail, voids=0, void_limited=False, tier="low", case=CASE):
    records = []
    for version, p, f in (("branch", branch_pass, branch_fail), ("main", main_pass, main_fail)):
        verdicts = ["PASS"] * p + ["FAIL"] * f + ["VOID"] * voids
        records += [RunRecord(case.id, version, tier, i, [], Verdict(v, "r")) for i, v in enumerate(verdicts, 1)]
    return CaseResult(case, records, void_limited=void_limited, only_tier=tier)


@pytest.mark.parametrize("bp, bf, mp, mf, expected", [
    (3, 0, 3, 0, "pass"),
    (3, 0, 0, 3, "pass"),
    (2, 1, 2, 1, "pass"),
    (2, 1, 1, 2, "pass"),
    (2, 1, 3, 0, "pass"),      # one run below main: the allowed gap
    (1, 2, 2, 1, "pass"),      # 1 of 3 is fine: no per-case 2-of-3 floor
    (1, 2, 0, 3, "pass"),
    (1, 2, 3, 0, "fail"),      # two runs below main
    (0, 3, 1, 2, "fail"),      # a case at zero fails, even one run below main
    (0, 3, 0, 3, "fail"),      # ...and even when main is also at zero
])
def test_agent_case_verdict_is_within_one_of_main_and_never_zero(bp, bf, mp, mf, expected):
    got = case_verdict(fake_case_result(bp, bf, mp, mf), 3, agent_mode=True)
    assert got["verdict"] == expected
    assert (got["branch_pass"], got["main_pass"]) == (bp, mp)
    assert got["valid_runs"] == {"branch": bp + bf, "main": mp + mf}


@pytest.mark.parametrize("bp, bf, mp, mf, expected", [
    (0, 3, 0, 3, "pass"),   # skill 0/3 vs 0/3
    (0, 3, 1, 2, "pass"),   # skill 0/3 vs 1/3: one run below main, no floor
    (1, 2, 2, 1, "pass"),   # skill 1/3 vs 2/3: one run below main
    (1, 2, 3, 0, "fail"),   # skill 1/3 vs 3/3: two runs below main
    (3, 0, 3, 0, "pass"),
])
def test_skill_case_verdict_is_within_one_of_main_with_no_floor(bp, bf, mp, mf, expected):
    assert case_verdict(fake_case_result(bp, bf, mp, mf), 3, agent_mode=False)["verdict"] == expected


# --- the file verdict ---

def case_entries(rows, agent_mode=True, runs=3):
    """rows: [(branch_pass, main_pass)] -> {case id: case_verdict dict}, one case per row."""
    out = {}
    for i, (bp, mp) in enumerate(rows):
        case = Case(f"c{i}", "p", "Fast", "none", "s1", "todo-app")
        out[case.id] = case_verdict(fake_case_result(bp, runs - bp, mp, runs - mp, case=case), runs, agent_mode=agent_mode)
    return out


def test_agent_file_at_29_of_36_passes():
    got = file_verdict(case_entries([(3, 3)] * 5 + [(2, 3)] * 7), agent_mode=True)
    assert (got["branch_pass"], got["branch_runs"], got["pass_rate"], got["verdict"]) == (29, 36, 0.806, "pass")


def test_agent_file_at_28_of_36_fails_on_the_rate_alone():
    entries = case_entries([(3, 3)] * 4 + [(2, 3)] * 8)
    assert all(c["verdict"] == "pass" for c in entries.values())
    got = file_verdict(entries, agent_mode=True)
    assert (got["branch_pass"], got["branch_runs"], got["pass_rate"], got["verdict"]) == (28, 36, 0.778, "fail")


def test_agent_file_with_a_case_at_zero_fails_at_92_percent():
    entries = case_entries([(0, 0)] + [(3, 3)] * 11)
    assert entries["c0"]["verdict"] == "fail"
    got = file_verdict(entries, agent_mode=True)
    assert got["pass_rate"] == 0.917 and got["verdict"] == "fail"


def test_agent_file_with_a_case_two_below_main_fails_at_97_percent():
    entries = case_entries([(1, 3)] + [(3, 3)] * 11)
    assert entries["c0"]["verdict"] == "fail"
    assert file_verdict(entries, agent_mode=True)["verdict"] == "fail"


def test_skill_file_keeps_the_per_case_rule_with_no_rate():
    entries = case_entries([(0, 0), (1, 2), (3, 3)], agent_mode=False)
    got = file_verdict(entries, agent_mode=False)
    assert (got["branch_pass"], got["branch_runs"], got["verdict"]) == (4, 9, "pass")  # 44% still passes
    entries["c1"]["verdict"] = "fail"
    assert file_verdict(entries, agent_mode=False)["verdict"] == "fail"


def test_entry_for_stores_the_file_verdict_and_pass_rate(repo):
    write(repo, "scripts/g.sh", "echo h")
    commit(repo)
    (test,) = select(repo).selected
    assert test.agent_mode
    cases = [Case(f"c{i}", "p", "Fast", "none", "s1", "todo-app") for i in range(12)]
    results = [fake_case_result(bp, 3 - bp, 3, 0, case=c) for c, bp in zip(cases, [3] * 5 + [2] * 7)]
    entry = entry_for(repo, test, results, 3, "tests/results/x")
    assert (entry["branch_pass"], entry["branch_runs"], entry["pass_rate"], entry["verdict"]) == (29, 36, 0.806, "pass")
    assert entry["cases"]["c11"]["branch_pass"] == 2 and entry["cases"]["c11"]["verdict"] == "pass"
    results[0] = fake_case_result(0, 3, 0, 3, case=cases[0])
    bad = entry_for(repo, test, results, 3, "tests/results/x")
    assert bad["cases"]["c0"]["verdict"] == "fail" and bad["verdict"] == "fail"


@pytest.mark.parametrize("agent", [True, False])
def test_fewer_valid_runs_than_asked_is_a_fail_on_either_side_in_both_modes(agent):
    assert case_verdict(fake_case_result(2, 0, 3, 0), 3, agent_mode=agent)["verdict"] == "fail"
    assert case_verdict(fake_case_result(3, 0, 2, 0), 3, agent_mode=agent)["verdict"] == "fail"


def test_void_runs_do_not_count_as_valid_and_void_limit_always_fails():
    ok = case_verdict(fake_case_result(3, 0, 3, 0, voids=2), 3, agent_mode=True)
    assert ok["verdict"] == "pass" and ok["valid_runs"] == {"branch": 3, "main": 3}
    limited = case_verdict(fake_case_result(3, 0, 3, 0, void_limited=True), 3, agent_mode=False)
    assert limited["verdict"] == "fail" and limited["void_limited"] is True


def test_a_result_with_no_expected_tier_fails():
    assert case_verdict(fake_case_result(3, 0, 3, 0, tier=None), 3, agent_mode=False)["verdict"] == "fail"


# --- fingerprints ---

def test_fingerprint_paths_are_tracked_covered_files_plus_the_case_file(repo):
    write(repo, "agents/a.md", "v2")
    commit(repo)
    write(repo, "skills/s1/untracked.md", "x")
    write(repo, "tests/releases/1.0.1/skills-s1.md", "x")
    (test,) = [t for t in select(repo).selected if t.path.endswith("s1/handoff.yaml")]
    assert fingerprint_paths(repo, test) == ["agents/a.md", "skills/s1/SKILL.md", "tests/skills/s1/handoff.yaml"]


def test_dirty_covered_sees_staged_and_unstaged_edits_to_covered_files_only(repo):
    write(repo, "agents/a.md", "v2")
    commit(repo)
    tests = select(repo).selected
    assert dirty_covered(repo, tests) == []
    write(repo, "agents/a.md", "v3"), write(repo, "README.md", "elsewhere")
    assert dirty_covered(repo, tests) == ["agents/a.md"]
    git(repo, "add", "agents/a.md")
    assert dirty_covered(repo, tests) == ["agents/a.md"]


def test_slug_of_names_the_test_folder():
    assert slug_of("tests/skills/advisor-mode/handoff.yaml") == "skills-advisor-mode"
    assert slug_of("tests/agents/executor-fast/patterns.yaml") == "agents-executor-fast"


# --- R1: --record, with fake run records ---

class Fake:
    """Replaces everything in run.py that touches a model, the network, or a long test run."""
    def __init__(self, monkeypatch, repo):
        self.passing = True
        self.file_runs = []
        self.offline = (0, "488 passed in 9.99s")
        self.synced = True
        monkeypatch.setattr(run, "REPO_ROOT", repo)
        monkeypatch.setattr(run, "sweep", lambda root: [])
        monkeypatch.setattr(run, "run_offline_tests", lambda root: self.offline)
        monkeypatch.setattr(run, "check_main_synced", self._synced)
        monkeypatch.setattr(run, "_run_file", self._run_file)

    def _synced(self, root):
        if not self.synced:
            raise ValueError("local main (aaaa) is not origin/main (bbbb); update main first")

    def _run_file(self, parser, args, path, agent_mode, collect=None):
        self.file_runs.append(Path(path).name)
        cases = load_agent_cases(path) if agent_mode else load_cases(path)
        results = []
        for case in cases:
            records = []
            for version in ("branch", "main"):
                n_pass = args.runs if (self.passing or version == "main") else 0
                verdicts = ["PASS"] * n_pass + ["FAIL"] * (args.runs - n_pass)
                records += [RunRecord(case.id, version, "low", i, [], Verdict(v, "r"), cost_usd=0.5)
                            for i, v in enumerate(verdicts, 1)]
            results.append(CaseResult(case, records, only_tier="low"))
        if collect is not None:
            collect.append({"results": results, "out_dir": Path(path).parents[3] / "tests" / "results" / "2026-10-10T120000"})
        return 0


def go(*extra):
    return run.main(["--changed", "--record", "--runtime", "claude-code", *extra])


def bump(repo, version="1.0.1", edit="v2"):
    write(repo, ".claude-plugin/plugin.json", json.dumps({"version": version}))
    write(repo, "agents/a.md", edit)
    commit(repo, "release")


def manifest_of(repo, version="1.0.1"):
    return json.loads((repo / "tests/releases" / version / "manifest.json").read_text())


@pytest.fixture
def fake(monkeypatch, repo):
    return Fake(monkeypatch, repo)


def test_record_writes_manifest_offline_line_and_one_table_per_test_file(fake, repo, capsys):
    bump(repo)
    assert go() == 0
    out = repo / "tests/releases/1.0.1"
    assert sorted(p.name for p in out.iterdir()) == ["manifest.json", "offline.txt", "skills-s1.md"]
    assert (out / "offline.txt").read_text() == "488 passed in 9.99s\n"
    m = manifest_of(repo)
    assert m["version"] == "1.0.1" and m["attempt"] == 1 and m["offline"] == "488 passed in 9.99s"
    assert m["tested_commit"] == git(repo, "rev-parse", "HEAD").strip()
    assert m["base_commit"] == git(repo, "rev-parse", "main").strip()
    assert m["changed_files"] == [".claude-plugin/plugin.json", "agents/a.md"]
    assert m["total_cost_usd"] == 6.0 and m["time"].endswith("+00:00")
    (entry,) = m["tests"]
    assert (entry["path"], entry["mode"], entry["verdict"]) == ("tests/skills/s1/handoff.yaml", "skill", "pass")
    assert entry["results"] == "tests/results/2026-10-10T120000"
    assert entry["cases"]["a"] == {"tier": "low", "branch_pass": 3, "main_pass": 3, "valid_runs": {"branch": 3, "main": 3},
                                   "void_limited": False, "verdict": "pass"}
    assert set(entry["fingerprints"]) == {"agents/a.md", "skills/s1/SKILL.md", "tests/skills/s1/handoff.yaml"}
    table = (out / "skills-s1.md").read_text()
    assert "| a | Fast | low | 3/3 | 3/3 | pass |" in table and "Runtime" not in table
    assert "attempt 1 for version 1.0.1" in capsys.readouterr().out


def test_nothing_in_the_release_folder_names_a_runtime(fake, repo):
    bump(repo)
    assert go() == 0
    ladders = load_ladders()
    runtime = "claude-code"
    forbidden = {runtime, *ladders[runtime].values()}
    for f in (repo / "tests/releases").rglob("*"):
        if f.is_file():
            text = f.read_text()
            assert not [word for word in forbidden if word in text], f


def test_recording_again_counts_the_attempt_and_replaces_the_folder(fake, repo, capsys):
    bump(repo)
    assert go() == 0
    stale = write(repo, "tests/releases/1.0.1/stale.md", "old")
    assert go() == 0
    assert manifest_of(repo)["attempt"] == 2
    assert not stale.exists()
    assert "attempt 2 for version 1.0.1" in capsys.readouterr().out


def test_every_selected_file_runs_in_its_own_mode(fake, repo):
    bump(repo)
    write(repo, "scripts/g.sh", "echo h")
    commit(repo)
    assert go() == 0
    assert fake.file_runs == ["handoff.yaml", "patterns.yaml"]
    assert [(e["path"], e["mode"]) for e in manifest_of(repo)["tests"]] == [
        ("tests/skills/s1/handoff.yaml", "skill"), ("tests/agents/a1/patterns.yaml", "agent")]
    assert sorted(p.name for p in (repo / "tests/releases/1.0.1").iterdir()) == [
        "agents-a1.md", "manifest.json", "offline.txt", "skills-s1.md"]


def test_a_failing_test_file_is_written_as_a_fail_and_exits_one(fake, repo):
    bump(repo)
    fake.passing = False
    assert go() == 1
    assert manifest_of(repo)["tests"][0]["verdict"] == "fail"
    fails, _ = check_gate(repo, "main")
    assert any("verdict" in f for f in fails)


def test_nothing_selected_writes_nothing_and_exits_zero(fake, repo, capsys):
    write(repo, "README.md", "r2")
    commit(repo)
    assert go() == 0
    assert not (repo / "tests/releases").exists() and fake.file_runs == []
    assert "no covered changes" in capsys.readouterr().out


def test_refuses_when_main_is_not_origin_main(fake, repo):
    bump(repo)
    fake.synced = False
    assert go() == 1
    assert fake.file_runs == [] and not (repo / "tests/releases").exists()


def test_a_failing_offline_run_stops_before_any_model_run(fake, repo):
    bump(repo)
    fake.offline = (1, "3 failed")
    assert go() == 1
    assert fake.file_runs == [] and not (repo / "tests/releases").exists()


def test_offline_tests_run_before_selection_so_even_no_change_needs_them(fake, repo):
    fake.offline = (1, "3 failed")
    assert go() == 1


def test_refuses_when_the_version_matches_main(fake, repo, capsys):
    write(repo, "agents/a.md", "v2")
    commit(repo)
    assert go() == 1
    assert "bump the version first" in capsys.readouterr().err
    assert fake.file_runs == []


def test_refuses_uncommitted_changes_to_a_covered_file(fake, repo, capsys):
    bump(repo)
    write(repo, "skills/s1/SKILL.md", "dirty")
    assert go() == 1
    err = capsys.readouterr().err
    assert "uncommitted" in err and "skills/s1/SKILL.md" in err
    assert fake.file_runs == []


def test_uncommitted_changes_elsewhere_do_not_block_recording(fake, repo):
    bump(repo)
    write(repo, "README.md", "dirty")
    assert go() == 0


def test_refuses_when_a_selected_test_file_was_deleted(fake, repo, capsys):
    bump(repo)
    (repo / "tests/skills/s1/handoff.yaml").unlink()
    commit(repo)
    assert go() == 1
    assert "a selected test file was deleted" in capsys.readouterr().err
    assert fake.file_runs == []


@pytest.mark.parametrize("argv", [
    ["--record", "--runtime", "rt"],
    ["--changed", "--record", "--runtime", "rt", "--pressure", "none"],
    ["--changed", "--record", "--runtime", "rt", "--tier", "low"],
    ["--changed", "--record", "--runtime", "rt", "--ladder"],
    ["--changed", "--record", "--runtime", "rt", "--runs", "2"],
    ["--changed", "--record", "--runtime", "rt", "--dry-run"],
    ["--changed", "--record", "--runtime", "rt", "--case", "a"],
    ["--changed", "feat", "--record", "--runtime", "rt"],
])
def test_record_refuses_partial_or_mismatched_runs(argv, fake):
    with pytest.raises(SystemExit) as e:
        run.main(argv)
    assert e.value.code == 2
    assert fake.file_runs == []


def test_record_accepts_more_than_three_runs_and_a_jobs_count(fake, repo):
    bump(repo)
    assert run.main(["--changed", "--record", "--runtime", "rt", "--runs", "4", "--jobs", "2"]) == 0
    assert manifest_of(repo)["runs"] == 4


# --- R2: the gate, offline ---

@pytest.fixture
def recorded(fake, repo):
    bump(repo)
    assert go() == 0
    assert check_gate(repo, "main")[0] == []
    return repo


def fails_of(repo):
    fails, _ = check_gate(repo, "main")
    return fails


def rewrite_manifest(repo, edit, version="1.0.1"):
    path = repo / "tests/releases" / version / "manifest.json"
    m = json.loads(path.read_text())
    edit(m)
    path.write_text(json.dumps(m))


def test_gate_passes_with_no_covered_changes(repo):
    write(repo, "README.md", "r2")
    commit(repo)
    assert check_gate(repo, "main") == ([], "no covered changes")


def test_gate_passes_on_a_clean_recording(recorded):
    fails, message = check_gate(recorded, "main")
    assert fails == [] and message.startswith("gate ok")


def test_gate_fails_without_a_version_bump(repo):
    write(repo, "agents/a.md", "v2")
    commit(repo)
    assert any("equals main's" in f for f in fails_of(repo))


def test_gate_fails_when_the_manifest_is_missing(repo):
    bump(repo)
    assert any("missing tests/releases/1.0.1/manifest.json" in f for f in fails_of(repo))


def test_gate_fails_on_an_unreadable_manifest(recorded):
    (recorded / "tests/releases/1.0.1/manifest.json").write_text("{")
    assert any("not valid JSON" in f for f in fails_of(recorded))


def test_gate_fails_when_the_manifest_version_differs_from_its_folder(recorded):
    rewrite_manifest(recorded, lambda m: m.update(version="0.9.0"))
    assert any("differs from its folder" in f for f in fails_of(recorded))


def test_gate_fails_when_a_selected_test_file_is_not_in_the_manifest(recorded):
    rewrite_manifest(recorded, lambda m: m.update(tests=[]))
    assert any("manifest lacks selected test file tests/skills/s1/handoff.yaml" in f for f in fails_of(recorded))


def test_gate_fails_when_a_case_in_the_head_yaml_is_not_in_the_manifest(recorded):
    rewrite_manifest(recorded, lambda m: m["tests"][0]["cases"].pop("b"))
    assert any("manifest lacks case b" in f for f in fails_of(recorded))


@pytest.mark.parametrize("edit", [
    lambda m: m["tests"][0]["cases"]["a"].update(verdict="fail"),
    lambda m: m["tests"][0].update(verdict="fail"),
])
def test_gate_fails_on_any_failing_verdict(recorded, edit):
    rewrite_manifest(recorded, edit)
    assert any("verdict is 'fail'" in f for f in fails_of(recorded))


@pytest.fixture
def recorded_agent(fake, repo):
    bump(repo)
    write(repo, "scripts/g.sh", "echo h")
    commit(repo)
    assert go() == 0
    assert check_gate(repo, "main")[0] == []
    return repo


def agent_entry(m):
    return next(e for e in m["tests"] if e["mode"] == "agent")


def test_gate_fails_an_agent_file_under_80_percent_even_if_its_verdicts_say_pass(recorded_agent):
    def edit(m):
        e = agent_entry(m)
        for c in e["cases"].values():
            c["branch_pass"], c["main_pass"] = 1, 2   # within main - 1, none at zero, verdicts still say pass
    rewrite_manifest(recorded_agent, edit)
    assert any("branch passed" in f and "under 80%" in f for f in fails_of(recorded_agent))


def test_gate_fails_on_a_failing_agent_file_verdict_or_case_verdict(recorded_agent):
    rewrite_manifest(recorded_agent, lambda m: agent_entry(m).update(verdict="fail"))
    assert any("tests/agents/a1/patterns.yaml: verdict is 'fail'" in f for f in fails_of(recorded_agent))
    rewrite_manifest(recorded_agent, lambda m: agent_entry(m).update(verdict="pass"))
    rewrite_manifest(recorded_agent, lambda m: next(iter(agent_entry(m)["cases"].values())).update(verdict="fail"))
    assert any("tests/agents/a1/patterns.yaml: case" in f and "'fail'" in f for f in fails_of(recorded_agent))


def test_gate_fails_when_a_fingerprinted_file_changed_after_testing(recorded):
    write(recorded, "skills/s1/SKILL.md", "edited after the run")
    assert any("skills/s1/SKILL.md changed since it was tested" in f for f in fails_of(recorded))


def test_gate_fails_when_the_case_file_itself_changed(recorded):
    write(recorded, "tests/skills/s1/handoff.yaml", SKILL_FILE + "# edit\n")
    assert any("tests/skills/s1/handoff.yaml changed since" in f for f in fails_of(recorded))


def test_gate_fails_when_a_fingerprinted_file_is_gone(recorded):
    (recorded / "skills/s1/SKILL.md").unlink()
    assert any("fingerprinted file is missing: skills/s1/SKILL.md" in f for f in fails_of(recorded))


def test_gate_fails_when_a_newly_covered_file_has_no_fingerprint(recorded):
    write(recorded, "skills/s1/added.md", "new")
    git(recorded, "add", "skills/s1/added.md")
    assert any("skills/s1/added.md is covered but has no fingerprint" in f for f in fails_of(recorded))


def test_gate_fails_when_a_selected_test_file_was_deleted(recorded):
    (recorded / "tests/skills/s1/handoff.yaml").unlink()
    commit(recorded)
    assert any("a selected test file was deleted" in f for f in fails_of(recorded))


def test_gate_ignores_untracked_files_and_tests_only_edits_elsewhere(recorded):
    write(recorded, "skills/s1/scratch.md", "untracked")
    write(recorded, "tests/run.py", "x")
    git(recorded, "add", "tests/run.py")
    git(recorded, "commit", "-q", "-m", "tests only")
    assert fails_of(recorded) == []


def test_gate_cli_prints_and_exits(capsys, monkeypatch, repo):
    import gate
    monkeypatch.setattr(gate, "TESTS_DIR", repo / "tests")
    write(repo, "agents/a.md", "v2")
    commit(repo)
    assert gate.main(["--base", "main"]) == 1
    out = capsys.readouterr().out
    assert "gate FAILED against main" in out and "  - " in out
    git(repo, "checkout", "-q", "main")
    git(repo, "checkout", "-q", "-B", "feat")
    assert gate.main(["--base", "main"]) == 0
    assert "no covered changes" in capsys.readouterr().out
    assert gate.main(["--base", "no-such-ref"]) == 2


def test_plugin_version_reads_the_tree_or_a_ref(repo):
    bump(repo, "1.0.9")
    assert (plugin_version(repo), plugin_version(repo, "main")) == ("1.0.9", "1.0.0")
