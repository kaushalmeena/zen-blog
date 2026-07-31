# Invariants and non-goals

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
