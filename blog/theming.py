"""Colour-scheme preference, stored in a cookie.

A JavaScript toggle would be the obvious way to do this, and this project does not
have any. So the preference round-trips through the server instead: the button is
a form, the choice lands in a cookie, and ``data-theme`` on ``<html>`` decides
which set of custom properties applies.

``auto`` is the default and leaves the decision to ``prefers-color-scheme``, so a
visitor who never touches the button still gets the theme their OS asked for.
"""

from __future__ import annotations

from flask import Request

COOKIE_NAME = "theme"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # one year

AUTO = "auto"
LIGHT = "light"
DARK = "dark"

THEMES = (AUTO, LIGHT, DARK)

#: What the button switches to next, so one control cycles all three states.
NEXT_THEME = {AUTO: LIGHT, LIGHT: DARK, DARK: AUTO}

LABELS = {
    AUTO: "follow system",
    LIGHT: "light",
    DARK: "dark",
}

ICONS = {
    AUTO: "contrast",
    LIGHT: "sun",
    DARK: "moon",
}


def current_theme(request: Request) -> str:
    """Return the visitor's stored theme, falling back to ``auto``."""
    value = request.cookies.get(COOKIE_NAME, AUTO)
    return value if value in THEMES else AUTO
