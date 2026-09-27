import sys
from pathlib import Path

# Make `harness` importable the same way run.py sees it: tests/ on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
