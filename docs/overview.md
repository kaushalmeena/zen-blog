# Overview

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
