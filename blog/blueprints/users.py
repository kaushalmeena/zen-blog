"""Public profiles, the follow graph and account settings."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from blog.extensions import db
from blog.forms import ProfileForm
from blog.listings import published_posts, render_listing
from blog.models import Post, User
from blog.responses import render_fragment, wants_fragment

bp = Blueprint("users", __name__)


def _get_user(username: str) -> User:
    user = db.session.scalar(select(User).where(User.username == username))
    if user is None:
        abort(404)
    return user


@bp.route("/u/<username>/")
def profile(username):
    """Show a user's published posts and profile details."""
    user = _get_user(username)
    query = published_posts().where(Post.user_id == user.id)
    return render_listing(
        query,
        "users/profile.html",
        profile_user=user,
        page_title=user.username,
        page_description=user.bio or f"Posts by {user.username}.",
        accent="orange",
        empty_message=f"{user.username} has not published anything yet.",
    )


@bp.route("/me/")
@login_required
def me():
    """Redirect to the signed-in user's own profile."""
    return redirect(url_for("users.profile", username=current_user.username))


@bp.route("/drafts/")
@login_required
def drafts():
    """List the signed-in user's unpublished posts."""
    query = (
        select(Post)
        .where(Post.user_id == current_user.id, Post.published.is_(False))
        .order_by(Post.updated.desc())
    )
    return render_listing(
        query,
        "users/drafts.html",
        page_title="DRAFTS",
        accent="grey",
        empty_message="No drafts. Un-tick “publish now” when writing to keep a post private.",
    )


@bp.post("/u/<username>/follow/")
@login_required
def toggle_follow(username):
    """Follow or unfollow another user."""
    user = _get_user(username)
    if user.id == current_user.id:
        abort(403, "You cannot follow yourself.")

    if user in current_user.following:
        current_user.following.remove(user)
    else:
        current_user.following.add(user)
    db.session.commit()

    if wants_fragment():
        return render_fragment("partials/follow_button.html", profile_user=user)
    return redirect(url_for("users.profile", username=user.username))


@bp.route("/u/<username>/followers/")
def followers(username):
    """List the people following ``username``."""
    user = _get_user(username)
    return render_template(
        "users/people.html",
        profile_user=user,
        people=sorted(user.followers, key=lambda person: person.username),
        heading="FOLLOWERS",
        page_title=f"{user.username.upper()} · FOLLOWERS",
        accent="blue",
    )


@bp.route("/u/<username>/following/")
def following(username):
    """List the people ``username`` follows."""
    user = _get_user(username)
    return render_template(
        "users/people.html",
        profile_user=user,
        people=sorted(user.following, key=lambda person: person.username),
        heading="FOLLOWING",
        page_title=f"{user.username.upper()} · FOLLOWING",
        accent="blue",
    )


@bp.route("/settings/", methods=["GET", "POST"])
@login_required
def settings():
    """Edit the signed-in user's public profile."""
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.bio = (form.bio.data or "").strip()
        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for("users.profile", username=current_user.username))

    return render_template("users/settings.html", form=form, page_title="SETTINGS", accent="purple")
