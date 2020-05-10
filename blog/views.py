"""Contains views for blog app."""

from blog import db, login_manager
from blog.forms import CommentForm, PostForm, SignInForm, SignUpForm
from blog.models import Comment, Post, User, func, likes

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import current_user, login_required, login_user, logout_user

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
    """HOME page which displays the blog posts."""
    query = request.args.get("query", "", type=str)
    page = request.args.get("page", 1, type=int)

    pagination = Post.query

    if query:
        pagination = pagination.filter(Post.title.ilike("%" + query + "%"))

    pagination = pagination.order_by(Post.created.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )

    template_params = {
        "pagination": pagination,
        "query": query,
        "page-route": "app.home",
        "page_title": "HOME",
    }

    if current_user.is_authenticated:
        template_params["user"] = current_user
        template_params["page_color"] = "red"
    else:
        template_params["page_color"] = "black"

    return render_template("home.html", **template_params)


@app_blueprint.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    """SIGN-IN page which allows users to login."""
    if current_user.is_authenticated:
        flash("You have already logged in.")
        return redirect(url_for("app.home"))
    else:
        form = SignInForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()

            if user and user.check_password(password=form.password.data):
                login_user(user)
                next_page = request.args.get("next")
                flash("Sucessfully logged in.")
                return redirect(next_page or url_for("app.home"))

            flash("Invalid username or password.")

        return render_template(
            "sign-in.html", form=form, page_title="SIGN-IN", page_color="black",
        )


@app_blueprint.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """SIGN-UP page which allows users to register."""
    if current_user.is_authenticated:
        flash("You have alredy logged in.")
        return redirect(url_for("app.home"))
    else:
        form = SignUpForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None:
                user = User(username=form.username.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Sucessfully registered.")
                flash("Sucessfully logged in.")
                return redirect(url_for("app.home"))

            flash("A user already exists with that email address.")

        return render_template(
            "sign-up.html", form=form, page_title="SIGN-UP", page_color="black",
        )


@app_blueprint.route("/new-post", methods=["GET", "POST"])
@login_required
def new_post():
    """NEW-POST page which allows users to create new blog posts."""
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            user=current_user, title=form.data.get("title"), body=form.data.get("body")
        )
        db.session.add(post)
        db.session.commit()
        flash("Post sucessfully created.")
        return redirect(url_for("app.home"))

    return render_template(
        "post.html",
        user=current_user,
        form=form,
        page_title="NEW-POST",
        page_color="green",
    )


@app_blueprint.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """EDIT-POST page helps in editing of blog post."""
    post = Post.query.get(post_id)

    if post:
        form = PostForm(obj=post)
        if form.validate_on_submit():
            post.title = form.data.get("title")
            post.body = form.data.get("body")
            db.session.add(post)
            db.session.commit()
            flash("Post sucessfully edited.")
            return redirect(url_for("app.view_post", post_id=post_id))

        return render_template(
            "post.html",
            user=current_user,
            post=post,
            form=form,
            page_title="EDIT-POST",
            page_color="purple",
        )
    else:
        next_page = request.headers.get("Referer")
        flash("Blog post not found.")
        return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    """DELETE-POST handler helps in deleting of blog post."""
    post = Post.query.get(post_id)

    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post sucessfully deleted.")
        return redirect(url_for("app.home"))
    else:
        flash("Blog post not found.")
        next_page = request.headers.get("Referer")
        return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    """EDIT-COMMENT page helps in editing of comment."""
    comment = Comment.query.get(comment_id)

    if comment:
        form = CommentForm(obj=comment)
        if form.validate_on_submit():
            comment.body = form.data.get("body")
            db.session.add(comment)
            db.session.commit()
            flash("Comment sucessfully edited.")
            return redirect(url_for("app.view_post", post_id=comment.post_id))

        return render_template(
            "comment.html",
            user=current_user,
            form=form,
            page_title="EDIT-COMMENT",
            page_color="purple",
        )
    else:
        next_page = request.headers.get("Referer")
        flash("Comment not found.")
        return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/comment/<int:comment_id>/delete")
@login_required
def delete_comment(comment_id):
    """DELETE-COMMENT handler helps in deleting of comment."""
    comment = Comment.query.get(comment_id)

    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment sucessfully deleted.")
    else:
        flash("Comment not found.")

    next_page = request.headers.get("Referer")
    return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def view_post(post_id):
    """VIEW-POST page displays post information alongwith comments."""
    post = Post.query.get(post_id)

    if post:
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(user=current_user, post=post, body=form.data.get("body"))
            db.session.add(comment)
            db.session.commit()
            flash("Comment sucessfully posted.")

        return render_template(
            "view-post.html",
            user=current_user,
            post=post,
            form=form,
            page_title="VIEW-POST",
            page_color="purple",
        )
    else:
        next_page = request.headers.get("Referer")
        flash("Blog post not found.")
        return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>/like")
@login_required
def like_post(post_id):
    """Handle LIKING of a blog post."""
    post = Post.query.get(post_id)

    if post:
        if not post.user_id == current_user.id:
            if post not in current_user.liked_posts:
                current_user.liked_posts.append(post)
                db.session.add(current_user)
                db.session.commit()
                flash("Post sucessfully liked.")
        else:
            flash("You can't like your own post.")
    else:
        flash("Blog post not found.")

    next_page = request.headers.get("Referer")
    return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>/dislike")
@login_required
def dislike_post(post_id):
    """Handle DISLIKING of a blog post."""
    post = Post.query.get(post_id)

    if post:
        if not post.user_id == current_user.id:
            if post in current_user.liked_posts:
                current_user.liked_posts.remove(post)
                db.session.add(current_user)
                db.session.commit()
                flash("Post sucessfully disliked.")
        else:
            flash("You can't dislike your own post.")
    else:
        flash("Blog post not found.")

    next_page = request.headers.get("Referer")
    return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>/save")
@login_required
def save_post(post_id):
    """Handle SAVING of a blog post."""
    post = Post.query.get(post_id)

    if post:
        if not post.user_id == current_user.id:
            if post not in current_user.saved_posts:
                current_user.saved_posts.append(post)
                db.session.add(current_user)
                db.session.commit()
                flash("Post sucessfully saved.")
        else:
            flash("You can't save your own post.")
    else:
        flash("Blog post not found.")

    next_page = request.headers.get("Referer")
    return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/post/<int:post_id>/unsave")
@login_required
def unsave_post(post_id):
    """Handle UN-SAVING of a blog post."""
    post = Post.query.get(post_id)

    if post:
        if not post.user_id == current_user.id:
            if post in current_user.saved_posts:
                current_user.saved_posts.remove(post)
                db.session.add(current_user)
                db.session.commit()
                flash("Post sucessfully unsaved.")
        else:
            flash("You can't unsave your own post.")
    else:
        flash("Blog post not found.")

    next_page = request.headers.get("Referer")
    return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/saved_posts")
@login_required
def saved_posts():
    """SAVED-POSTS page which displays the saved blog posts."""
    page = request.args.get("page", 1, type=int)

    pagination = current_user.saved_posts.order_by(Post.created.desc()).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False
    )

    return render_template(
        "saved-posts.html",
        pagination=pagination,
        user=current_user,
        page_route="app.saved_posts",
        page_title="SAVED-POSTS",
        page_color="blue",
    )


@app_blueprint.route("/user/<int:user_id>")
@login_required
def view_user(user_id):
    """VIEW-USER page which displays posts of specified user."""
    page = request.args.get("page", 1, type=int)

    user = User.query.get(user_id)

    if user:
        pagination = (
            Post.query.filter_by(user_id=user_id)
            .order_by(Post.created.desc())
            .paginate(page, current_app.config["POSTS_PER_PAGE"], False)
        )

        post_count = (
            db.session.query(Post, func.count().label("number"))
            .filter_by(user_id=user_id)
            .first()
            .number
        )
        like_count = (
            db.session.query(Post, func.count().label("number"))
            .join(likes, Post.id == likes.c.post_id)
            .filter(Post.user_id == user_id, likes.c.user_id != user_id)
            .first()
            .number
        )

        return render_template(
            "user.html",
            pagination=pagination,
            post_count=post_count,
            like_count=like_count,
            user=current_user,
            username=user.username,
            page_route="app.view_user",
            page_title="VIEW-USER",
            page_color="orange",
        )
    else:
        flash("User not found.")
        next_page = request.headers.get("Referer")

        return redirect(next_page or url_for("app.home"))


@app_blueprint.route("/profile")
@login_required
def profile():
    """PROFILE page which displays posts of current logged in user."""
    page = request.args.get("page", 1, type=int)

    pagination = (
        Post.query.filter_by(user_id=current_user.id)
        .order_by(Post.created.desc())
        .paginate(page, current_app.config["POSTS_PER_PAGE"], False)
    )

    post_count = (
        db.session.query(Post, func.count().label("number"))
        .filter_by(user_id=current_user.id)
        .first()
        .number
    )
    like_count = (
        db.session.query(Post, func.count().label("number"))
        .join(likes, Post.id == likes.c.post_id)
        .filter(Post.user_id == current_user.id, likes.c.user_id != current_user.id)
        .first()
        .number
    )

    return render_template(
        "user.html",
        pagination=pagination,
        post_count=post_count,
        like_count=like_count,
        user=current_user,
        username=current_user.username,
        page_route="app.profile",
        page_title="PROFILE",
        page_color="orange",
    )


@app_blueprint.route("/sign-out")
@login_required
def sign_out():
    """Logout the user and redirects to HOME page."""
    logout_user()
    flash("Sucessfully logged out.")
    return redirect(url_for("app.home"))


def error400(exception=None):
    """Error 404 page."""
    template_params = {"page_title": "ERROR", "page_color": "grey"}

    if current_user.is_authenticated:
        template_params["user"] = current_user

    return render_template("400.html", **template_params), 400


def error404(exception=None):
    """Error 404 page."""
    template_params = {"page_title": "ERROR", "page_color": "grey"}

    if current_user.is_authenticated:
        template_params["user"] = current_user

    return render_template("404.html", **template_params), 404


def error500(exception=None):
    """Error 500 page."""
    template_params = {"page_title": "ERROR", "page_color": "grey"}

    if current_user.is_authenticated:
        template_params["user"] = current_user

    return render_template("500.html", **template_params), 500
