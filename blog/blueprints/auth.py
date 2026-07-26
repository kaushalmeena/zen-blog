"""Login, registration and logout."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from blog.extensions import db, login_manager
from blog.forms import LoginForm, RegisterForm
from blog.models import User

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Reload the signed-in user from the session cookie."""
    return db.session.get(User, int(user_id)) if user_id else None


def _safe_next() -> str | None:
    """Return the ``next`` parameter only when it points at this site.

    Guards against an open redirect: without this an attacker could send
    ``/login/?next=https://evil.example`` and bounce a freshly authenticated
    user off-site.

    Asking ``urlparse`` whether it found a host is not enough on its own. It
    reports a netloc only for *exactly* two leading slashes, whereas a browser
    skips any run of slashes or backslashes and reads whatever follows as the
    host — so ``////evil.example`` looks like an ordinary path here and
    navigates off-site there. Hence the explicit second-character check, and the
    rejection of the whitespace browsers strip before parsing.
    """
    target = request.args.get("next")
    if not target or target.strip() != target or {"\t", "\r", "\n"} & set(target):
        return None
    # A single leading slash, and the next character must not start an authority.
    if not target.startswith("/") or target[1:2] in {"/", "\\"}:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc:
        return None
    return target


@bp.route("/login/", methods=["GET", "POST"])
def login():
    """Authenticate an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.username == form.username.data))
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Logged in as {user.username}.")
            return redirect(_safe_next() or url_for("main.home"))
        flash("Invalid username or password.")

    return render_template("auth/login.html", form=form, page_title="LOGIN", accent="green")


@bp.route("/register/", methods=["GET", "POST"])
def register():
    """Register a new user and sign them in."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
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

    return render_template("auth/register.html", form=form, page_title="REGISTER", accent="green")


@bp.post("/logout/")
@login_required
def logout():
    """Sign the current user out.

    POST-only so a stray link, image or prefetch cannot end someone's session.
    """
    logout_user()
    flash("Logged out.")
    return redirect(url_for("main.home"))
