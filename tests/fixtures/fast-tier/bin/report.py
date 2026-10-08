#!/usr/bin/env python3
"""Print one report line: python3 bin/report.py --item N"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stockroom import importer, report, store  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--item", type=int, required=True)
    args = parser.parse_args()
    importer.load_items()
    print(report.render_line(store.get_item(args.item)))


if __name__ == "__main__":
    main()
