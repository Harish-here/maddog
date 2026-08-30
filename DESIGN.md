# maddog Design System

Version: 1.0.0

## 1. Purpose and scope

This document governs maddog's visual identity: wordmark, colour,
typography, text colour, and the words on user-facing surfaces. That
covers README, CHANGELOG, and any prose a person reads rather than
an agent loads. Out of scope: code architecture, agent routing, and
conversational sentence rules — see `PHILOSOPHY.md` and the
`plain-english` skill.

## 2. Principles

| # | Principle | Traced to (PHILOSOPHY.md) |
|---|---|---|
| 1 | Black and white is the constant | Harness-neutral core — renders the same everywhere |
| 2 | Colour and shape are named, never memorised | Tokens are the new currency — every value is a token |
| 3 | Colour is the exception | Spend your attention on what matters — a colourful page is a wrong page |
| 4 | The rule outranks the drawing | Architect the integrity. Don't just instruct the agent. |
| 5 | Cheapest mark that reads | Intelligence is a budget — the mark is text; it ships wherever text ships |

**Tone standard.** Every visual surface reads in one line as: neat,
minimal, strong, detail-oriented.

## 3. Wordmark

The mark is MADDOG set in the figlet font `ansi_shadow`, above a
subtitle band. The band opens with a full-width double rule
(`═`, U+2550, 53 columns). It centres "SKILLS & AGENTS" in
letterspaced capitals on the art width, then closes with a second
rule. The subtitle's written form is "Skills & Agents"; the capitals are display-only. Lockup: 53×10. Canonical file: `assets/wordmark.txt`. ASCII
fallback: `assets/wordmark-ascii.txt` (figlet `slant`, art 43
columns, `=` rules), 43×10 — used when Unicode is unsupported or
width is 43–52 columns.

It ships as a fenced code block in README and as plain text in any
terminal splash. It is never re-typeset in another font, and never
rendered as an image where text can go.

**Colour.** `--md-ink` on `--md-paper`, or `--md-text-primary` on
`--md-paper-dark`. No colour inside the art. The ampersand in the
subtitle may take `--md-amber-ink` on light or `--md-amber` on dark —
the only accent.

**Sizing.** The art is fixed-size text, so "minimum size" is replaced
by a width rule: never wrap. Below 43 columns, use the subtitle line
alone in plain text — "maddog — Skills & Agents". Clear space: one
blank line above and below.

**Do:** ship the canonical file byte-for-byte; use the ASCII fallback
when Unicode is unsupported or width is 43–52 columns, subtitle alone
below 43.

**Don't:** re-typeset in another font; render as an image; add colour
inside the glyphs.

## 4. Colour

| Token | Value | Role |
|---|---|---|
| `--md-ink` | `#1A1A18` | text (light) |
| `--md-paper` | `#FFFFFF` | light ground |
| `--md-paper-dark` | `#16171A` | dark ground |
| `--md-grey` | `#D9D8D2` | shade; rules/borders (light) |
| `--md-grey-dark` | `#3A3B3F` | rules/borders (dark) |
| `--md-amber` | `#F2B441` | attention: warnings — not light-text |
| `--md-amber-ink` | `#8A5E12` | amber, text-safe (light) |
| `--md-blue` | `#1F4B99` | links, active states (light) |
| `--md-blue-light` | `#7FB0F2` | links (dark) |

Text-on-ground tokens (`--md-text-*`) are defined in section 6.

**Rule.** Amber and blue together cover no more than a small fraction
of any surface; a colourful page is wrong. No token may approximate a
sibling or vendor hue: Claude orange `#D97757`, Copilot purple
`#6E40C9`, OpenAI green `#10A37F`.

## 5. Typography

| Use | Typeface | Fallback stack |
|---|---|---|
| UI and docs prose | IBM Plex Sans | `-apple-system, "Segoe UI", Helvetica, Arial, sans-serif` |
| Code | IBM Plex Mono | `ui-monospace, SFMono-Regular, "Cascadia Code", Consolas, monospace` |

Both SIL Open Font License, on Google Fonts — one licence, one system.

**Type scale**

| Step | Name | px | rem | Use |
|---|---|---|---|---|
| 1 | Body | 16 | 1rem | paragraph text |
| 2 | Small | 14 | 0.875rem | captions, meta, inline code |
| 3 | Subhead | 20 | 1.25rem | h3 |
| 4 | Heading | 28 | 1.75rem | h2 |
| 5 | Display | 40 | 2.5rem | h1, hero |

**Wordmark.** Only in the wordmark lockup, a README masthead, or a
splash/hero graphic. Never in running text, headings, table headers,
error text, or below 43 columns (section 3).

## 6. Text colour and contrast

`--md-ground` is the page-ground pair: `--md-paper` on light,
`--md-paper-dark` on dark. Each row below names the text token used
against it.

| Token | Ground | Value | Ratio |
|---|---|---|---|
| `--md-text-primary` | light | `#1A1A18` | 17.43:1 |
| `--md-text-secondary` | light | `#4A4A46` | 8.90:1 |
| `--md-text-muted` | light | `#6E6E68` | 5.13:1 |
| `--md-text-link` | light | `#1F4B99` | 8.32:1 |
| `--md-text-accent-on-ground` | light | `#8A5E12` | 5.69:1 |
| `--md-text-primary` | dark | `#F2F1EC` | 15.85:1 |
| `--md-text-secondary` | dark | `#C8C6BE` | 10.48:1 |
| `--md-text-muted` | dark | `#9C9A92` | 6.36:1 |
| `--md-text-link` | dark | `#7FB0F2` | 8.02:1 |
| `--md-text-accent-on-ground` | dark | `#F2B441` | 9.71:1 |

All ten rows pass AA (≥4.5:1). Raw `--md-amber` on `--md-paper`
measures 1.85:1 and fails — hence `--md-amber-ink`.

## 7. Words

- **Product name.** "maddog" always lowercase, sentence start too —
  except the ansi_shadow wordmark ("MADDOG"); the ASCII fallback
  stays lowercase.
- **Agent names.** Verbatim as `agents/*.md` — lowercase, hyphenated,
  code-styled (`executor-smart`), never title-cased.
- **Skill names.** Namespaced (`/maddog:plain-english`) to invoke;
  bare as a concept.
- **Sentence-level rules.** Governed by the `plain-english` skill.
- **Tone by surface.** README: direct, one line per shipped thing.
  CHANGELOG: terse, dated, links its verdict or PR. Error/refusal
  text: reason and boundary, no apology.

## 8. Family illustrations

Family illustrations are deferred. When they return, they are a
separate asset class from the wordmark, and get their own rule under
a minor version.

## 9. File layout

- `assets/wordmark.txt`, `assets/wordmark-ascii.txt`.
- Family assets: reserved.
- `assets/` holds the wordmark files and nothing else at 1.0.0.

## 10. Versioning

Own semantic version, independent of the plugin's release (`2.x`).

- **Breaking (major):** wordmark construction change, a token
  rename/removal, a typeface change, or a picture mark if one is
  ever adopted.
- **Non-breaking (minor):** a new family member, a new text-colour
  token, an extended type scale.
- **Patch:** wording or contrast-value corrections, no rule change.

The version line bumps with the document. 1.0.0 is cut with the
wordmark lock.

**Reserved for later** — a future minor or major may add, without
breaking 1.x:

- Motion (hover/loading states for the mark)
- A data-viz palette
- A component library (buttons, cards, form controls)
- Additional family members
- Print and social sizing (favicons, OG images, print marks)
</content>
