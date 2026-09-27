"""Turn results into report.md and runs.jsonl. Names no runtime."""
import json
from pathlib import Path

from harness.core.cases import TIERS, expected_tier
from harness.core.runner import CaseResult, passes


def _valid(records, version, tier):
    return sum(1 for r in records if r.version == version and r.tier == tier and r.verdict.result != "VOID")


def _flag(result: CaseResult, expected: str) -> str:
    if result.void_limited:
        return "VOID LIMIT"
    if result.lowest_tier is None:
        if result.only_tier is not None:
            return f"NO PASS AT {result.only_tier} (only tier tried)"
        return f"NO PASSING TIER (tried up to {result.max_tier})"
    if TIERS.index(result.lowest_tier) > TIERS.index(expected):
        return "ABOVE EXPECTED"
    return ""


def render(results: list[CaseResult], ladders: dict, runtime: str) -> str:
    lines = [
        f"# Test report — {runtime}",
        "",
        "| Case | Expected role | Tier | Branch | Main | Lowest passing tier | Expected tier | Flag |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for result in results:
        expected = expected_tier(result.case, ladders)
        flag = _flag(result, expected)
        tiers_run = [t for t in TIERS if any(r.tier == t for r in result.records)]
        for tier in tiers_run:
            branch = f"{passes(result.records, 'branch', tier)}/{_valid(result.records, 'branch', tier)}"
            main = f"{passes(result.records, 'main', tier)}/{_valid(result.records, 'main', tier)}"
            lowest = result.lowest_tier or "—"
            lines.append(f"| {result.case.id} | {result.case.expect} | {tier} | {branch} | {main} | {lowest} | {expected} | {flag} |")

    lines += ["", "## Failed and void runs", ""]
    for result in results:
        for r in result.records:
            if r.verdict.result == "PASS":
                continue
            events = ", ".join(f"{e.kind}:{e.detail}" for e in r.events) or "(none)"
            lines.append(f"- **{r.case_id}** {r.version} {r.tier} #{r.attempt} — {r.verdict.result}: {r.verdict.reason}")
            lines.append(f"  - events: {events}")
    return "\n".join(lines) + "\n"


def write_results(out_dir: Path, results: list[CaseResult], report: str) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "runs.jsonl", "w") as f:
        for result in results:
            for r in result.records:
                f.write(json.dumps(r.to_dict()) + "\n")
    (out_dir / "report.md").write_text(report)
