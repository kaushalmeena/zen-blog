"""Contains views for blog app."""

from blog import db, login_manager
from blog.forms import SignInForm
from blog.models import Post, User

from flask import Blueprint, flash, redirect, request, render_template, url_for

from flask_login import (
    login_required,
    logout_user,
    current_user,
    login_user,
)

# Initialise Blueprint
app_blueprint = Blueprint("app", __name__)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash("You must be logged in to view that page.")
    return redirect("/login")


@app_blueprint.route("/")
def home():
    """HOME page which displays the blog posts along with their comments."""
    posts = Post.query.order_by(Post.created.desc()).limit(20).all()

    return render_template(
        "home.html", posts=posts, page_title="HOME", page_color="red"
    )


@app_blueprint.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    """SIGN-IN page which allows users to login."""
    if current_user.is_authenticated:
        flash("You have alredy logged in.")
        return redirect(url_for("app.home"))
    else:
        form = SignInForm()

        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()

            if existing_user is None:
                user = User(username=form.username.data,)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("home"))

            flash("A user already exists with that email address.")

        return render_template(
            "sign-in.html", form=form, page_title="SIGN-IN", page_color="purple",
        )


@app_blueprint.route("/sign-up")
def sign_up():
    """SIGN-UP page which allows users to register."""
    posts = Post.query.order_by(Post.created.desc()).limit(20).all()

    return render_template(
        "home.html", posts=posts, page_title="HOME", page_color="red"
    )


def error400(exception=None):
    """Error 404 page."""
    return render_template("400.html", title="error 400"), 400


def error404(exception=None):
    """Error 404 page."""
    return render_template("404.html", title="error 404"), 404


def error500(exception=None):
    """Error 500 page."""
    return render_template("500.html", title="error 500"), 500
