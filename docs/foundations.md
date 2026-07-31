# Foundations

## The idea

Warm paper, wabi-sabi minimalism. A page should read like a well-set book: one
quiet column of serif text, structure from whitespace and hairlines rather than
cards and boxes, and a single accent used sparingly.

Three rules follow from that, and most decisions in the stylesheet are one of
them applied:

**Two voices.** A book serif for everything *written* — post bodies, titles,
author names. Small tracked-out capitals in a sans for everything that is
*interface* — nav, meta, labels, buttons. Which face a thing is set in tells you
what kind of thing it is. The account menu's "theme" caption is serif italic for
exactly that reason: it cannot be mistaken for a row you can press.

**Structure from absence.** Prefer whitespace and a hairline over a border, a
fill or a shadow. Post listings are separated by a single rule; there are no
cards. Shadows appear only where something genuinely floats above the page.

**Quiet motion.** One duration, one easing, applied to colour and opacity only —
never to position or size. Nothing bounces, and everything collapses under
`prefers-reduced-motion`.

## Naming convention

Tokens are grouped by the CSS property family they feed, following the
namespacing [Tailwind v4](https://tailwindcss.com/docs/theme) settled on:

| Namespace | Holds | Example |
| --------- | ----- | ------- |
| `--color-*` | every colour, including both palette halves | `--color-ink-subtle` |
| `--font-*` | font families | `--font-serif` |
| `--text-*` | font sizes | `--text-heading` |
| `--tracking-*` | letter-spacing | `--tracking-label` |
| `--spacing-*` | padding, margin, gap | `--spacing-4` |
| `--radius-*` | border radius | `--radius-sm` |
| `--shadow-*` | box shadows | `--shadow-panel` |
| `--container-*` | max-widths | `--container-prose` |
| `--duration-*`, `--ease-*` | motion | `--duration-quiet` |

The point is that a name tells you where it may be used, and a new value has an
obvious home.

Two deliberate departures from Tailwind's defaults:

- **Names inside a namespace are semantic, not positional.** Tailwind ships
  `--text-xs` through `--text-4xl`; this uses `--text-<role>` with an optional
  `-sm` / `-lg` tier, the most common size in each role left unsuffixed. Tailwind
  needs a t-shirt ladder because it is a generic framework whose sizes are chosen
  in markup; here the token is consumed by a rule that already knows its role, so
  `--text-heading-lg` says what it is for while `--text-4xl` only says how big it
  is. A ladder also brings back the renumbering problem — inserting a size between
  `lg` and `xl` shifts everything after it. Spacing keeps numbers, because there it
  really is a ladder.
- **Duration and easing are set as separate properties**, the way Tailwind's own
  `transition` utility does, rather than folded into the shorthand. A rule then
  states its timing once instead of once per animated property.

Colours are semantic for the same reason, one layer up: `--color-ink`, never
`--color-stone-800`. A hue ramp like Tailwind's `red-100…900` is a *primitive* —
useful for building a palette, wrong for consuming one, because every component
would name a shade and every shade would need swapping per theme. Modifiers come
from a single vocabulary so the ladder reads the same everywhere:

| Modifier | Means |
| -------- | ----- |
| *(none)* | the default for that role |
| `-muted` | one step weaker |
| `-subtle` | two steps weaker |
| `-strong` | one step stronger |
| `-sunken` | recessed rather than raised — an elevation, not an emphasis |

[`tests/test_tokens.py`](../tests/test_tokens.py) enforces both patterns: the type
scale must resolve to those four roles, and no colour may carry a modifier outside
that table or a bare numeric suffix.

`--border` is the one token outside the scheme: a composite shorthand
(`1px solid var(--color-line)`), not a theme value. Tailwind has no namespace for
it because it generates border utilities from a width and a colour; here
`border: var(--border)` appears often enough that spelling it out every time
would be worse.
