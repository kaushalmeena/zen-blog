# Code map

## Code map

Coarse tour. Line counts are a rough guide to weight, not a target.

### The request layer

- **`blog/blueprints/`** — one module per area of the site. `main` (home, tags,
  following feed, theme switch), `auth` (login, register, logout), `posts` (the
  biggest, ~236 lines: CRUD, likes, saves, comments), `users` (profiles, follow
  graph, drafts, settings), `feeds` (RSS, sitemap, robots).
- **`blog/responses.py`** — the htmx/full-page decision. `wants_fragment()`,
  `render_fragment()`, `redirect_back()`, `referrer_or()`. Read this before
  touching any view that htmx talks to.
- **`blog/listings.py`** — every paginated post list (home, tag filter, profile,
  saved, drafts, following) shares one query builder and one renderer, because
  they are the same screen with a different `WHERE` clause.
- **`blog/forms.py`** — WTForms classes. Validation lives here, not in views.
- **`blog/errors.py`** — 400/403/404/500 handlers, all rendering one template.

### Data

- **`blog/models.py`** — the largest module (~295 lines) and the right place to
  start reading. Four entities and four join tables:

  ```
  user ──┬── post ──┬── comment
         │          └── post_tags ── tag
         ├── likes ──── post
         ├── saves ──── post
         └── follows ── user        (self-referential)
  ```

  Aggregate counts (`Post.like_count`, `User.follower_count`, …) are
  `column_property` correlated subqueries attached after mapping, so a listing
  reads its counts in the same round trip as its rows.

- **`migrations/`** — Alembic. The schema is only ever changed through a
  revision; `flask db check` fails if the models and the history disagree, and
  CI runs it.

### Presentation

- **`blog/templates/`** — `base.html` plus one directory per area. Everything in
  `partials/` is an htmx swap target or a shared macro, and each carries a stable
  `id` so the server can re-render exactly that element.
- **`blog/static/styles/main.css`** — the entire design system in one file:
  tokens, both palettes, every component. No preprocessor, no build.
  [`design.md`](foundations.md) covers the token naming convention and the
  intent behind the visual choices.
- **`blog/rendering.py`** — Markdown to sanitized HTML, plus excerpts and reading
  time. The only place untrusted text becomes markup.
- **`blog/template_filters.py`** — Jinja filters and globals (dates, `url_with`,
  identicons).
- **`blog/avatars.py`** — identicons generated from a hash of the username.
- **`blog/theming.py`** — the light/dark/auto preference and its cookie.
- **`blog/assets.py`** — content-hash stamps on static URLs, which is what makes
  long cache lifetimes safe.

### Tests

`tests/` is organised by concern, not by module, because the interesting
properties cut across modules. `test_authorization.py` and
`test_no_javascript.py` are the two worth reading first: they encode rules the
implementation must not break, and both exist because those rules were once
broken.

`scripts/` sits outside the package and is not imported by it. It currently holds
`screenshots.py`, which drives the local Chrome through Playwright to recapture
the README images against a running dev server — so those images can be
regenerated rather than being artefacts nobody can reproduce.
