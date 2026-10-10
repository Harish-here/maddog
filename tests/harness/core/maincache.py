"""Reuse `main`'s run events across invocations. Names no runtime: the
runtime, model, and adapter-source hash it keys on are opaque strings and
bytes handed in by the caller (same pattern as report.py's `runtime` param).

Only `main` runs are ever cached — branch runs always run fresh, because
they are the thing under test.

Stores raw events per run, never a verdict, so a scoring change never
invalidates a cache entry: `score()` runs again on load."""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from harness.core.cases import AgentCase, Case
from harness.core.events import Event

CACHE_DIRNAME = ".main-cache"


def hash_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True)
class CacheKey:
    sha: str            # main's commit SHA
    runtime: str
    model: str           # the model id the tier maps to
    prompt: str           # the case's prompt
    fixture: str          # the case's fixture
    adapter_hash: str     # hash of the adapter source file
    role: str = ""        # agent cases only: the role under test; "" keeps every skill-mode digest unchanged

    def digest(self) -> str:
        parts = [self.sha, self.runtime, self.model, self.prompt, self.fixture, self.adapter_hash]
        if self.role:
            parts.append(self.role)
        return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()


class MainCache:
    """Bound to one run.py invocation: knows main's SHA, the runtime name,
    its tier->model ladder, and the adapter source hash. `fresh=True` makes
    get() always miss and put() always overwrite."""

    def __init__(self, cache_dir: Path, sha: str, runtime: str, model_ladder: dict, adapter_hash: str, fresh: bool = False):
        self.cache_dir = Path(cache_dir)
        self.sha = sha
        self.runtime = runtime
        self.model_ladder = model_ladder
        self.adapter_hash = adapter_hash
        self.fresh = fresh

    def _key(self, case: Case, tier: str) -> CacheKey:
        return CacheKey(self.sha, self.runtime, self.model_ladder[tier], case.prompt, case.fixture, self.adapter_hash,
                        case.expect if isinstance(case, AgentCase) else "")

    def _path(self, case: Case, tier: str) -> Path:
        return self.cache_dir / f"{self._key(case, tier).digest()}.json"

    def get(self, case: Case, tier: str, min_valid: int) -> list[list[Event]] | None:
        """Returns up to `min_valid` cached run event-lists, or None on a miss
        (no file, unreadable file, or fewer than `min_valid` runs stored)."""
        if self.fresh:
            return None
        path = self._path(case, tier)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        runs = data.get("runs", [])
        if len(runs) < min_valid:
            return None
        return [[Event(**e) for e in run["events"]] for run in runs[:min_valid]]

    def put(self, case: Case, tier: str, event_lists: list[list[Event]]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(case, tier)
        meta = {
            "sha": self.sha, "runtime": self.runtime, "model": self.model_ladder[tier],
            "case": case.id, "fixture": case.fixture,
        }
        body = {"meta": meta, "runs": [{"events": [e.to_dict() for e in events]} for events in event_lists]}
        path.write_text(json.dumps(body, indent=2))
