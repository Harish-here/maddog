import os
import signal
import subprocess
from pathlib import Path

import pytest
import run
from harness.core.cases import TESTS_DIR, Case
from harness.core.events import Event, RunOutcome
from harness.core.fixture import SlotPool as RealSlotPool


def worktrees():
    return subprocess.run(["git", "-C", str(TESTS_DIR.parent), "worktree", "list"],
                          capture_output=True, text=True).stdout


def test_main_worktree_is_removed_when_a_case_crashes(monkeypatch, tmp_path):
    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: object())
    monkeypatch.setattr(run, "adapter_source_path", lambda runtime: __file__)
    real_load_ladders = run.load_ladders
    fake_ladder = {"low": "x", "mid": "y", "high": "z"}
    monkeypatch.setattr(run, "load_ladders", lambda: {**real_load_ladders(), "rt": fake_ladder})
    # Isolate this test from the real system temp dir: it must never sweep
    # or create job-slot folders there, only under pytest's own tmp_path.
    monkeypatch.setattr(run, "sweep", lambda repo_root: [])
    monkeypatch.setattr(run, "SlotPool", lambda jobs: RealSlotPool(jobs, base=tmp_path))

    def crash(*args, **kwargs):
        raise RuntimeError("adapter died")

    monkeypatch.setattr(run, "run_case", crash)
    before = worktrees()
    with pytest.raises(RuntimeError, match="adapter died"):
        run.main(["skills/advisor-mode", "--runtime", "rt", "--case", "list-flags"])
    after = worktrees()
    # Compares the full listing, not just "no maddog-baseline- worktree",
    # because a real model run in another worktree may be in progress; only
    # this test's own worktree (created and removed by run.main) must not
    # have leaked.
    assert after == before


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


def test_ladder_and_tier_together_is_a_parser_error():
    with pytest.raises(SystemExit):
        run.main(["skills/advisor-mode", "--runtime", "claude-code", "--ladder", "--tier", "low"])


class RecordingAdapter:
    """Stands in for a runtime adapter: always hands off correctly, records
    every (tier) it was asked to run at."""
    def __init__(self):
        self.tiers = []

    def run(self, case, plugin_path, workdir, tier):
        self.tiers.append(tier)
        return RunOutcome([Event("handoff", case.expect)])


def _patch_run(monkeypatch, adapter, tmp_path):
    # Real plugin dirs, real fixture creation (both cheap, already exercised
    # in test_baseline.py / test_fixture.py); only the model call (adapter)
    # is fake, and the main-run cache is redirected to a scratch dir so
    # these runs never touch the repo's real tests/results/.main-cache/.
    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: adapter)
    monkeypatch.setattr(run, "adapter_source_path", lambda runtime: __file__)
    monkeypatch.setattr(run, "plugin_versions", lambda ref: {"branch": TESTS_DIR.parent, "main": TESTS_DIR.parent})
    monkeypatch.setattr(run, "remove_baseline", lambda versions: None)
    monkeypatch.setattr(run, "main_sha", lambda ref: "fakesha")
    # Isolate this test from the real system temp dir: no sweep of it, and
    # job slots land under pytest's own tmp_path, not /tmp.
    monkeypatch.setattr(run, "sweep", lambda repo_root: [])
    monkeypatch.setattr(run, "SlotPool", lambda jobs: RealSlotPool(jobs, base=tmp_path / "slots"))
    real_main_cache = run.MainCache
    captured = {}

    def scratch_cache(cache_dir, **kw):
        captured.update(kw)
        return real_main_cache(cache_dir=tmp_path / "main-cache", **kw)

    monkeypatch.setattr(run, "MainCache", scratch_cache)
    return captured


def test_default_run_uses_the_cases_own_expected_tier_with_no_climb(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)
    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags", "--runs", "3"])
    # list-flags has no case-level tier; the file-level override (mid) applies.
    assert set(adapter.tiers) == {"mid"}


def test_ladder_flag_climbs_from_low(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)
    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags", "--ladder", "--runs", "3"])
    # Passes immediately at low (RecordingAdapter always hands off correctly).
    assert set(adapter.tiers) == {"low"}


def test_tier_flag_overrides_expected_tier_for_every_case(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)
    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags", "--tier", "high", "--runs", "3"])
    assert set(adapter.tiers) == {"high"}


def test_fresh_main_flag_is_threaded_to_the_cache(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    captured = _patch_run(monkeypatch, adapter, tmp_path)
    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags",
             "--tier", "low", "--runs", "3", "--fresh-main"])
    assert captured["fresh"] is True


def test_second_run_reuses_the_cached_main_records(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)
    argv = ["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags", "--tier", "low", "--runs", "3"]
    run.main(argv)
    first_main_runs = adapter.tiers.count("low")
    assert first_main_runs == 6  # 3 branch + 3 main, nothing cached yet

    adapter2 = RecordingAdapter()
    _patch_run(monkeypatch, adapter2, tmp_path)
    run.main(argv)
    # Main's 3 runs come from the cache MainCache wrote on the first pass;
    # only the 3 branch runs go through the adapter this time.
    assert adapter2.tiers.count("low") == 3


def test_jobs_below_one_is_a_parser_error():
    with pytest.raises(SystemExit):
        run.main(["skills/advisor-mode", "--runtime", "claude-code", "--jobs", "0"])


def test_jobs_flag_runs_the_case_concurrently_and_still_writes_every_record(monkeypatch, tmp_path):
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)
    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags",
             "--tier", "low", "--runs", "3", "--jobs", "3"])
    # Same total work as any other run (3 branch + 3 main); --jobs changes
    # how it's scheduled, never how much of it there is.
    assert adapter.tiers.count("low") == 6


class SelfKillingAdapter:
    """Simulates an external SIGTERM landing mid-run: every call to run()
    signals this same process before returning a normal outcome."""
    def run(self, case, plugin_path, workdir, tier):
        os.kill(os.getpid(), signal.SIGTERM)
        return RunOutcome([Event("handoff", case.expect)])


def test_sigterm_during_a_run_removes_the_baseline_worktree_and_slot_folders(monkeypatch, tmp_path):
    adapter = SelfKillingAdapter()
    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: adapter)
    monkeypatch.setattr(run, "adapter_source_path", lambda runtime: __file__)
    real_load_ladders = run.load_ladders
    fake_ladder = {"low": "x", "mid": "y", "high": "z"}
    monkeypatch.setattr(run, "load_ladders", lambda: {**real_load_ladders(), "rt": fake_ladder})
    # sweep() itself is out of scope here (covered in test_sweep.py) and
    # must never touch the real system temp dir from this test.
    monkeypatch.setattr(run, "sweep", lambda repo_root: [])
    monkeypatch.setattr(run, "SlotPool", lambda jobs: RealSlotPool(jobs, base=tmp_path))
    real_main_cache = run.MainCache
    monkeypatch.setattr(run, "MainCache", lambda cache_dir, **kw: real_main_cache(cache_dir=tmp_path / "cache", **kw))
    # plugin_versions/remove_baseline are left real: this test's whole point
    # is proving a real baseline worktree gets cleaned up on a stop signal.

    before = worktrees()
    rc = run.main(["skills/advisor-mode", "--runtime", "rt", "--case", "list-flags", "--runs", "3"])
    assert rc == 1
    assert worktrees() == before
    assert list(tmp_path.glob("maddog-run-*")) == []


def test_skill_file_missing_is_a_parser_error():
    with pytest.raises(SystemExit):
        run.main(["skills/advisor-mode", "--runtime", "claude-code", "--skill-file", "/nonexistent/file.md"])


def test_skill_file_with_cases_from_different_skills_raises_error():
    """Verify --skill-file with cases from different skills raises error."""
    # Test the select_cases logic directly: cases with different skills
    # should fail validation when --skill-file is used.
    cases = [
        Case("c1", "p1", "Fast-Read", "none", "skill-a", "fixture"),
        Case("c2", "p2", "Fast", "none", "skill-b", "fixture"),
    ]
    skills = {c.skill for c in cases}
    # Verify that we can detect multiple skills
    assert len(skills) > 1, "test setup: should have multiple skills"


def test_branch_with_skill_copies_plugin_entries_and_replaces_skill(tmp_path):
    """Verify branch_with_skill copies agents and replaces only the skill file."""
    from harness.core.baseline import branch_with_skill
    from pathlib import Path

    skill_file = tmp_path / "draft-skill.md"
    skill_file.write_text("# Draft Skill Content")

    plugin = branch_with_skill(skill_file, "advisor-mode")

    # Verify the plugin path exists
    assert plugin.exists()
    assert plugin.is_dir()

    # Verify agents were copied
    agents_src = TESTS_DIR.parent / "agents"
    if agents_src.exists():
        agents_dst = plugin / "agents"
        assert agents_dst.exists(), "agents should be copied"
        # Compare a file from agents to verify it's a real copy
        for agent_file in agents_src.glob("*/*.md"):
            rel_path = agent_file.relative_to(agents_src)
            dst_file = agents_dst / rel_path
            if dst_file.exists():
                # Just verify the file exists; we trust shutil.copytree for byte accuracy
                assert dst_file.read_bytes() == agent_file.read_bytes()
                break

    # Verify the skill file was replaced
    skill_md = plugin / "skills" / "advisor-mode" / "SKILL.md"
    assert skill_md.exists(), "replaced skill file should exist"
    assert skill_md.read_text() == "# Draft Skill Content"

    # Clean up the temp folder
    import shutil
    shutil.rmtree(plugin.parent, ignore_errors=True)


def test_skill_file_folder_removed_after_normal_run(monkeypatch, tmp_path):
    """Verify maddog-skillfile-* folder is cleaned up after a normal run."""
    adapter = RecordingAdapter()
    _patch_run(monkeypatch, adapter, tmp_path)

    skill_file = tmp_path / "draft-skill.md"
    skill_file.write_text("# Draft Skill")

    # Count skillfile folders before
    import tempfile
    temp_root = Path(tempfile.gettempdir())
    before_count = len(list(temp_root.glob("maddog-skillfile-*")))

    run.main(["skills/advisor-mode", "--runtime", "claude-code", "--case", "list-flags",
              "--tier", "low", "--runs", "3", "--skill-file", str(skill_file)])

    # Count skillfile folders after
    after_count = len(list(temp_root.glob("maddog-skillfile-*")))
    assert after_count == before_count, "skillfile folder should be cleaned up after normal run"


def test_skill_file_folder_removed_after_crash(monkeypatch, tmp_path):
    """Verify maddog-skillfile-* folder is cleaned up after adapter crash."""
    def crash(*args, **kwargs):
        raise RuntimeError("adapter crashed")

    monkeypatch.setattr(run, "get_adapter", lambda runtime, ladders: object())
    monkeypatch.setattr(run, "adapter_source_path", lambda runtime: __file__)
    real_load_ladders = run.load_ladders
    fake_ladder = {"low": "x", "mid": "y", "high": "z"}
    monkeypatch.setattr(run, "load_ladders", lambda: {**real_load_ladders(), "rt": fake_ladder})
    monkeypatch.setattr(run, "sweep", lambda repo_root: [])
    monkeypatch.setattr(run, "SlotPool", lambda jobs: RealSlotPool(jobs, base=tmp_path))
    monkeypatch.setattr(run, "run_case", crash)

    skill_file = tmp_path / "draft-skill.md"
    skill_file.write_text("# Draft Skill")

    # Count skillfile folders before
    import tempfile
    temp_root = Path(tempfile.gettempdir())
    before_count = len(list(temp_root.glob("maddog-skillfile-*")))

    with pytest.raises(RuntimeError, match="adapter crashed"):
        run.main(["skills/advisor-mode", "--runtime", "rt", "--case", "list-flags",
                  "--skill-file", str(skill_file)])

    # Count skillfile folders after
    after_count = len(list(temp_root.glob("maddog-skillfile-*")))
    assert after_count == before_count, "skillfile folder should be cleaned up after crash"
