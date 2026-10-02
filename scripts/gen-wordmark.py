#!/usr/bin/env python3
# Draws assets/wordmark.txt as SVG: assets/wordmark-dark.svg, assets/wordmark-light.svg, assets/icon.svg.
# Colours are the DESIGN.md section 4 and 6 tokens. Standard library only.
# Run from anywhere: python3 scripts/gen-wordmark.py

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# One text cell is drawn 32 wide and 64 tall (a terminal cell is about 1:2).
CELL_W = 32
CELL_H = 64

# Wordmark rows in wordmark.txt: 0-5 art, 6 blank, 7 rule, 8 subtitle, 9 rule.
ART_ROWS = range(0, 6)
RULE_ROWS = (7, 9)
SUBTITLE_ROW = 8
COLUMNS = 53

# One cell of clear space around the wordmark.
MARGIN_X = CELL_W
MARGIN_Y = CELL_H

# Colours by role. Each value is a DESIGN.md token.
THEMES = {
    "dark": {
        "face": "#F2F1EC",    # --md-text-primary (dark)
        "shadow": "#3A3B3F",  # --md-grey-dark
        "text": "#F2F1EC",    # --md-text-primary (dark): rules and subtitle
        "amp": "#F2B441",     # --md-amber
    },
    "light": {
        "face": "#1A1A18",    # --md-ink
        "shadow": "#D9D8D2",  # --md-grey
        "text": "#1A1A18",    # --md-ink: rules and subtitle
        "amp": "#8A5E12",     # --md-amber-ink
    },
}
ICON_GROUND = "#16171A"  # --md-paper-dark
ICON_RING = "#3A3B3F"    # --md-grey-dark
ICON_FACE = "#F2F1EC"    # --md-text-primary (dark)

# Subtitle letters as stroked lines in a 22 x 40 box, with a 6px stroke.
LETTERS = {
    "S": "M19 3H3V20H19V37H3",
    "K": "M3 3V37M19 3L5 20M5 20L19 37",
    "I": "M3 3H19M11 3V37M3 37H19",
    "L": "M3 3V37H19",
    "A": "M3 37V3H19V37M3 20H19",
    "G": "M19 3H3V37H19V20H11",
    "E": "M19 3H3V37H19M3 20H15",
    "N": "M3 37V3L19 37V3",
    "T": "M3 3H19M11 3V37",
    "&": "M19 37L4 15V3H14V15L3 28V37H13L19 26",
}


def face_path(rows, columns):
    """Every run of full blocks (█) as one rectangle, joined into a single path.

    One path (not one rect per run) avoids hairline seams between rows.
    """
    parts = []
    for row, line in enumerate(rows):
        col = 0
        while col < min(len(line), columns):
            if line[col] != "█":
                col += 1
                continue
            start = col
            while col < min(len(line), columns) and line[col] == "█":
                col += 1
            width = (col - start) * CELL_W
            parts.append(f"M{start * CELL_W} {row * CELL_H}h{width}v{CELL_H}h-{width}z")
    return "".join(parts)


def shadow_path(rows, columns):
    """The box-drawing shadow as thin centre-line strokes, one segment per character."""
    parts = []
    for row, line in enumerate(rows):
        for col, ch in enumerate(line[:columns]):
            x = col * CELL_W
            y = row * CELL_H
            cx = x + CELL_W // 2
            cy = y + CELL_H // 2
            right = x + CELL_W
            bottom = y + CELL_H
            segments = {
                "╗": f"M{x} {cy}H{cx}V{bottom}",
                "╔": f"M{right} {cy}H{cx}V{bottom}",
                "╝": f"M{x} {cy}H{cx}V{y}",
                "╚": f"M{right} {cy}H{cx}V{y}",
                "═": f"M{x} {cy}H{right}",
                "║": f"M{cx} {y}V{bottom}",
            }
            if ch in segments:
                parts.append(segments[ch])
    return "".join(parts)


def rule_path():
    """The two ═ rules as one full-width line each."""
    return "".join(
        f"M0 {row * CELL_H + CELL_H // 2}H{COLUMNS * CELL_W}" for row in RULE_ROWS
    )


def subtitle_paths(line):
    """Subtitle letters as stroked paths. Returns (plain letters, the ampersand)."""
    plain = []
    amp = []
    for col, ch in enumerate(line):
        if ch == " ":
            continue
        x = col * CELL_W + 5
        y = SUBTITLE_ROW * CELL_H + 12
        path = f'<path transform="translate({x} {y})" d="{LETTERS[ch]}"/>'
        (amp if ch == "&" else plain).append(path)
    return "".join(plain), "".join(amp)


def wordmark_svg(lines, colours):
    art = lines[:6]
    plain, amp = subtitle_paths(lines[SUBTITLE_ROW])
    height = len(lines) * CELL_H
    view = f"{-MARGIN_X} {-MARGIN_Y} {COLUMNS * CELL_W + 2 * MARGIN_X} {height + 2 * MARGIN_Y}"
    stroke = 'fill="none" stroke="{}" stroke-width="{}"'
    letters = 'fill="none" stroke="{}" stroke-width="6" stroke-linejoin="miter"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}">\n'
        f'<path d="{shadow_path(art, COLUMNS)}" {stroke.format(colours["shadow"], 8)}/>\n'
        f'<path fill="{colours["face"]}" d="{face_path(art, COLUMNS)}"/>\n'
        f'<path d="{rule_path()}" {stroke.format(colours["text"], 8)}/>\n'
        f'<g {letters.format(colours["text"])}>{plain}</g>\n'
        f'<g {letters.format(colours["amp"])}>{amp}</g>\n'
        "</svg>\n"
    )


def icon_svg(lines):
    """The first M (11 columns, 6 rows) on a dark rounded square with a grey ring."""
    cols = 11
    art = lines[:6]
    glyph_w = cols * CELL_W
    glyph_h = 6 * CELL_H
    ox = (512 - glyph_w) // 2
    oy = (512 - glyph_h) // 2
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n'
        f'<rect width="512" height="512" rx="96" fill="{ICON_GROUND}"/>\n'
        f'<rect x="8" y="8" width="496" height="496" rx="88" fill="none" stroke="{ICON_RING}" stroke-width="8"/>\n'
        f'<g transform="translate({ox} {oy})">\n'
        f'<path d="{shadow_path(art, cols)}" fill="none" stroke="{ICON_RING}" stroke-width="8"/>\n'
        f'<path fill="{ICON_FACE}" d="{face_path(art, cols)}"/>\n'
        "</g>\n"
        "</svg>\n"
    )


def main():
    lines = (ASSETS / "wordmark.txt").read_text(encoding="utf-8").split("\n")[:10]
    for name, colours in THEMES.items():
        (ASSETS / f"wordmark-{name}.svg").write_text(wordmark_svg(lines, colours), encoding="utf-8")
    (ASSETS / "icon.svg").write_text(icon_svg(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
