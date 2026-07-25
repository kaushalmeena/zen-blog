"""Markdown rendering, HTML sanitizing and text helpers.

Post and comment bodies are stored as Markdown and rendered on the server. The
result is run through :mod:`nh3` so a user cannot inject scripts or event
handlers into someone else's browser.
"""

from __future__ import annotations

import re

import markdown
import nh3
from markupsafe import Markup

WORDS_PER_MINUTE = 220

#: Tags a post body may use. Deliberately excludes ``script``, ``style``,
#: ``iframe`` and form elements.
ALLOWED_TAGS = {
    "a",
    "abbr",
    "b",
    "blockquote",
    "br",
    "code",
    "dd",
    "del",
    "details",
    "div",
    "dl",
    "dt",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "loading"},
    "code": {"class"},
    "div": {"class"},
    "pre": {"class"},
    "td": {"align"},
    "th": {"align"},
}

_MARKDOWN_SYNTAX = re.compile(r"[*_`#>\[\]()!\-]|\n{2,}")
_WHITESPACE = re.compile(r"\s+")


BASE_EXTENSIONS = ["fenced_code", "tables", "sane_lists"]


def render_markdown(text: str | None, *, soft_breaks: bool = False) -> Markup:
    """Render ``text`` as Markdown and return sanitized, template-safe HTML.

    Args:
        text: The Markdown source.
        soft_breaks: Turn every single newline into a ``<br>``. Right for
            comments, where people press Enter and expect a line break; wrong for
            posts, where it would break hard-wrapped prose mid-sentence.
    """
    if not text:
        return Markup("")
    extensions = [*BASE_EXTENSIONS, "nl2br"] if soft_breaks else BASE_EXTENSIONS
    html = markdown.markdown(text, extensions=extensions, output_format="html")
    clean = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer nofollow",
    )
    return Markup(clean)


def plain_text(text: str | None) -> str:
    """Strip Markdown syntax and collapse whitespace into a single line."""
    if not text:
        return ""
    stripped = nh3.clean(render_markdown(text), tags=set())
    return _WHITESPACE.sub(" ", _MARKDOWN_SYNTAX.sub(" ", stripped)).strip()


def excerpt(text: str | None, length: int = 200) -> str:
    """Return a plain-text teaser of at most ``length`` characters."""
    flat = plain_text(text)
    if len(flat) <= length:
        return flat
    return flat[:length].rsplit(" ", 1)[0].rstrip(".,;:") + "…"


def reading_time(text: str | None) -> int:
    """Estimate reading time in whole minutes, never returning less than one."""
    words = len(plain_text(text).split())
    return max(1, round(words / WORDS_PER_MINUTE))
