# Architecture

Orientation for someone about to change this code. It describes the shape of the
system, the handful of rules the code relies on, and the things it deliberately
does not do. It is intentionally coarse: anything that would need editing for a
routine change belongs in a docstring, not here.

For how to run and deploy the project, see [README.md](../README.md). For the
visual system and its tokens, see [DESIGN.md](DESIGN.md).

## Bird's eye view

A server-rendered multi-user blog. Requests come in, Flask renders Jinja
templates against a SQL database, and HTML goes out. There is no client-side
application and no API — the HTML *is* the interface.

The one wrinkle is [htmx](https://htmx.org/). Some interactions (search, load
more, like, save, follow, comment) update part of the page instead of reloading
it. htmx does that by asking the server for a fragment of HTML and swapping it
into place. So most views can answer in two shapes: a full page, or the fragment
that changed. Deciding between those two shapes is the central piece of
machinery, and it lives in one module (`blog/responses.py`).

Everything else is conventional Flask.

```
browser ──▶ blueprint view ──▶ models (SQLAlchemy) ──▶ SQLite/Postgres
                  │
                  └──▶ responses.py ──▶ full page   (normal navigation)
                                    └──▶ fragment   (htmx request)
```

## Entry points

| Entry | Where |
| ----- | ----- |
| App factory | `create_app()` in `blog/__init__.py` — the only way an app is built |
| Dev server | `flask --app blog run` |
| Production | `gunicorn "blog:create_app()"` |
| CLI | `blog/cli.py` registers `flask seed` and `flask reset` |
| Migrations | `migrations/`, driven by Flask-Migrate |

`create_app()` reads `APP_CONFIG` to pick a class from `blog/config.py`, then
registers extensions, blueprints, error handlers, Jinja helpers and the cache
policy. Nothing is configured at import time — there is no module-level `app`,
so tests build isolated instances freely.

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
  [`DESIGN.md`](DESIGN.md) covers the token naming convention and the
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

## The request lifecycle

Worth understanding once, because it explains the shape of most views.

1. A view does its work and then hands off to `blog/responses.py`.
2. `wants_fragment()` asks whether htmx sent this request.
3. **Full page** — render the page template as normal.
4. **Fragment** — render just the changed partial, and append the flash-message
   region as an [out-of-band swap](https://htmx.org/attributes/hx-swap-oob/) so a
   message raised during a fragment request still reaches the page.
5. For actions that should move the user, `redirect_back()` sends a normal 302 to
   a browser and an `HX-Redirect` header to htmx.

`blog/listings.py` is the same idea one level up: one view serves a full page, a
replaced list (search), or the next batch of cards (load-more, flagged with
`partial=page`).

## Cross-cutting concerns

**Authorization.** Ownership is checked in the view, not the template. Hiding a
button is presentation; `_require_author()` is the control. Both matter, and the
tests assert both, because an earlier version only hid the button.

**CSRF.** `CSRFProtect` covers every state-changing request. htmx sends the token
as a header from a single `hx-headers` attribute on `<body>`; hand-written forms
*also* embed a hidden field via the `csrf()` macro, because a browser without
JavaScript posts natively and sends no header.

**Caching.** Two opposite rules, both in `_register_cache_policy()`. Static files
are identical for everyone and their URLs carry a content stamp, so in production
they are `public, max-age=1y, immutable`; development leaves `STATIC_MAX_AGE` at
zero, which is why edits appear immediately there. Pages rendered for a logged-in
user are `no-store, private`, or the back button would redisplay one account's
page to the next. Static responses also drop `Vary: Cookie` — a custom session
interface skips session handling for them, because Flask adds that header in
`save_session`, after `after_request` has already run.

**Theming.** The preference is a cookie the server reads into `data-theme` on
`<html>`. No script, so no flash of the wrong theme. Where a decision needs to
know the *effective* appearance rather than the stored one — a switch offering
the opposite of what you see — it is made in CSS, because
`prefers-color-scheme` is invisible to the server.

**Sanitising.** Post and comment bodies are user Markdown. `blog/rendering.py`
renders and then runs the result through `nh3` with an explicit tag allowlist.
Nothing else should be marked safe for Jinja.

## Invariants

Rules the code relies on. Breaking one is a bug even if nothing visibly fails,
and each is covered by a test.

1. **Links navigate; forms mutate.** Anything that writes to the database is a
   `<form method="post">`, never a link — a prefetch or an `<img>` must not be
   able to trigger it. This is why logout is a form.
2. **htmx is an enhancement, never a requirement.** Every control works as a
   plain form or link first. `tests/test_no_javascript.py` turns CSRF on and
   posts each one the way a script-less browser would.
3. **The server owns authorization.** A hidden control is not a check.
4. **Fragments are addressable.** A swappable element has a stable `id`, and the
   partial that renders it reproduces that same `id`.
5. **No component names a literal colour or size.** Only tokens, so light and
   dark need no per-component branching. `tests/test_tokens.py` enforces this.
6. **Drafts are invisible to everyone but their author** — in listings, on the
   post page, in the feed and in the sitemap.
7. **One script tag.** The vendored htmx, and nothing else. Asserted by test.

## Deliberate non-goals

Things that look missing but are choices:

- **No build step, bundler or CSS preprocessor.** Editing a file is the whole
  workflow. The cost is one large hand-written stylesheet, accepted knowingly.
- **No JavaScript of our own.** Where a browser-side capability would normally be
  reached for — persisting a theme, a dropdown menu — the job is given to a
  cookie or to the native Popover API instead.
- **No web fonts.** System stacks only, so there is no font loading to manage.
- **No JSON API.** Views return HTML. Adding an API means adding a serialisation
  layer, which does not exist yet.
- **No image uploads.** Avatars are generated from the username, which is why
  there is no storage backend or upload validation.
- **No caching layer or background jobs.** The aggregate counts are subqueries
  and the site is small; Redis and Celery would be unearned complexity.

## Where to make a change

| To change… | Start at |
| ---------- | -------- |
| A page's content or markup | `blog/templates/` |
| Anything visual | `blog/static/styles/main.css` |
| Behaviour of a route | the matching module in `blog/blueprints/` |
| The schema | `blog/models.py`, then generate a migration |
| What htmx swaps | the partial's `id`, plus the view's `render_fragment()` call |
| Validation rules | `blog/forms.py` |
| A new page-level setting | `blog/config.py` |
