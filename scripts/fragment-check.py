#!/usr/bin/env python3
"""Fragment check: does every carrying file hold its shared fragments byte-identically?

Usage: fragment-check.py [--source docs/executor-family/constitution.md]

Reads the fragments (## FAMILY LAWS, ## ROUTE, ## CONTRACT, ## VERIFY) and the
carrier table from the source, then checks each assigned carrier contains
each fragment exactly once, verbatim (exact bytes, not whitespace-
normalized), and that no carrier holds a fragment the table does not assign
it. Exit 0 iff every check passes. Prints one line per (file, fragment).
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CARRIER_PATH = {
    "advisor-mode": "skills/advisor-mode/SKILL.md",
    "executor-lead": "agents/executor-lead.md",
    "executor-smart": "agents/executor-smart.md",
    "executor-judge": "agents/executor-judge.md",
    "executor-fast": "agents/executor-fast.md",
    "executor-fast-read": "agents/executor-fast-read.md",
}

FRAGMENT_NAMES = ("FAMILY LAWS", "ROUTE", "CONTRACT", "VERIFY")

def fragments(doc):
    out = {}
    for m in re.finditer(r"^## (FAMILY LAWS|ROUTE|CONTRACT|VERIFY)\n\n(.*?)(?=^## |\Z)", doc, re.S | re.M):
        out[m.group(1)] = m.group(2).strip("\n")
    return out

def carriers(doc):
    out = {}
    for m in re.finditer(r"^\| (FAMILY LAWS|ROUTE|CONTRACT|VERIFY) \| (.*?) \|$", doc, re.M):
        out[m.group(1)] = [c.strip() for c in m.group(2).split(",")]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="docs/executor-family/constitution.md")
    a = ap.parse_args()
    doc = (ROOT / a.source).read_text(encoding="utf-8")
    frags, carry = fragments(doc), carriers(doc)
    ok = True

    if not carry:
        print(f"FAIL no carrier rows parsed from {a.source}")
        sys.exit(1)

    bodies = {}
    def body_of(carrier):
        if carrier not in bodies:
            rel = CARRIER_PATH[carrier]
            bodies[carrier] = (rel, (ROOT / rel).read_text(encoding="utf-8"))
        return bodies[carrier]

    for name in FRAGMENT_NAMES:
        if name not in frags:
            print(f"MISSING fragment {name} in {a.source}"); ok = False; continue
        for c in carry.get(name, []):
            if c not in CARRIER_PATH:
                print(f"UNKNOWN carrier {c}"); ok = False; continue
            path, body = body_of(c)
            count = body.count(frags[name])
            hit = count == 1
            tag = 'OK  ' if hit else 'FAIL'
            detail = '' if hit else f" ({count} occurrences, expected 1)"
            print(f"{tag} {path}: {name}{detail}")
            ok &= hit

    for c in CARRIER_PATH:
        path, body = body_of(c)
        for name in FRAGMENT_NAMES:
            if name not in frags:
                continue
            if c in carry.get(name, []):
                continue
            if frags[name] in body:
                print(f"FAIL {path}: contains unassigned fragment {name}")
                ok = False

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
