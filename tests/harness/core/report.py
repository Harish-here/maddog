"""Turn results into report.md and runs.jsonl. Names no runtime."""
import json
from pathlib import Path

from harness.core.cases import TIERS, expected_tier
from harness.core.runner import CaseResult, passes, tier_failed


def _valid(records, version, tier):
    return sum(1 for r in records if r.version == version and r.tier == tier and r.verdict.result != "VOID")


def _cached(records, version, tier):
    return any(r.cached for r in records if r.version == version and r.tier == tier)


def _cost(records, version, tier):
    known = [r.cost_usd for r in records if r.version == version and r.tier == tier and r.cost_usd is not None]
    return sum(known) if known else None


def _fmt_cost(value) -> str:
    return f"${value:.4f}" if value is not None else "n/a"


def _flag(result: CaseResult, expected: str, ladder: bool) -> str:
    if result.void_limited:
        return "VOID LIMIT"
    if not ladder:
        # Non-ladder run: flag if fewer than half the valid branch runs passed.
        if result.only_tier is not None:
            branch_passes = passes(result.records, "branch", result.only_tier)
            valid = _valid(result.records, "branch", result.only_tier)
            if tier_failed(branch_passes, valid):
                return f"FAIL AT {result.only_tier}"
        return ""
    if result.lowest_tier is None:
        return f"NO PASSING TIER (tried up to {result.max_tier})"
    if TIERS.index(result.lowest_tier) > TIERS.index(expected):
        return "ABOVE EXPECTED"
    return ""


def render(results: list[CaseResult], ladders: dict, runtime: str, ladder: bool = False) -> str:
    lines = [f"# Test report — {runtime}", ""]
    if ladder:
        lines.append("| Case | Expected role | Tier | Branch | Main | Cost | Lowest passing tier | Expected tier | Flag |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
    else:
        lines.append("| Case | Expected role | Tier | Branch | Main | Cost | Flag |")
        lines.append("|---|---|---|---|---|---|---|")

    total_cost = 0.0
    any_cost = False
    for result in results:
        expected = expected_tier(result.case, ladders)
        flag = _flag(result, expected, ladder)
        tiers_run = [t for t in TIERS if any(r.tier == t for r in result.records)]
        for tier in tiers_run:
            branch = f"{passes(result.records, 'branch', tier)}/{_valid(result.records, 'branch', tier)}"
            main = f"{passes(result.records, 'main', tier)}/{_valid(result.records, 'main', tier)}"
            if _cached(result.records, "main", tier):
                main += " (cached)"
            branch_cost = _cost(result.records, "branch", tier)
            main_cost = _cost(result.records, "main", tier)
            for value in (branch_cost, main_cost):
                if value is not None:
                    total_cost += value
                    any_cost = True
            cost = f"{_fmt_cost(branch_cost)} / {_fmt_cost(main_cost)}"
            if ladder:
                lowest = result.lowest_tier or "—"
                lines.append(f"| {result.case.id} | {result.case.expect} | {tier} | {branch} | {main} | {cost} | {lowest} | {expected} | {flag} |")
            else:
                lines.append(f"| {result.case.id} | {result.case.expect} | {tier} | {branch} | {main} | {cost} | {flag} |")

    lines += ["", f"**Total cost:** {_fmt_cost(total_cost if any_cost else None)}", ""]
    lines += ["## Failed and void runs", ""]
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
