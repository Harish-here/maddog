# maddog Design System

Version: 0.2.0

## 1. Purpose and scope

This document governs maddog's visual identity: logo, colour,
typography, text colour, and the words on user-facing surfaces —
README, CHANGELOG, any prose a person reads rather than an agent
loads. Out of scope: code architecture, agent routing, and
conversational sentence rules — see `PHILOSOPHY.md` and the
`plain-english` skill.

## 2. Principles

| # | Principle | Traced to (PHILOSOPHY.md) |
|---|---|---|
| 1 | Black and white is the constant | Harness-neutral core — renders the same everywhere |
| 2 | Colour and shape are named, never memorised | Tokens are the new currency — every value is a token |
| 3 | Colour is the exception | Spend your attention on what matters — a colourful page is a wrong page |
| 4 | The rule outranks the drawing | Architect the integrity — valid because it followed section 8, not because it looks right |
| 5 | Cheapest mark that reads | Intelligence is a budget — a 32×32 grid reads at icon size, no per-resolution tuning |

**Tone standard.** Every visual surface reads in one line as: neat,
minimal, strong, detail-oriented.

## 3. Logo

**Construction.** 32×32 pixel grid, one `<rect>` per pixel,
`shape-rendering="crispEdges"`. Cartoon dog head, curious look, tongue
out: `--md-ink` outline, `--md-paper` body, `--md-grey` shade,
`--md-tongue` tongue, one `--md-amber` spark. Fixed: tilted head, one
ear up one down, big eyes with a 1px catch-light, raised brow — pixel
placement is `assets/logo/maddog-head.svg`, once locked.

**Dark ground.** No inversion: outline stays `--md-ink`, body
`--md-paper`, tongue becomes `--md-tongue-dark`. The dark icon tile
carries `--md-paper-dark`; the mark does not.

**Sizing.** Clear space: one grid cell per side (4px at 128px render).
16px floor; below it, a two-tone ink-on-paper silhouette. Lockup
(icon + wordmark) floor: 120px; below that, icon alone.

**Do:** named tokens only; one spark; tongue always on; dark tile for
icon-only contexts on dark ground.

**Don't:** rotate, skew, mirror, recolour the outline, add a shadow or
gradient, or invert on dark ground.

## 4. Colour

| Token | Value | Role |
|---|---|---|
| `--md-ink` | `#1A1A18` | outline; text (light) |
| `--md-paper` | `#FFFFFF` | logo body; light ground |
| `--md-paper-dark` | `#16171A` | dark ground |
| `--md-grey` | `#D9D8D2` | shade; rules/borders (light) |
| `--md-grey-dark` | `#3A3B3F` | rules/borders (dark) |
| `--md-amber` | `#F2B441` | attention: spark, warnings — not light-text |
| `--md-amber-ink` | `#8A5E12` | amber, text-safe (light) |
| `--md-blue` | `#1F4B99` | links, active states (light) |
| `--md-blue-light` | `#7FB0F2` | links (dark) |
| `--md-tongue` | `#F28BA8` | tongue (light) |
| `--md-tongue-dark` | `#C9607F` | tongue (dark) |

**Rule.** Amber and blue together cover no more than a small fraction
of any surface; a colourful page is wrong. No token may approximate a
sibling or vendor hue: Claude orange `#D97757`, Copilot purple
`#6E40C9`, OpenAI green `#10A37F`, Jobbunny purple `#7B5EA7`.

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

**Pixel wordmark.** Only in the logo lockup, a README masthead, or a
splash/hero graphic — never in running text, headings, table headers,
error text, or below its 16px floor (section 3).

## 6. Text colour and contrast

`--md-ground` pairs the page background per theme: `--md-paper` on
light, `--md-paper-dark` on dark.

| Token | Ground | Value | Ratio |
|---|---|---|---|
| primary | light | `#1A1A18` | 17.43:1 |
| secondary | light | `#4A4A46` | 8.90:1 |
| muted | light | `#6E6E68` | 5.13:1 |
| link (`--md-blue`) | light | `#1F4B99` | 8.32:1 |
| amber-ink | light | `#8A5E12` | 5.69:1 |
| primary | dark | `#F2F1EC` | 15.85:1 |
| secondary | dark | `#C8C6BE` | 10.48:1 |
| muted | dark | `#9C9A92` | 6.36:1 |
| link (`--md-blue-light`) | dark | `#7FB0F2` | 8.02:1 |
| amber | dark | `#F2B441` | 9.71:1 |

All ten rows pass AA (≥4.5:1). Raw `--md-amber` on `--md-paper`
measures 1.85:1 and fails — hence `--md-amber-ink`.

## 7. Words

- **Product name.** "maddog" always lowercase, sentence start too —
  except the pixel wordmark ("MADDOG").
- **Agent names.** Verbatim as `agents/*.md` — lowercase, hyphenated,
  code-styled (`executor-smart`), never title-cased.
- **Skill names.** Namespaced (`/maddog:plain-english`) to invoke;
  bare as a concept.
- **Sentence-level rules.** Governed by the `plain-english` skill.
- **Tone by surface.** README: direct, one line per shipped thing.
  CHANGELOG: terse, dated, links its verdict or PR. Error/refusal
  text: reason and boundary, no apology.

## 8. Family illustrations

32×32 grid. Fixed: silhouette, `--md-ink` outline, `--md-paper` body,
`--md-grey` shade, `--md-tongue` — every member keeps the tongue.
Varies, exactly one: a prop, `--md-ink` outline, filled with either
`--md-amber` or `--md-blue`, inside a fixed prop zone. Nothing else
moves.

## 9. File layout

- `assets/logo/maddog-head.svg`, `maddog-icon.svg`,
  `maddog-wordmark.svg`; `assets/family/<agent-name>.svg`.
- `viewBox="0 0 32 32"`, one `<rect>` per pixel, `shape-rendering=
  "crispEdges"`, `role="img"`, plain-sentence `aria-label`, fills as
  `fill="var(--md-ink)"` — a palette change is a token swap.
- Two copies: token-based source (inlined) and static-hex for
  `<img>` embeds.

## 10. Versioning

Own semantic version, independent of the plugin's release (`2.12.x`).

- **Breaking (major):** logo construction change, a token
  rename/removal, a typeface change.
- **Non-breaking (minor):** a new family member, a new text-colour
  token, an extended type scale.
- **Patch:** wording or contrast-value corrections, no rule change.

The version line bumps with the document. 1.0.0 is cut when
`assets/logo/maddog-head.svg` is locked.

**Reserved for later** — a future minor or major may add, without
breaking 1.x:

- Motion (hover/loading states for the mark)
- A data-viz palette
- A component library (buttons, cards, form controls)
- Additional family members beyond the current lineups
- Print and social sizing (favicons, OG images, print marks)

Nothing else about these appears elsewhere in this document.
