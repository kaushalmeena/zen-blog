# The request lifecycle

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
