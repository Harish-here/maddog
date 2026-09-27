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


class Adapter(Protocol):
    def run(self, case, plugin_path: Path, workdir: Path, tier: str) -> list[Event]:
        """Run one case once and return its ordered event log."""
        ...
