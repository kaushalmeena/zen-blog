"""Sign-in, sign-up and sign-out."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from blog.extensions import db, login_manager
from blog.forms import SignInForm, SignUpForm
from blog.models import User

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Reload the signed-in user from the session cookie."""
    return db.session.get(User, int(user_id)) if user_id else None


def _safe_next() -> str | None:
    """Return the ``next`` parameter only when it points at this site.

    Guards against an open redirect: without the host check an attacker could
    send ``/sign-in/?next=https://evil.example`` and bounce a freshly
    authenticated user off-site.
    """
    target = request.args.get("next")
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    return target if target.startswith("/") else None


@bp.route("/sign-in/", methods=["GET", "POST"])
def sign_in():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = SignInForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.username == form.username.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Signed in as {user.username}.")
            return redirect(_safe_next() or url_for("main.home"))
        flash("Invalid username or password.")

    return render_template("auth/sign_in.html", form=form, page_title="SIGN-IN", accent="green")


@bp.route("/sign-up/", methods=["GET", "POST"])
def sign_up():
    """Register a new user and sign them in."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = SignUpForm()
    if form.validate_on_submit():
        taken = db.session.scalar(select(User.id).where(User.username == form.username.data))
        if taken:
            form.username.errors.append("That username is already taken.")
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f"Welcome, {user.username}! Your account is ready.")
            return redirect(url_for("main.home"))

    return render_template("auth/sign_up.html", form=form, page_title="SIGN-UP", accent="green")


@bp.post("/sign-out/")
@login_required
def sign_out():
    """Sign the current user out.

    POST-only so a stray link, image or prefetch cannot end someone's session.
    """
    logout_user()
    flash("Signed out.")
    return redirect(url_for("main.home"))
