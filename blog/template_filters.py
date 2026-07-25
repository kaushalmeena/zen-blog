"""Jinja filters, globals and context processors."""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import format_datetime
from urllib.parse import urlencode

from flask import Flask, current_app, request

from blog.avatars import identicon
from blog.forms import MAX_TAGS
from blog.theming import ICONS, LABELS, NEXT_THEME, current_theme


def url_with(**overrides) -> str:
    """Return the current URL with ``overrides`` merged into the query string.

    Used for pagination and filter links so parameters already in the URL
    survive. Passing ``None`` removes a parameter, e.g. ``url_with(tag=None)``.
    """
    args = request.args.to_dict()
    # 'partial' is htmx bookkeeping (see blog/listings.py); it must never leak
    # into an href a plain browser might follow.
    args.pop("partial", None)
    for key, value in overrides.items():
        if value in (None, ""):
            args.pop(key, None)
        else:
            args[key] = value
    query = urlencode(args)
    return f"{request.path}?{query}" if query else request.path


def as_local(value: datetime) -> datetime:
    """Treat a naive database timestamp as UTC."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def date_format(value: datetime | None, fmt: str = "%b %d, %Y") -> str:
    """Format a timestamp for display."""
    return as_local(value).strftime(fmt) if value else ""


def iso_format(value: datetime | None) -> str:
    """Format a timestamp for a ``<time datetime>`` attribute."""
    return as_local(value).isoformat() if value else ""


def rfc822(value: datetime | None) -> str:
    """Format a timestamp for RSS ``pubDate`` elements."""
    return format_datetime(as_local(value)) if value else ""


# (unit, seconds per unit, how many of them before moving up to the next unit)
_AGE_UNITS = (
    ("minute", 60, 60),
    ("hour", 3600, 24),
    ("day", 86400, 7),
    ("week", 604800, 5),
)


def time_ago(value: datetime | None) -> str:
    """Render a coarse relative time such as ``3 days ago``.

    Falls back to an absolute date once something is more than a few weeks old,
    where "5 weeks ago" stops being more useful than the date itself.
    """
    if not value:
        return ""
    seconds = int((datetime.now(UTC) - as_local(value)).total_seconds())
    if seconds < 60:
        return "just now"
    for unit, length, limit in _AGE_UNITS:
        if seconds < length * limit:
            count = seconds // length
            return f"{count} {unit}{'s' if count != 1 else ''} ago"
    return date_format(value)


def register(app: Flask) -> None:
    """Attach the filters, globals and context processors to ``app``."""
    app.jinja_env.filters.update(
        date=date_format,
        iso=iso_format,
        rfc822=rfc822,
        time_ago=time_ago,
    )
    app.jinja_env.globals.update(
        identicon=identicon,
        url_with=url_with,
        max_tags=MAX_TAGS,
    )

    @app.context_processor
    def inject_site():
        theme = current_theme(request)
        return {
            "site_name": current_app.config["SITE_NAME"],
            "site_tagline": current_app.config["SITE_TAGLINE"],
            "current_year": datetime.now(UTC).year,
            "theme": theme,
            "theme_icon": ICONS[theme],
            "theme_label": LABELS[theme],
            "next_theme": NEXT_THEME[theme],
            "next_theme_label": LABELS[NEXT_THEME[theme]],
        }
