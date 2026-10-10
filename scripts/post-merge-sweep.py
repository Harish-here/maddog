#!/usr/bin/env python3
"""Post-merge sweep: stray files, orphans, and README drift against disk.

Usage: post-merge-sweep.py

Checks the committed tree:
  1. README catalog names every agent and skill on disk, and names nothing absent.
  2. No relative markdown link in a tracked .md file points at a missing path.
  3. Every file under scripts/ and docs/ is referenced by some other tracked file.
  4. No tracked junk (*.bak, *.orig, *.tmp, *.swp, .DS_Store).
Exit 0 iff every check passes. Prints one line per finding.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JUNK = re.compile(r"(\.(bak|orig|tmp|swp|rej)$)|(^|/)\.DS_Store$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if (ROOT / p).is_file()]


def readme_catalog(files):
    findings = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    named = set(re.findall(r"^\| `([a-z][a-z0-9-]*)` \|", readme, re.M))
    named |= set(re.findall(r"^#{2,3} ([a-z][a-z0-9-]*)$", readme, re.M))
    on_disk = {Path(p).stem for p in files if re.fullmatch(r"agents/[^/]+\.md", p)}
    on_disk |= {p.split("/")[1] for p in files if re.fullmatch(r"skills/[^/]+/SKILL\.md", p)}
    mentioned = named | set(re.findall(r"`([a-z][a-z0-9-]*)`", readme))
    for n in sorted(on_disk - mentioned):
        findings.append(f"README.md does not list {n}")
    for n in sorted(named - on_disk):
        findings.append(f"README.md lists {n} but no agent or skill has that name")
    return findings


def broken_links(files):
    findings = []
    for p in files:
        if not p.endswith(".md"):
            continue
        text = (ROOT / p).read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        text = re.sub(r"^(?: {4}|\t).*$", "", text, flags=re.M)
        for target in LINK.findall(text):
            if re.match(r"(https?:|mailto:|#)", target):
                continue
            path = target.split("#")[0]
            if path and not (ROOT / p).parent.joinpath(path).resolve().exists():
                findings.append(f"{p} links to missing {target}")
    return findings


def orphans(files):
    findings = []
    bodies = {p: (ROOT / p).read_text(encoding="utf-8", errors="replace") for p in files if not p.endswith((".svg", ".png"))}
    for p in files:
        if not (p.startswith("scripts/") or p.startswith("docs/")):
            continue
        name = Path(p).name
        if not any(name in body for other, body in bodies.items() if other != p):
            findings.append(f"{p} is referenced by no other tracked file")
    return findings


def junk(files):
    return [f"{p} is junk" for p in files if JUNK.search(p)]


def main():
    files = tracked()
    findings = readme_catalog(files) + broken_links(files) + orphans(files) + junk(files)
    for f in findings:
        print(f"FAIL {f}")
    if not findings:
        print("OK sweep clean")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
