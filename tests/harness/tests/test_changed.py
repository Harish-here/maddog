"""--changed: covers: loading, glob matching, test selection, and run.py's offline paths."""
import subprocess

import pytest
import run
from harness.core.cases import TESTS_DIR, load_agent_cases, load_cases, load_covers, load_covers_frontmatter
from harness.core.changed import (changed_files, discover, frontmatter_block, glob_to_regex, matches, select_for_base,
                                  select_tests)
from harness.tests.test_cases import AGENT_FILE

SKILL_FILE = "skill: x\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: none}\n"


def write(tmp_path, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


# --- covers: loading ---

def test_covers_absent_means_covers_nothing(tmp_path):
    assert load_covers(write(tmp_path, "handoff.yaml", SKILL_FILE)) == ()


def test_covers_loads_as_a_tuple_of_globs(tmp_path):
    path = write(tmp_path, "handoff.yaml", 'covers:\n  - "a/**"\n  - "b/*.md"\n' + SKILL_FILE)
    assert load_covers(path) == ("a/**", "b/*.md")


@pytest.mark.parametrize("bad", ["covers: a/**\n", "covers: [1]\n", "covers: [[x]]\n", "covers: ['']\n", "covers: {a: b}\n"])
def test_covers_must_be_a_list_of_strings(tmp_path, bad):
    path = write(tmp_path, "handoff.yaml", bad + SKILL_FILE)
    with pytest.raises(ValueError, match="'covers' must be a list"):
        load_covers(path)
    with pytest.raises(ValueError, match="'covers' must be a list"):
        load_cases(path)


def test_agent_case_files_validate_covers_too(tmp_path):
    path = write(tmp_path, "patterns.yaml", "covers: nope\n" + AGENT_FILE)
    with pytest.raises(ValueError, match="'covers' must be a list"):
        load_agent_cases(path)


def test_the_shipped_case_files_declare_their_covers():
    advisor = TESTS_DIR / "skills/advisor-mode/handoff.yaml"
    assert load_covers(advisor) == ("skills/advisor-mode/**",)
    assert load_covers_frontmatter(advisor) == ("agents/executor-*.md",)
    for agent in ("executor-fast", "executor-fast-read"):
        assert load_covers(TESTS_DIR / "agents" / agent / "patterns.yaml") == (
            f"agents/{agent}.md", "scripts/pattern-declare-guard.sh", "hooks/hooks.json")


# --- glob matching ---

@pytest.mark.parametrize("glob, path, expected", [
    ("skills/advisor-mode/**", "skills/advisor-mode/SKILL.md", True),
    ("skills/advisor-mode/**", "skills/advisor-mode/refs/deep/x.md", True),
    ("skills/advisor-mode/**", "skills/other/SKILL.md", False),
    ("skills/advisor-mode/**", "skills/advisor-mode", False),
    ("**/x.md", "x.md", True),
    ("**/x.md", "a/b/x.md", True),
    ("a/**/x.md", "a/x.md", True),
    ("a/**/x.md", "a/b/c/x.md", True),
    ("a/**/x.md", "ab/x.md", False),
    ("agents/executor-*.md", "agents/executor-fast.md", True),
    ("agents/executor-*.md", "agents/executor-fast-read.md", True),
    ("agents/executor-*.md", "agents/product-pm.md", False),
    ("agents/executor-*.md", "agents/sub/executor-fast.md", False),  # one star stays in one folder
    ("scripts/*.sh", "scripts/a/b.sh", False),
    ("a?c.md", "abc.md", True),
    ("a?c.md", "a/c.md", False),
    ("hooks/hooks.json", "hooks/hooks.json", True),
    ("hooks/hooks.json", "hooks/hooksxjson", False),  # dots are literal
    ("hooks/hooks.json", "hooks/hooks.json.bak", False),
])
def test_glob_matching(glob, path, expected):
    assert bool(glob_to_regex(glob).match(path)) is expected


def test_matches_is_any_glob_against_one_path():
    assert matches(["a/*", "b/**"], "b/c/d")
    assert not matches(["a/*"], "a/b/c")
    assert not matches([], "anything")


# --- selection ---

def make_tests(tmp_path):
    write(tmp_path, "skills/s1/handoff.yaml", 'covers: ["skills/s1/**", "agents/executor-*.md"]\n' + SKILL_FILE)
    write(tmp_path, "skills/s2/handoff.yaml", SKILL_FILE)  # no covers: never selected
    write(tmp_path, "agents/a1/patterns.yaml", 'covers: ["scripts/g.sh"]\n' + AGENT_FILE)
    write(tmp_path, "agents/a2/handoff.yaml", 'covers: ["scripts/g.sh"]\n' + SKILL_FILE)  # only patterns.yaml is discovered under agents/
    return discover(tmp_path)


def test_discover_finds_handoff_under_skills_and_patterns_under_agents(tmp_path):
    found = make_tests(tmp_path)
    assert [(p.relative_to(tmp_path).as_posix(), agent_mode) for p, agent_mode in found] == [
        ("skills/s1/handoff.yaml", False), ("skills/s2/handoff.yaml", False), ("agents/a1/patterns.yaml", True)]


def test_discover_on_the_real_tree_finds_the_shipped_files():
    names = {p.relative_to(TESTS_DIR).as_posix() for p, _ in discover(TESTS_DIR)}
    assert {"skills/advisor-mode/handoff.yaml", "agents/executor-fast/patterns.yaml",
            "agents/executor-fast-read/patterns.yaml"} <= names


def selected(tmp_path, changed):
    return [(p.relative_to(tmp_path).as_posix(), agent_mode) for p, agent_mode in select_tests(make_tests(tmp_path), changed)]


def test_a_changed_file_selects_only_the_tests_that_cover_it(tmp_path):
    assert selected(tmp_path, ["skills/s1/SKILL.md"]) == [("skills/s1/handoff.yaml", False)]
    assert selected(tmp_path, ["scripts/g.sh"]) == [("agents/a1/patterns.yaml", True)]


def test_one_changed_file_can_select_several_tests_and_modes(tmp_path):
    assert selected(tmp_path, ["agents/executor-fast.md", "scripts/g.sh"]) == [
        ("skills/s1/handoff.yaml", False), ("agents/a1/patterns.yaml", True)]


def test_nothing_changed_or_nothing_matching_selects_nothing(tmp_path):
    assert selected(tmp_path, []) == []
    assert selected(tmp_path, ["README.md", "tests/run.py"]) == []


# --- changed_files against a real git repo ---

def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    write(tmp_path, "a.txt", "1")
    write(tmp_path, "b.txt", "1")
    git(tmp_path, "add", "."), git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "checkout", "-q", "-b", "feat")
    return tmp_path


def test_changed_files_joins_branch_commits_and_uncommitted_tracked_changes(repo):
    write(repo, "dir/new.txt", "x")
    git(repo, "add", "."), git(repo, "commit", "-q", "-m", "branch")
    write(repo, "b.txt", "2")  # uncommitted edit to a tracked file
    write(repo, "untracked.txt", "x")  # untracked: not counted
    assert changed_files(repo, "main") == ["b.txt", "dir/new.txt"]


def test_changed_files_ignores_what_main_gained_after_the_branch_left(repo):
    git(repo, "checkout", "-q", "main")
    write(repo, "a.txt", "2")
    git(repo, "commit", "-qam", "main moves")
    git(repo, "checkout", "-q", "feat")
    assert changed_files(repo, "main") == []


def test_changed_files_with_an_unknown_base_raises(repo):
    with pytest.raises(ValueError, match="failed"):
        changed_files(repo, "no-such-ref")


# --- run.py --changed, offline ---

def fake_selection(monkeypatch, tmp_path, changed):
    monkeypatch.setattr(run, "changed_files", lambda root, base: changed)
    monkeypatch.setattr(run, "sweep", lambda root: pytest.fail("a dry run must not sweep"))


def boom(*a, **k):
    pytest.fail("a dry run must not call a model")


def test_dry_run_prints_changed_files_selection_and_counts_then_exits(monkeypatch, capsys):
    fake_selection(monkeypatch, None, ["agents/executor-fast.md", "skills/advisor-mode/SKILL.md"])
    monkeypatch.setattr(run, "run_cases", boom)
    monkeypatch.setattr(run, "get_adapter", boom)
    assert run.main(["--changed", "--runtime", "rt", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "changed files vs main: 2" in out
    assert "agents/executor-fast.md" in out
    assert "tests/skills/advisor-mode/handoff.yaml (skill mode)" in out  # skills/advisor-mode/** covers it
    assert "tests/agents/executor-fast/patterns.yaml (agent mode)" in out
    assert "tests/agents/executor-fast-read/patterns.yaml" not in out
    n = len(load_agent_cases(TESTS_DIR / "agents/executor-fast/patterns.yaml"))
    assert f"{n} cases x 3 runs x 2 sides (branch, main) = {n * 6} runs" in out


def test_dry_run_honours_runs_and_a_base(monkeypatch, capsys):
    seen = []
    monkeypatch.setattr(run, "changed_files", lambda root, base: seen.append(base) or ["hooks/hooks.json"])
    assert run.main(["--changed", "origin/main", "--runtime", "rt", "--dry-run", "--runs", "1"]) == 0
    out = capsys.readouterr().out
    assert seen == ["origin/main"]
    assert "x 1 runs x 2 sides" in out


def test_nothing_selected_says_so_and_exits_zero(monkeypatch, capsys):
    fake_selection(monkeypatch, None, ["README.md"])
    monkeypatch.setattr(run, "run_cases", boom)
    assert run.main(["--changed", "--runtime", "rt"]) == 0
    assert "no model tests selected" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [
    ["skills/advisor-mode", "--changed", "--runtime", "rt"],
    ["--changed", "main", "skills/advisor-mode", "--runtime", "rt"],
    ["--runtime", "rt"],
    ["skills/advisor-mode", "--runtime", "rt", "--dry-run"],
    ["--changed", "--runtime", "rt", "--case", "x"],
    ["--changed", "--runtime", "rt", "--patterns"],
])
def test_bad_argument_combinations_are_rejected(argv):
    with pytest.raises(SystemExit) as e:
        run.main(argv)
    assert e.value.code == 2


def test_an_unknown_base_is_a_usage_error(monkeypatch):
    def bad(root, base):
        raise ValueError("git diff failed: unknown revision")
    monkeypatch.setattr(run, "changed_files", bad)
    with pytest.raises(SystemExit) as e:
        run.main(["--changed", "nope", "--runtime", "rt", "--dry-run"])
    assert e.value.code == 2


# --- covers_frontmatter: ---

FM_FILE = '---\nname: x\ndescription: first\n---\nbody one\n'


@pytest.mark.parametrize("text, expected", [
    (FM_FILE, "name: x\ndescription: first"),
    ("---\nname: x\n---\n---\nnot the block\n", "name: x"),
    ("---\r\nname: x\r\n---\r\nbody", "name: x"),
    ("no frontmatter\n---\nfoo\n---\n", ""),
    ("---\nunclosed: yes\n", ""),
    ("", ""),
    (None, None),
])
def test_frontmatter_block_is_the_text_between_the_leading_dashes(text, expected):
    assert frontmatter_block(text) == expected


def test_covers_frontmatter_loads_and_defaults_to_nothing(tmp_path):
    assert load_covers_frontmatter(write(tmp_path, "handoff.yaml", SKILL_FILE)) == ()
    path = write(tmp_path, "h2.yaml", 'covers_frontmatter:\n  - "agents/*.md"\n' + SKILL_FILE)
    assert load_covers_frontmatter(path) == ("agents/*.md",) and load_covers(path) == ()


@pytest.mark.parametrize("bad", ["covers_frontmatter: a.md\n", "covers_frontmatter: [1]\n", "covers_frontmatter: ['']\n"])
def test_covers_frontmatter_must_be_a_list_of_strings(tmp_path, bad):
    path = write(tmp_path, "handoff.yaml", bad + SKILL_FILE)
    for load in (load_covers_frontmatter, load_covers, load_cases):
        with pytest.raises(ValueError, match="'covers_frontmatter' must be a list"):
            load(path)


CASES = "skill: s\nfixture: todo-app\ncases:\n  - {id: a, prompt: p, expect: Fast, pressure: none}\n"


@pytest.fixture
def fm_repo(tmp_path):
    """main has tests/skills/s/handoff.yaml covering skills/s/** in full and agents/*.md by frontmatter."""
    git(tmp_path, "init", "-q", "-b", "main")
    write(tmp_path, "tests/skills/s/handoff.yaml",
          'covers: ["skills/s/**"]\ncovers_frontmatter: ["agents/*.md", "skills/s/both.md"]\n' + CASES)
    write(tmp_path, "agents/fast.md", FM_FILE)
    write(tmp_path, "skills/s/both.md", FM_FILE)
    git(tmp_path, "add", "."), git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "checkout", "-q", "-b", "feat")
    return tmp_path


def picked(repo):
    return [t.path for t in select_for_base(repo, "main", changed_files(repo, "main")).selected]


def commit_all(repo):
    git(repo, "add", "."), git(repo, "commit", "-q", "-m", "c")


def test_advisor_mode_is_selected_by_an_executor_description_edit_but_not_a_body_edit(tmp_path):
    handoff = (TESTS_DIR / "skills/advisor-mode/handoff.yaml").read_text()
    git(tmp_path, "init", "-q", "-b", "main")
    write(tmp_path, "tests/skills/advisor-mode/handoff.yaml", handoff)
    write(tmp_path, "agents/executor-fast.md", FM_FILE)
    git(tmp_path, "add", "."), git(tmp_path, "commit", "-q", "-m", "base")
    git(tmp_path, "checkout", "-q", "-b", "feat")
    write(tmp_path, "agents/executor-fast.md", FM_FILE.replace("body one", "body two"))
    commit_all(tmp_path)
    assert picked(tmp_path) == []
    write(tmp_path, "agents/executor-fast.md", FM_FILE.replace("first", "second"))
    commit_all(tmp_path)
    assert picked(tmp_path) == ["tests/skills/advisor-mode/handoff.yaml"]


def test_a_body_only_edit_to_a_frontmatter_covered_file_selects_nothing(fm_repo):
    write(fm_repo, "agents/fast.md", FM_FILE.replace("body one", "body two"))
    commit_all(fm_repo)
    assert picked(fm_repo) == []


def test_a_frontmatter_edit_selects_the_test(fm_repo):
    write(fm_repo, "agents/fast.md", FM_FILE.replace("first", "second"))
    commit_all(fm_repo)
    assert picked(fm_repo) == ["tests/skills/s/handoff.yaml"]


def test_an_uncommitted_frontmatter_edit_selects_too(fm_repo):
    write(fm_repo, "agents/fast.md", FM_FILE.replace("first", "second"))
    assert picked(fm_repo) == ["tests/skills/s/handoff.yaml"]


def test_an_added_frontmatter_covered_file_counts_as_changed(fm_repo):
    write(fm_repo, "agents/new.md", "body only, no frontmatter\n")
    commit_all(fm_repo)
    assert picked(fm_repo) == ["tests/skills/s/handoff.yaml"]


def test_a_deleted_frontmatter_covered_file_counts_as_changed(fm_repo):
    (fm_repo / "agents/fast.md").unlink()
    commit_all(fm_repo)
    assert picked(fm_repo) == ["tests/skills/s/handoff.yaml"]


def test_a_file_matched_by_both_keys_is_covered_in_full(fm_repo):
    write(fm_repo, "skills/s/both.md", FM_FILE.replace("body one", "body two"))
    commit_all(fm_repo)
    assert picked(fm_repo) == ["tests/skills/s/handoff.yaml"]  # covers: wins, so a body edit selects


def test_frontmatter_globs_are_the_union_of_base_and_head(fm_repo):
    write(fm_repo, "tests/skills/s/handoff.yaml", 'covers: ["skills/s/**"]\n' + CASES)  # head drops the key
    write(fm_repo, "agents/fast.md", FM_FILE.replace("first", "second"))
    commit_all(fm_repo)
    (test,) = select_for_base(fm_repo, "main", changed_files(fm_repo, "main")).selected
    assert test.base_fm_covers == ("agents/*.md", "skills/s/both.md") and test.head_fm_covers == ()
    assert test.covers_frontmatter == ("agents/*.md", "skills/s/both.md")
