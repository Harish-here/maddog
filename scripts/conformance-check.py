#!/usr/bin/env python3
"""Conformance check: is an agent body a faithful rendering of the mechanical-work schema?

Usage: conformance-check.py --hand read|write --body agents/<file>.md [--schema docs/executor-family/mechanical-work.md]

Checks, per hand, that every LOCKED item of the schema appears verbatim (whitespace-normalized) in the body:
  - the LAW line (name + sentence) of every row II.5's first table gives this hand (R5 is carried by II.4)
  - X1, this hand's X2, X3
  - II.4 stance paragraph, stop list, cord paragraph
  - II.3 envelope field names in order, and the `partial` rule
Also checks: nothing after the NOTES: line; frontmatter tools: line equals the hand's tool set;
no schema row ids (R1..R8) or section marks (§) leak into the body.
Exit 0 iff every check passes. Prints one line per item.
"""
import argparse, re, sys

TOOLS = {"read": "Read, Glob, Grep", "write": "Read, Write, Edit, Bash, Glob, Grep"}
FIELDS = ["STATUS:", "BLOCKED-ON:", "RESULT:", "NOT DONE:", "NOTES:"]
PARTIAL_RULE = '(partial whenever NOT DONE is not "none")'

def norm(s):
    return re.sub(r"\s+", " ", s).strip()

def section(doc, start, end):
    i = doc.index(start)
    j = doc.index(end, i) if end else len(doc)
    return doc[i:j]

def rows_for_hand(doc, hand):
    s7 = section(doc, "## II.5", "## II.6")
    want = "Read hand renders" if hand == "read" else "Write hand renders"
    col = None
    rows = []
    for line in s7.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if col is None:
            if cells[:1] == ["Row"] and want in cells:
                col = cells.index(want)
            continue
        m = re.match(r"R\d$", cells[0]) if cells else None
        if not m or len(cells) <= col:
            continue
        cell = cells[col]
        if cell and cell != "—" and cells[0] != "R5":
            rows.append(cells[0])
    if col is None:
        raise SystemExit("schema: II.5 table header does not name '%s'" % want)
    return rows

def law_line(doc, rid, hand):
    i = doc.index(f"### {rid} ")
    ends = [x for x in (doc.find("\n### ", i + 1), doc.find("\n## ", i + 1)) if x != -1]
    block = doc[i:min(ends)] if ends else doc[i:]
    for tag in (f"LAW ({hand} hand): ", "LAW: "):
        m = re.search(re.escape(tag) + r"(.*?)\n(?=Source|Sources|LAW|Residue)", block, re.S)
        if m:
            return m.group(1)
    raise SystemExit(f"schema: no LAW line for {rid}")

def cross_laws(doc, hand):
    """Each X law is required as NAME — sentence (the hand qualifier is schema-only)."""
    s4 = section(doc, "## II.2", "## II.3")
    out = {}
    m = re.search(r"X1 ([^—\n]+?) — (.*?)(?=\n\n)", s4, re.S); out["X1"] = m.group(1).strip() + " — " + m.group(2)
    m = re.search(r"X2 ([^—\n(]+?) \(" + hand + r" hand\) — (.*?)(?=\n\n)", s4, re.S); out["X2"] = m.group(1).strip() + " — " + m.group(2)
    m = re.search(r"X3 ([^—\n]+?) — (.*?)(?=\n\n)", s4, re.S); out["X3"] = m.group(1).strip() + " — " + m.group(2)
    return out

def stance_blocks(doc):
    s6 = section(doc, "## II.4", "## II.5")
    st = re.search(r"Stance: (.*?)(?=\n\n)", s6, re.S).group(1)
    stops = re.search(r"(Return `blocked`, naming the gap.*?)(?=\n\n)", s6, re.S).group(1)
    cord = re.search(r"(THE ANDON CORD — .*?)(?=\n\n|\n## |\Z)", s6, re.S).group(1)
    comp = re.search(r"Composition: (.*?)(?=\n\n)", s6, re.S).group(1)
    return {"II.4 stance": st, "II.4 composition": comp, "II.4 stop list": stops, "II.4 cord": cord}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True, choices=["read", "write"])
    ap.add_argument("--body", required=True)
    ap.add_argument("--schema", default="docs/executor-family/mechanical-work.md")
    a = ap.parse_args()
    doc = open(a.schema).read()
    raw = open(a.body).read()
    fm, body = raw.split("---", 2)[1:3] if raw.startswith("---") else ("", raw)
    b = norm(body)
    items = {}
    for rid in rows_for_hand(doc, a.hand):
        items[f"{rid} LAW"] = law_line(doc, rid, a.hand)
    items.update(cross_laws(doc, a.hand))
    items.update(stance_blocks(doc))
    ok = True
    for k, v in items.items():
        hit = norm(v) in b
        ok &= hit
        print(f"{'PRESENT' if hit else 'MISSING':8s} {k}")
    # envelope order
    pos = []
    for f in FIELDS:
        m = re.search(r"^[ \t]*" + re.escape(f), body, re.M)
        pos.append(m.start() if m else -1)
    env_ok = all(p >= 0 for p in pos) and pos == sorted(pos)
    # whole envelope block, verbatim (whitespace-normalized), from II.3's code block
    s5 = section(doc, "## II.3", "## II.4")
    env_lines = [l.strip() for l in s5.splitlines() if l.startswith("    ") and l.strip()]
    env_block_ok = norm(" ".join(env_lines)) in b
    ok &= env_block_ok
    print(f"{'PRESENT' if env_block_ok else 'MISSING':8s} II.3 envelope block verbatim")
    ok &= env_ok
    print(f"{'PRESENT' if env_ok else 'MISSING':8s} II.3 envelope fields in order")
    pr = norm(PARTIAL_RULE) in b
    ok &= pr
    print(f"{'PRESENT' if pr else 'MISSING':8s} II.3 partial rule")
    mn = list(re.finditer(r"^[ \t]*NOTES:", body, re.M))
    tail = body[mn[-1].start():].split("\n", 1)[1] if mn else "x"
    tail_ok = tail.strip() == ""
    ok &= tail_ok
    print(f"{'PASS' if tail_ok else 'FAIL':8s} nothing after NOTES line")
    dm = re.search(r"^description:\s*>?\s*\n((?:[ \t]+.*\n?)+)", fm, re.M)
    desc = dm.group(1) if dm else ""
    desc_ok = len(desc.split()) >= 30 and "(unchanged" not in desc
    ok &= desc_ok
    print(f"{'PASS' if desc_ok else 'FAIL':8s} frontmatter description present (>=30 words, no placeholder)")
    tm = re.search(r"^tools:\s*(.*)$", fm, re.M)
    tools_ok = bool(tm) and norm(tm.group(1)) == TOOLS[a.hand]
    ok &= tools_ok
    print(f"{'PASS' if tools_ok else 'FAIL':8s} tools line == {TOOLS[a.hand]!r}")
    leak = re.findall(r"\bR[1-8]\b|§", body)
    ok &= not leak
    print(f"{'PASS' if not leak else 'FAIL':8s} no schema ids in body" + (f" (found {sorted(set(leak))})" if leak else ""))
    print("RESULT:", "CONFORMS" if ok else "NONCONFORMING")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
