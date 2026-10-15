# zen-blog

A multi-user blogging site rendered entirely on the server. There is **no
hand-written JavaScript and no front-end build step** — the only script on the
page is a vendored copy of htmx. Most rules below exist to keep it that way.

## Done means the checks pass

```bash
uv run pytest
uv run ruff check . && uv run ruff format .
```

`uv run flask --app blog db check` fails when the models and the migration
history have drifted apart; CI runs it on every push. After changing a model,
generate and apply a migration rather than editing the schema by hand.

## Reading the codebase

Start with [`docs/overview.md`](docs/overview.md), then follow the work:

| Working on                                     | Read                                                  |
| ---------------------------------------------- | ----------------------------------------------------- |
| Orientation, entry points                      | [overview.md](docs/overview.md)                       |
| Finding the module that owns something         | [code-map.md](docs/code-map.md)                       |
| Request handling, cross-cutting concerns       | [request-lifecycle.md](docs/request-lifecycle.md)     |
| Rules the code relies on, and what is refused  | [invariants.md](docs/invariants.md)                   |
| The idea, token naming convention              | [foundations.md](docs/foundations.md)                 |
| Colours, type scale                            | [palette.md](docs/palette.md)                         |
| Spacing, layout, theme switching               | [layout.md](docs/layout.md)                           |

## Invariants

Each of these is covered by a test. Breaking one is a bug even when nothing
visibly fails — read [invariants.md](docs/invariants.md) before working around
any of them.

- **Links navigate; forms mutate.** Anything that writes to the database is a
  `<form method="post">`, never a link, so a prefetch or an `<img>` cannot
  trigger it. This is why logout is a form.
- **htmx is an enhancement, never a requirement.** Every control works as a
  plain form or link first; `tests/test_no_javascript.py` posts each one the way
  a script-less browser would.
- **The server owns authorization.** A hidden control is not a check.
- **Fragments are addressable.** A swappable element has a stable `id`, and the
  partial that renders it reproduces that same `id`.
- **No component names a literal colour or size.** Tokens only, so light and
  dark need no per-component branching. `tests/test_tokens.py` enforces this.
- **Drafts are invisible to everyone but their author** — in listings, on the
  post page, in the feed and in the sitemap.
- **One script tag.** The vendored htmx and nothing else, asserted by test.

## Non-goals

Do not add these without being asked — each absence is a decision, not an
oversight: a build step, bundler or CSS preprocessor; any JavaScript of our own;
web fonts; a JSON API; image uploads; a caching layer or background jobs.
