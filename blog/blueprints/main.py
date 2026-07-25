"""Home page, tag browsing and the personalised following feed."""

from __future__ import annotations

from flask import Blueprint, abort, current_app, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func, select

from blog.extensions import db
from blog.listings import apply_filters, published_posts, render_listing
from blog.models import Post, Tag, follows, post_tags
from blog.responses import referrer_or
from blog.theming import COOKIE_MAX_AGE, COOKIE_NAME, THEMES

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    """List every published post, honouring the search box and tag filter."""
    return render_listing(
        apply_filters(published_posts()),
        "home.html",
        page_title="HOME",
        accent="orange",
    )


@bp.route("/tags/")
def tags():
    """Show every tag with its post count, largest first."""
    rows = db.session.execute(
        select(Tag, func.count(post_tags.c.post_id).label("total"))
        .outerjoin(post_tags, post_tags.c.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(func.count(post_tags.c.post_id).desc(), Tag.name)
    ).all()
    return render_template(
        "tags.html",
        tag_counts=rows,
        page_title="TAGS",
        accent="purple",
    )


@bp.post("/theme/")
def set_theme():
    """Store the visitor's colour-scheme choice and return them to their page.

    No JavaScript involved: the switch is a form, the answer is a cookie, and the
    next render puts it on ``<html data-theme>``. Works for anonymous visitors too,
    so it deliberately has no ``@login_required``.
    """
    choice = request.form.get("theme", "")
    if choice not in THEMES:
        abort(400, "Unknown theme.")

    response = referrer_or("main.home")
    response.set_cookie(
        COOKIE_NAME,
        choice,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
        secure=current_app.config.get("SESSION_COOKIE_SECURE", False),
    )
    return response


@bp.route("/following/")
@login_required
def following():
    """List posts written by the people the signed-in user follows."""
    followed_ids = select(follows.c.followed_id).where(follows.c.follower_id == current_user.id)
    query = apply_filters(published_posts().where(Post.user_id.in_(followed_ids)))
    return render_listing(
        query,
        "following.html",
        page_title="FOLLOWING",
        accent="blue",
        search_endpoint="main.following",
        empty_message="Nothing here yet — follow a few authors and their posts show up here.",
    )
