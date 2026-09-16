#!/usr/bin/env python3
"""Fragment check: does every carrying file hold its shared fragments byte-identically?

Usage: fragment-check.py [--source docs/executor-family/constitution.md]

Reads the fragments (## LAWS, ## ROUTE, ## CONTRACT, ## VERIFY) and the
carrier table from the source, then checks each carrier contains each
assigned fragment verbatim (exact bytes, not whitespace-normalized).
Exit 0 iff every check passes. Prints one line per (file, fragment).
"""
import argparse, re, sys

CARRIER_PATH = {
    "advisor-mode": "skills/advisor-mode/SKILL.md",
    "executor-lead": "agents/executor-lead.md",
    "executor-smart": "agents/executor-smart.md",
    "executor-judge": "agents/executor-judge.md",
    "executor-fast": "agents/executor-fast.md",
    "executor-fast-read": "agents/executor-fast-read.md",
}

def fragments(doc):
    out = {}
    for m in re.finditer(r"^## (LAWS|ROUTE|CONTRACT|VERIFY)\n\n(.*?)(?=^## |\Z)", doc, re.S | re.M):
        out[m.group(1)] = m.group(2).strip("\n")
    return out

def carriers(doc):
    out = {}
    for m in re.finditer(r"^\| (LAWS|ROUTE|CONTRACT|VERIFY) \| (.*?) \|$", doc, re.M):
        out[m.group(1)] = [c.strip() for c in m.group(2).split(",")]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="docs/executor-family/constitution.md")
    a = ap.parse_args()
    doc = open(a.source, encoding="utf-8").read()
    frags, carry = fragments(doc), carriers(doc)
    ok = True
    for name in ("LAWS", "ROUTE", "CONTRACT", "VERIFY"):
        if name not in frags:
            print(f"MISSING fragment {name} in {a.source}"); ok = False; continue
        for c in carry.get(name, []):
            path = CARRIER_PATH.get(c)
            if not path:
                print(f"UNKNOWN carrier {c}"); ok = False; continue
            body = open(path, encoding="utf-8").read()
            hit = frags[name] in body
            print(f"{'OK  ' if hit else 'FAIL'} {path}: {name}")
            ok &= hit
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
