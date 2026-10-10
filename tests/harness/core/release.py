"""Release recording and the gate check. Names no runtime.

`run.py --changed --record` writes `tests/releases/<version>/` from a finished
model run; `gate.py` re-checks that folder offline against the branch's files.
The pass rules (D1) and the fingerprints live here so the two agree.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from harness.core.cases import load_agent_cases, load_cases
from harness.core.changed import SelectedTest, changed_files, frontmatter_block, matches, select_for_base
from harness.core.runner import passes

RELEASES = "tests/releases"
PLUGIN_JSON = ".claude-plugin/plugin.json"
NO_CHANGES = "no covered changes"


def _git(repo_root: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def rev_parse(repo_root: Path, ref: str) -> str:
    return _git(repo_root, "rev-parse", ref).strip()


def plugin_version(repo_root: Path, ref: str | None = None) -> str:
    """The plugin version in the working tree, or as committed at `ref`."""
    text = _git(repo_root, "show", f"{ref}:{PLUGIN_JSON}") if ref else (Path(repo_root) / PLUGIN_JSON).read_text()
    return json.loads(text)["version"]


def release_dir(repo_root: Path, version: str) -> Path:
    return Path(repo_root) / RELEASES / version


# --- D1: the pass rule ---

FILE_PASS_RATE = (3, 4)  # agent-mode files pass on at least 3/4 (75%) of their branch runs


def case_verdict(result, runs: int, agent_mode: bool) -> dict:
    """D1, per case: the branch passes at least `main`'s passes minus one (a
    one-run gap is allowed). An agent-mode case also needs at least one branch
    pass (no case at zero); the file-level rate is `file_verdict`'s. Always a
    fail when the case hit its void limit or either side has fewer than `runs`
    valid (non-VOID) runs, or no single expected tier is known."""
    tier = result.only_tier

    def valid(version):
        return sum(1 for r in result.records if r.version == version and r.tier == tier and r.verdict.result != "VOID")

    branch_pass, main_pass = passes(result.records, "branch", tier), passes(result.records, "main", tier)
    branch_valid, main_valid = valid("branch"), valid("main")
    floor_ok = branch_pass >= 1 if agent_mode else True
    ok = (tier is not None and not result.void_limited and branch_valid >= runs and main_valid >= runs
          and branch_pass >= main_pass - 1 and floor_ok)
    return {"tier": tier, "branch_pass": branch_pass, "main_pass": main_pass,
            "valid_runs": {"branch": branch_valid, "main": main_valid},
            "void_limited": result.void_limited, "verdict": "pass" if ok else "fail"}


def branch_totals(cases: dict) -> tuple[int, int]:
    """(branch passes, valid branch runs) summed over a file's case entries."""
    return (sum(c.get("branch_pass", 0) for c in cases.values()),
            sum(c.get("valid_runs", {}).get("branch", 0) for c in cases.values()))


def rate_ok(passed: int, total: int) -> bool:
    return total > 0 and passed * FILE_PASS_RATE[1] >= total * FILE_PASS_RATE[0]


def file_verdict(cases: dict, agent_mode: bool) -> dict:
    """The file's verdict from its case entries. Skill mode: every case passes.
    Agent mode: every case passes (so none is at zero or two below main) and the
    branch passes at least 75% of all its runs together."""
    passed, total = branch_totals(cases)
    ok = bool(cases) and all(c["verdict"] == "pass" for c in cases.values())
    if agent_mode:
        ok = ok and rate_ok(passed, total)
    return {"branch_pass": passed, "branch_runs": total, "pass_rate": round(passed / total, 3) if total else 0.0,
            "verdict": "pass" if ok else "fail"}


# --- fingerprints ---

def file_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def fingerprint_paths(repo_root: Path, test: SelectedTest) -> list[str]:
    """Tracked files matched by the test's base-or-head covers or covers_frontmatter, plus its own yaml."""
    root = Path(repo_root)
    paths = [p for p in _git(root, "ls-files").splitlines()
             if (matches(test.covers, p) or matches(test.covers_frontmatter, p))
             and not p.startswith(RELEASES + "/") and (root / p).is_file()]
    return sorted(set(paths) | {test.path})


def fingerprint_of(repo_root: Path, test: SelectedTest, path: str) -> str:
    """A file's fingerprint: its whole content, or only its frontmatter block when
    the test covers it by `covers_frontmatter:` alone. The gate uses the same function."""
    f = Path(repo_root) / path
    if path != test.path and test.frontmatter_only(path):
        return text_hash(frontmatter_block(f.read_text()))
    return file_hash(f)


def fingerprints(repo_root: Path, test: SelectedTest) -> dict:
    return {p: fingerprint_of(repo_root, test, p) for p in fingerprint_paths(repo_root, test)}


def dirty_covered(repo_root: Path, tests) -> list[str]:
    """Covered files (and case files) with uncommitted changes to tracked content.
    A frontmatter-only file counts only when its frontmatter, not just its body, changed."""
    dirty = set(_git(repo_root, "diff", "--name-only", "HEAD").splitlines())
    out = set()
    for t in tests:
        for p in set(fingerprint_paths(repo_root, t)) & dirty:
            if p != t.path and t.frontmatter_only(p):
                committed = frontmatter_block(_git(repo_root, "show", f"HEAD:{p}"))
                if committed == frontmatter_block((Path(repo_root) / p).read_text()):
                    continue
            out.add(p)
    return sorted(out)


# --- recording ---

def slug_of(test_path: str) -> str:
    """tests/skills/advisor-mode/handoff.yaml -> skills-advisor-mode"""
    return "-".join(Path(test_path).parent.relative_to("tests").parts)


def entry_for(repo_root: Path, test: SelectedTest, results, runs: int, results_path: str) -> dict:
    cases = {r.case.id: case_verdict(r, runs, test.agent_mode) for r in results}
    f = file_verdict(cases, test.agent_mode)
    return {"path": test.path, "mode": "agent" if test.agent_mode else "skill", "results": results_path,
            "cases": cases, "branch_pass": f["branch_pass"], "branch_runs": f["branch_runs"],
            "pass_rate": f["pass_rate"], "verdict": f["verdict"], "fingerprints": fingerprints(repo_root, test)}


def case_table(entry: dict, results) -> str:
    """One test file's case table as markdown. No runtime column, no runtime name."""
    roles = {r.case.id: r.case.expect for r in results}
    rate = f"; branch passes {entry['branch_pass']}/{entry['branch_runs']} ({entry['pass_rate']:.1%})"
    lines = [f"# {entry['path']}", "", f"Verdict: **{entry['verdict']}** ({entry['mode']} mode{rate}, results {entry['results']})", "",
             "| Case | Expected role | Tier | Branch | Main | Verdict |", "|---|---|---|---|---|---|"]
    for cid, c in entry["cases"].items():
        v = c["valid_runs"]
        flag = " (void limit)" if c["void_limited"] else ""
        lines.append(f"| {cid} | {roles.get(cid, '')} | {c['tier']} | {c['branch_pass']}/{v['branch']} "
                     f"| {c['main_pass']}/{v['main']} | {c['verdict']}{flag} |")
    return "\n".join(lines) + "\n"


def previous_attempt(repo_root: Path, version: str) -> int:
    try:
        return int(json.loads((release_dir(repo_root, version) / "manifest.json").read_text()).get("attempt", 0))
    except (OSError, ValueError, TypeError):
        return 0


def total_cost(all_results) -> float:
    return sum(r.cost_usd for results in all_results for res in results for r in res.records if r.cost_usd is not None)


def write_release(repo_root: Path, manifest: dict, offline_line: str, tables: dict) -> Path:
    """Replace tests/releases/<version>/ with manifest.json, offline.txt and one <slug>.md per test file."""
    out = release_dir(repo_root, manifest["version"])
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")
    (out / "offline.txt").write_text(offline_line.strip() + "\n")
    for slug, text in tables.items():
        (out / f"{slug}.md").write_text(text)
    return out


# --- the gate ---

def _head_case_ids(repo_root: Path, test: SelectedTest) -> list[str]:
    path = Path(repo_root) / test.path
    return [c.id for c in (load_agent_cases(path) if test.agent_mode else load_cases(path))]


def check_gate(repo_root: Path, base: str):
    """(failures, message). No failures and NO_CHANGES when nothing is selected."""
    root = Path(repo_root)
    selection = select_for_base(root, base, changed_files(root, base))
    if not selection.selected:
        return [], NO_CHANGES
    fails = []
    version = plugin_version(root)
    if version == plugin_version(root, base):
        fails.append(f"plugin.json version {version} equals {base}'s: covered files changed, bump the version")
    fails += [f"a selected test file was deleted: {p}" for p in selection.deleted]

    manifest_path = release_dir(root, version) / "manifest.json"
    if not manifest_path.is_file():
        return fails + [f"missing {manifest_path.relative_to(root)}: record it with run.py --changed --record"], ""
    try:
        manifest = json.loads(manifest_path.read_text())
    except ValueError as e:
        return fails + [f"{manifest_path.relative_to(root)} is not valid JSON: {e}"], ""
    if manifest.get("version") != version:
        fails.append(f"manifest version {manifest.get('version')!r} differs from its folder {version!r}")

    entries = {e.get("path"): e for e in manifest.get("tests", [])}
    for test in selection.selected:
        if not test.in_head:
            continue
        entry = entries.get(test.path)
        if entry is None:
            fails.append(f"manifest lacks selected test file {test.path}")
            continue
        try:
            ids = _head_case_ids(root, test)
        except ValueError as e:
            fails.append(f"{test.path} does not load: {e}")
            ids = []
        cases = entry.get("cases", {})
        fails += [f"{test.path}: manifest lacks case {cid}" for cid in ids if cid not in cases]
        fails += [f"{test.path}: case {cid} verdict is {c.get('verdict')!r}" for cid, c in cases.items() if c.get("verdict") != "pass"]
        if entry.get("verdict") != "pass":
            fails.append(f"{test.path}: verdict is {entry.get('verdict')!r}")
        if test.agent_mode:
            passed, total = branch_totals(cases)
            if not rate_ok(passed, total):
                fails.append(f"{test.path}: branch passed {passed} of {total} runs, under 75%")
        prints = entry.get("fingerprints", {})
        for path, digest in prints.items():
            f = root / path
            if not f.is_file():
                fails.append(f"{test.path}: fingerprinted file is missing: {path}")
            elif fingerprint_of(root, test, path) != digest:
                fails.append(f"{test.path}: {path} changed since it was tested")
        fails += [f"{test.path}: {p} is covered but has no fingerprint" for p in fingerprint_paths(root, test) if p not in prints]
    return fails, "" if fails else f"gate ok: {len(selection.selected)} test file(s) recorded for {version}"
