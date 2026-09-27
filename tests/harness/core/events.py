"""The six kinds of event every run is turned into. Names no runtime."""
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Protocol

KINDS = ("handoff", "write", "read", "command", "skill_load", "refused")


@dataclass(frozen=True)
class Event:
    kind: str
    detail: str = ""  # handoff: the role; otherwise the tool, path, or command

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"unknown event kind: {self.kind!r}")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RunOutcome:
    """What one adapter run produces: the event log plus plain cost fields.
    Runtime-specific parsing (SDK types, usage dict shapes) stays in the
    adapter; core only ever sees these plain fields. cost_usd and usage are
    None when the runtime could not report them — never 0."""
    events: list[Event]
    cost_usd: float | None = None
    usage: dict | None = None  # keys: input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens


class Adapter(Protocol):
    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> RunOutcome:
        """Run one case once and return its outcome (event log, cost, usage)."""
        ...
