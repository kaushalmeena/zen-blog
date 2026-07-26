"""Helpers for serving the same view to htmx and to plain browsers.

Every interactive control in the templates is a real link or form first and an
htmx attribute second. These helpers keep that contract in one place: when the
request came from htmx we answer with a fragment, otherwise we fall back to a
normal redirect or full page render.
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from flask import Response, make_response, redirect, render_template, request, url_for
from markupsafe import Markup

from blog.extensions import htmx


def wants_fragment() -> bool:
    """Return whether htmx issued this request and expects a fragment back."""
    return bool(htmx) and not htmx.boosted


def render_fragment(template: str, **context) -> Response:
    """Render ``template`` plus an out-of-band refresh of the flash message area."""
    body = Markup(render_template(template, **context)) + Markup(
        render_template("partials/messages.html", oob=True)
    )
    response = make_response(body)
    response.headers["Cache-Control"] = "no-store"
    return response


def redirect_back(endpoint: str = "main.home", **values) -> Response:
    """Redirect the browser, using htmx's client-side redirect when applicable.

    ``HX-Redirect`` makes htmx perform a full navigation, which is what we want
    after an action that changes which page the user should be looking at.
    """
    target = url_for(endpoint, **values)
    if wants_fragment():
        response = make_response("")
        response.headers["HX-Redirect"] = target
        return response
    return redirect(target)


def _referrer_path() -> str | None:
    """Reduce ``Referer`` to a path on this site, or return ``None``.

    Only the path and query survive. Rebuilding the target rather than echoing
    the header back means the redirect cannot leave this origin even if the
    ``Host`` it was compared against was itself spoofed, and it rules out the
    leading-slash tricks a browser reads as an authority.
    """
    referrer = request.referrer
    if not referrer:
        return None
    parsed = urlsplit(referrer)
    # A browser always sends an absolute URL here, so anything without an
    # http(s) scheme and a matching host is either hostile or not worth guessing
    # about. Demanding both is what rejects `//evil.example` and its
    # extra-slash variants, which `urlsplit` otherwise reads as a bare path.
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc != urlsplit(request.host_url).netloc:
        return None
    path = parsed.path or "/"
    if not path.startswith("/") or path[1:2] in {"/", "\\"}:
        return None
    return urlunsplit(("", "", path, parsed.query, ""))


def referrer_or(endpoint: str = "main.home", **values) -> Response:
    """Redirect to the referring page when it is safe, else to ``endpoint``."""
    target = _referrer_path()
    if target:
        if wants_fragment():
            response = make_response("")
            response.headers["HX-Redirect"] = target
            return response
        return redirect(target)
    return redirect_back(endpoint, **values)
