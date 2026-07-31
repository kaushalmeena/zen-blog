# Spacing, layout and theming

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
