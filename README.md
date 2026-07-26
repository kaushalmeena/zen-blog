<div align="center">

<img src="blog/static/images/icon.svg" alt="" width="96" height="96" />

# myapp-blog

**A minimal, JavaScript-free multi-user blog — Flask + htmx, server-rendered, no build step.**

[![CI](https://github.com/kaushalmeena/myapp-blog/actions/workflows/ci.yml/badge.svg)](https://github.com/kaushalmeena/myapp-blog/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-3DA639?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![htmx](https://img.shields.io/badge/htmx-2.x-3D72D7?logo=htmx&logoColor=white)](https://htmx.org/)
[![uv](https://img.shields.io/badge/uv-managed-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)

</div>

---

## What this is

A small multi-user blogging site: register, write posts in Markdown, tag them,
follow other authors, like, save and comment. Everything is rendered on the
server. There is **no hand-written JavaScript and no front-end build step** — the
only script on the page is a vendored copy of [htmx](https://htmx.org/), which
turns ordinary links and forms into partial page updates.

Every interactive control is a real `<a href>` or `<form method="post">` first.
htmx attributes are layered on top, so with JavaScript disabled the site still
works — it just does full page loads instead of swapping fragments.

## Features

**Writing**

- Markdown posts with fenced code blocks, tables and quotes, sanitized server-side with [`nh3`](https://github.com/messense/nh3)
- Drafts — write privately, publish when ready
- Tags, with per-tag filtering and a tag index
- SEO-friendly slugs derived from the title, de-duplicated automatically
- Estimated reading time

**Reading**

- Posts are public; no login wall in front of the content
- Search-as-you-type across titles and bodies, with a shareable URL
- "Load more" pagination that appends instead of navigating
- RSS feed, `sitemap.xml` and `robots.txt`
- Light / dark / follow-system switch. The choice is a cookie the server reads,
  not a script, so it persists across pages and never flashes the wrong theme
- A CSS-generated graph-paper background that recolours with the theme — no image
  request, and nothing to swap when the theme changes

**Social**

- Follow authors and read a feed of just their posts
- Likes and a personal reading list (saved posts)
- Comments, added and removed in place
- Profiles with bios and deterministic identicon avatars generated from the username — nothing to upload, nothing to store

## Tech stack

| Area           | Tools                                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| **Framework**  | [Flask 3](https://flask.palletsprojects.com/) · [Jinja2](https://jinja.palletsprojects.com/)                |
| **Front end**  | [htmx 2](https://htmx.org/) + [flask-htmx](https://flask-htmx.readthedocs.io/) · one hand-written CSS file · [Lucide](https://lucide.dev/) icons as an SVG sprite |
| **Database**   | [SQLAlchemy 2](https://www.sqlalchemy.org/) · SQLite by default, any URL via `DATABASE_URL`                 |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) via [Flask-Migrate](https://flask-migrate.readthedocs.io/)      |
| **Auth**       | [Flask-Login](https://flask-login.readthedocs.io/) · [Flask-WTF](https://flask-wtf.readthedocs.io/) CSRF    |
| **Tooling**    | [uv](https://docs.astral.sh/uv/) · [Ruff](https://docs.astral.sh/ruff/) · [pytest](https://pytest.org/)     |
| **Deployment** | [Docker](https://www.docker.com/) · [gunicorn](https://gunicorn.org/)                                      |

## Getting started

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[git](https://git-scm.com/downloads). uv installs the right Python for you.

```bash
git clone https://github.com/kaushalmeena/myapp-blog.git
```

```bash
cd myapp-blog && uv sync
```

Create the schema, and optionally some demo content:

```bash
uv run flask --app blog db upgrade
```

```bash
uv run flask --app blog seed
```

Run it:

```bash
uv run flask --app blog run --debug
```

The site is at [localhost:5000](http://localhost:5000/). The seed command creates
the users `ada`, `grace` and `linus`, all with the password `password123`.

Copy `.env.example` to `.env` to set `FLASK_APP=blog` once and drop the `--app`
flag from the commands above.

## Development

```bash
uv run pytest
```

```bash
uv run ruff check . && uv run ruff format .
```

After changing a model, generate and apply a migration:

```bash
uv run flask --app blog db migrate -m "describe the change"
```

```bash
uv run flask --app blog db upgrade
```

`uv run flask --app blog db check` fails when the models and the migration
history have drifted apart; CI runs it on every push.

Other useful commands:

| Command        | What it does                                          |
| -------------- | ----------------------------------------------------- |
| `flask seed`   | Insert demo users, posts, comments, likes and follows  |
| `flask reset`  | Drop and recreate every table (asks first)             |
| `flask routes` | List the URL map                                       |

## Caching

There is no build step, so static filenames never change and a browser cannot tell
a new stylesheet from the one it has. Every `url_for('static', ...)` therefore
gains a `?v=` stamp derived from the file's contents, which makes it safe to serve
assets as `public, max-age=1y, immutable` in production — no revalidation request
per asset, per page load. In development the lifetime stays at zero so edits show
up immediately.

Pages are the opposite case: anything rendered for a logged-in user is
`no-store, private`, because it contains controls only that user may use and the
back button would otherwise redisplay it after someone else logs in.

## How the htmx pieces fit together

- `blog/responses.py` decides between a fragment and a full page. `render_fragment()`
  also appends the flash-message region as an [out-of-band swap](https://htmx.org/attributes/hx-swap-oob/),
  so a flash raised during a fragment request still reaches the page.
- `blog/listings.py` serves three shapes from one view: a full page, a replacement
  list (search), or the next batch of cards (load-more, flagged with `partial=page`).
- Templates in `templates/partials/` are each addressable by id, so the server can
  re-render exactly one element — an action bar, a follow button, a comment.
- CSRF tokens reach htmx through a single `hx-headers` attribute on `<body>`, and
  `CSRFProtect` validates every state-changing request. Hand-written forms also
  carry a hidden token via the `csrf()` macro, because a browser without
  JavaScript posts them natively and sends no header — `tests/test_no_javascript.py`
  turns CSRF on and posts every one of those forms the way such a browser would.

## Deployment

With Docker:

```bash
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))") docker compose up --build
```

The app then listens on [localhost:8000](http://localhost:8000/). The container
applies migrations on start and serves through gunicorn as a non-root user;
SQLite lives in the `blog-data` volume.

Without Docker, set `APP_CONFIG=production` and a `SECRET_KEY` (production
refuses to boot without one), then:

```bash
uv run gunicorn "blog:create_app()" --bind 0.0.0.0:8000 --workers 3
```

To use Postgres instead of SQLite, set `DATABASE_URL` and add the driver:

```bash
uv add "psycopg[binary]"
```

### Configuration

| Variable       | Default               | Notes                                                      |
| -------------- | --------------------- | ---------------------------------------------------------- |
| `APP_CONFIG`   | `development`         | `development` · `testing` · `production`                    |
| `SECRET_KEY`   | `dev`                 | **Required** in production; the app won't start without it  |
| `DATABASE_URL` | SQLite in `instance/` | Any SQLAlchemy URL                                          |
| `STATIC_MAX_AGE` | `0` dev / 1 year prod | Static cache lifetime; URLs are content-stamped, so long is safe |
| `FLASK_APP`    | —                     | Set to `blog` to skip `--app blog`                          |

## License

MIT — see [LICENSE](LICENSE).
