"""Load case files and the ladder config. Names no runtime."""
from dataclasses import dataclass
from pathlib import Path

import yaml

ROLES = ("Fast-Read", "Fast", "Smart", "Judge", "Lead")
TIERS = ("low", "mid", "high")
PRESSURES = ("none", "user", "decision")

TESTS_DIR = Path(__file__).resolve().parents[2]
LADDERS_FILE = TESTS_DIR / "harness" / "runtimes" / "ladders.yaml"


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    expect: str
    pressure: str
    skill: str | None  # None means a plain session with no skill loaded
    fixture: str
    expected_tier: str | None = None  # set only when the maintainer raised it
    why: str | None = None            # required with expected_tier


def load_cases(path: Path) -> list[Case]:
    data = yaml.safe_load(Path(path).read_text())
    skill = data.get("skill")
    fixture = data.get("fixture")
    if not fixture:
        raise ValueError(f"{path}: missing 'fixture'")
    file_tier = data.get("expected_tier")
    file_why = data.get("why")
    if file_tier is not None and file_tier not in TIERS:
        raise ValueError(f"{path}: unknown tier {file_tier!r}")
    if file_tier is not None and not file_why:
        raise ValueError(f"{path}: expected_tier needs a 'why'")
    if file_why and not file_tier:
        raise ValueError(f"{path}: 'why' needs an 'expected_tier'")
    cases = []
    seen = set()
    for raw in data.get("cases", []):
        for field in ("id", "prompt", "expect", "pressure"):
            if field not in raw:
                raise ValueError(f"{path}: a case is missing '{field}'")
        if raw["expect"] not in ROLES:
            raise ValueError(f"{path}: case {raw['id']}: unknown role {raw['expect']!r}")
        if raw["pressure"] not in PRESSURES:
            raise ValueError(f"{path}: case {raw['id']}: unknown pressure {raw['pressure']!r}")
        if raw["id"] in seen:
            raise ValueError(f"{path}: duplicate case id {raw['id']!r}")
        seen.add(raw["id"])
        tier = raw.get("expected_tier")
        why = raw.get("why")
        if tier is not None and tier not in TIERS:
            raise ValueError(f"{path}: case {raw['id']}: unknown tier {tier!r}")
        if tier is not None and not why:
            raise ValueError(f"{path}: case {raw['id']}: expected_tier needs a 'why'")
        if tier is None:
            # No case-level override: inherit the file-level pair, if any.
            tier, why = file_tier, file_why
        cases.append(Case(raw["id"], raw["prompt"], raw["expect"], raw["pressure"], skill, fixture, tier, why))
    if not cases:
        raise ValueError(f"{path}: no cases")
    return cases


def load_ladders(path: Path = LADDERS_FILE) -> dict:
    return yaml.safe_load(Path(path).read_text())


def expected_tier(case: Case, ladders: dict) -> str:
    if case.expected_tier:
        return case.expected_tier
    return ladders["expected_tier"][case.pressure]
