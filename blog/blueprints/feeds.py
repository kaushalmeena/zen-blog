"""Machine-readable endpoints: RSS, sitemap and robots.txt."""

from __future__ import annotations

from flask import Blueprint, Response, render_template, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from blog.extensions import db
from blog.models import Post, User

bp = Blueprint("feeds", __name__)

FEED_LIMIT = 30


def _xml(template: str, **context) -> Response:
    body = render_template(template, **context)
    return Response(body, mimetype="application/xml")


@bp.route("/feed.xml")
def rss():
    """Serve an RSS 2.0 feed of the most recent published posts."""
    posts = db.session.scalars(
        select(Post)
        .where(Post.published.is_(True))
        .order_by(Post.created.desc())
        .limit(FEED_LIMIT)
        .options(selectinload(Post.author))
    ).all()
    return _xml("feeds/rss.xml", posts=posts)


@bp.route("/sitemap.xml")
def sitemap():
    """Serve a sitemap covering the home page, posts and profiles."""
    posts = db.session.scalars(
        select(Post).where(Post.published.is_(True)).order_by(Post.updated.desc())
    ).all()
    usernames = db.session.scalars(select(User.username).order_by(User.username)).all()
    return _xml("feeds/sitemap.xml", posts=posts, usernames=usernames)


@bp.route("/robots.txt")
def robots():
    """Allow crawling of public pages and point crawlers at the sitemap."""
    lines = [
        "User-agent: *",
        "Disallow: /settings/",
        "Disallow: /drafts/",
        "Disallow: /saved/",
        "Disallow: /sign-in/",
        "Disallow: /sign-up/",
        f"Sitemap: {url_for('feeds.sitemap', _external=True)}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")
