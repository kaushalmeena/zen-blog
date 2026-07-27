# Design

The visual system: what it is trying to be, the tokens it is built from, and the
naming convention those tokens follow. All of it lives in one file,
`blog/static/styles/main.css`, with no preprocessor and no build step.

For the system's architecture, see [architecture.md](architecture.md).

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

## Palette

Every colour is declared once per theme as `--color-light-*` / `--color-dark-*`,
then assigned to the semantic name below. `data-theme` on `<html>` picks the
half. No component rule ever names a literal colour — that is what lets light and
dark work with no per-component branching, and
[`tests/test_tokens.py`](../tests/test_tokens.py) enforces it.

| Token | Light | Dark |
| ----- | ----- | ---- |
| `--color-bg` | `#f7f5f0` | `#181716` |
| `--color-surface` | `#fdfbf6` | `#1e1d1b` |
| `--color-surface-sunken` | `#edeae2` | `#262421` |
| `--color-ink` | `#2c2a29` | `#e6e2dd` |
| `--color-ink-muted` | `#55524f` | `#c2bdb6` |
| `--color-ink-subtle` | `#787470` | `#9e9993` |
| `--color-line` | `#e0dcd3` | `#2f2d2a` |
| `--color-line-strong` | `#c4bfb4` | `#494540` |
| `--color-accent` | `#a35c48` | `#d98870` |
| `--color-danger` | `#9e3b2e` | `#e08573` |

Light is warm paper: unbleached cotton, charcoal ink, terracotta. Dark is night
ink: charcoal slate, aged-paper text, soft clay. Neither uses pure black or pure
white.

## Type

System stacks only — nothing is downloaded, so there is no font-loading flash.
`Newsreader` and `Inter` lead their stacks and are used where installed, falling
back to Palatino/Charter/Georgia and the platform sans.

| Token | Size | Role |
| ----- | ---- | ---- |
| `--text-label` | 0.6875rem | tracked capitals: nav, buttons, meta, form labels |
| `--text-caption` | 0.8125rem | small secondary text: hints, counts, menu items |
| `--text-body` | 1.0625rem | default body copy |
| `--text-body-lg` | 1.1875rem | long-form article text |
| `--text-heading-sm` | 1.4375rem | listing and card titles |
| `--text-heading` | 1.75rem | page headings |
| `--text-heading-lg` | 2.375rem | a single post's title |

## Spacing

One ramp, used for padding, margin and gap alike:

`1` 0.25rem · `2` 0.5rem · `3` 0.75rem · `4` 1rem · `5` 1.5rem · `6` 2.5rem · `7` 4rem

## Layout

- One reading column, `--container-prose` at 680px.
- Page margins `clamp(1.5rem, 6vw, 3rem)` — generous, and they grow with the
  viewport.
- The header is sticky, which also gives the account popover a fixed trigger
  position to align against.

## Theme switching

The preference is a cookie the server reads into `data-theme`, not a script, so
it persists across pages and never flashes the wrong theme. Three states:
`light`, `dark`, `auto` (follow the OS).

One consequence worth knowing: while the stored value is `auto`, the server does
not know which appearance is actually in effect — `prefers-color-scheme` is
invisible to it. So any control that must reflect the *effective* theme rather
than the stored one is decided in CSS. That is why the header toggle renders both
a "go light" and a "go dark" control and hides one with a media query, instead of
the server picking a single target.

## Conventions to keep

- Add a colour to the palette, never to a component.
- Pick a size from the scale; if none fits, that is usually a sign the design does
  not need another size.
- State changes show in colour and fill, never in size — a toggled control that
  changes its own dimensions makes a row go ragged.
- Focus is always visible. Text controls get a flush ring instead of the offset
  outline, so a focused field does not appear to grow.
- Icons inherit `currentColor` and size with the text around them.
