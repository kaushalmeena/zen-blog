"""Shared query and rendering logic for the paginated post lists.

Home, tag pages, profiles, saved posts and the following feed all show the same
list of post cards, so they share one entry point. It decides whether to answer
with a full page, a replacement list (search) or the next batch of cards
(load-more), based on what htmx asked for.
"""

from __future__ import annotations

from flask import Response, current_app, render_template, request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from blog.extensions import db
from blog.models import Post, Tag
from blog.responses import render_fragment, wants_fragment


def published_posts():
    """Return a select() of published posts, newest first, with authors loaded."""
    return (
        select(Post)
        .where(Post.published.is_(True))
        .order_by(Post.created.desc())
        .options(selectinload(Post.author), selectinload(Post.tags))
    )


def apply_filters(query):
    """Narrow ``query`` using the ``q`` and ``tag`` query-string parameters."""
    search = (request.args.get("q") or "").strip()
    if search:
        term = f"%{search}%"
        query = query.where(Post.title.ilike(term) | Post.body.ilike(term))

    tag_slug = (request.args.get("tag") or "").strip()
    if tag_slug:
        query = query.where(Post.tags.any(Tag.slug == tag_slug))

    return query


def render_listing(query, template: str, **context) -> Response | str:
    """Paginate ``query`` and render it for either htmx or a plain browser."""
    pagination = db.paginate(
        query,
        page=request.args.get("page", 1, type=int),
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    context = {
        "pagination": pagination,
        "search": (request.args.get("q") or "").strip(),
        "active_tag": (request.args.get("tag") or "").strip(),
        **context,
    }

    if wants_fragment():
        # The load-more link sends partial=page and swaps itself for the next
        # batch; the search box sends nothing and replaces the whole list.
        fragment = (
            "partials/post_batch.html"
            if request.args.get("partial") == "page"
            else "partials/post_list.html"
        )
        return render_fragment(fragment, **context)

    return render_template(template, **context)
