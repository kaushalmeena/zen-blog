"""Colour-scheme preference, stored in a cookie.

A JavaScript toggle would be the obvious way to do this, and this project does not
have any. So the preference round-trips through the server instead: the button is
a form, the choice lands in a cookie, and ``data-theme`` on ``<html>`` decides
which set of custom properties applies.

``auto`` is the default and defers to ``prefers-color-scheme``, so a visitor who
never touches the switch gets the theme their OS asked for.

The switch is always one click. Both a "go light" and a "go dark" control are
rendered, and CSS shows only the one that is not the current appearance — see
``partials/theme_switch.html``. That matters for ``auto``: the server cannot know
what the OS prefers, so it cannot pick the right single target, but CSS can.
"""

from __future__ import annotations

from flask import Request

COOKIE_NAME = "theme"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # one year

AUTO = "auto"
LIGHT = "light"
DARK = "dark"

THEMES = (AUTO, LIGHT, DARK)


def current_theme(request: Request) -> str:
    """Return the visitor's stored theme, falling back to ``auto``."""
    value = request.cookies.get(COOKIE_NAME, AUTO)
    return value if value in THEMES else AUTO
