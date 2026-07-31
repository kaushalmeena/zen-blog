# Palette and type

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
