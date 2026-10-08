"""Read config/settings.toml."""
import tomllib
from pathlib import Path

_FILE = Path(__file__).resolve().parents[2] / "config" / "settings.toml"


def get(section: str, key: str, default=None):
    with open(_FILE, "rb") as f:
        data = tomllib.load(f)
    return data.get(section, {}).get(key, default)
