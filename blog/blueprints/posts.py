"""Creating, reading, editing and reacting to posts and comments."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from blog.extensions import db
from blog.forms import CommentForm, PostForm
from blog.listings import published_posts, render_listing
from blog.models import Comment, Post, Tag
from blog.responses import redirect_back, render_fragment, wants_fragment

bp = Blueprint("posts", __name__)


def _get_post(slug: str) -> Post:
    """Look up a post by slug, hiding other people's drafts."""
    post = db.session.scalar(select(Post).where(Post.slug == slug).options(selectinload(Post.tags)))
    if post is None:
        abort(404)
    if not post.published and post.author != current_user:
        abort(404)
    return post


def _require_author(obj: Post | Comment) -> None:
    """Abort with 403 unless the signed-in user owns ``obj``."""
    if obj.user_id != current_user.id:
        abort(403)


def _sync_tags(post: Post, names: list[str]) -> None:
    post.tags = {Tag.get_or_create(db.session, name) for name in names}


@bp.route("/posts/<slug>/")
def view(slug):
    """Show a single post with its comments. Readable without an account."""
    post = _get_post(slug)
    return render_template(
        "posts/view.html",
        post=post,
        form=CommentForm(),
        page_title=post.title,
        accent="orange",
    )


@bp.route("/posts/new/", methods=["GET", "POST"])
@login_required
def create():
    """Write a new post."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            author=current_user,
            title=form.title.data,
            body=form.body.data,
            published=form.published.data,
        )
        post.assign_slug(db.session)
        _sync_tags(post, form.tag_names())
        db.session.add(post)
        db.session.commit()
        flash("Post published." if post.published else "Draft saved.")
        return redirect(url_for("posts.view", slug=post.slug))

    return render_template(
        "posts/edit.html", form=form, post=None, page_title="NEW-POST", accent="green"
    )


@bp.route("/posts/<slug>/edit/", methods=["GET", "POST"])
@login_required
def edit(slug):
    """Edit a post you wrote."""
    post = _get_post(slug)
    _require_author(post)

    form = PostForm(obj=post)
    if form.validate_on_submit():
        retitled = post.title != form.title.data
        post.title = form.title.data
        post.body = form.body.data
        post.published = form.published.data
        if retitled:
            post.assign_slug(db.session)
        _sync_tags(post, form.tag_names())
        db.session.commit()
        flash("Post updated.")
        return redirect(url_for("posts.view", slug=post.slug))

    if not form.is_submitted():
        form.tags.data = ", ".join(sorted(tag.name for tag in post.tags))

    return render_template(
        "posts/edit.html", form=form, post=post, page_title="EDIT-POST", accent="purple"
    )


@bp.post("/posts/<slug>/delete/")
@login_required
def delete(slug):
    """Delete a post you wrote."""
    post = _get_post(slug)
    _require_author(post)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.")
    return redirect_back("main.home")


@bp.post("/posts/<slug>/like/")
@login_required
def toggle_like(slug):
    """Like or un-like a post."""
    post = _get_post(slug)
    if post.user_id == current_user.id:
        abort(403, "You cannot like your own post.")

    if post in current_user.liked_posts:
        current_user.liked_posts.remove(post)
    else:
        current_user.liked_posts.add(post)
    db.session.commit()
    return _post_actions(post)


@bp.post("/posts/<slug>/save/")
@login_required
def toggle_save(slug):
    """Add or remove a post from your reading list."""
    post = _get_post(slug)
    if post in current_user.saved_posts:
        current_user.saved_posts.remove(post)
    else:
        current_user.saved_posts.add(post)
    db.session.commit()
    return _post_actions(post)


def _post_actions(post: Post):
    """Return the refreshed action bar to htmx, or bounce a plain browser back."""
    if wants_fragment():
        return render_fragment("partials/post_actions.html", post=post)
    return redirect(url_for("posts.view", slug=post.slug))


@bp.route("/saved/")
@login_required
def saved():
    """List the posts the signed-in user has saved."""
    query = published_posts().where(Post.saved_by.any(id=current_user.id))
    return render_listing(
        query,
        "posts/saved.html",
        page_title="SAVED",
        accent="blue",
        search_endpoint="posts.saved",
        empty_message="Your reading list is empty. Use the bookmark button on any post.",
    )


@bp.post("/posts/<slug>/comments/")
@login_required
def add_comment(slug):
    """Post a comment on a post."""
    post = _get_post(slug)
    form = CommentForm()

    if not form.validate_on_submit():
        if wants_fragment():
            return render_fragment("partials/comment_form.html", post=post, form=form, oob=True)
        return render_template(
            "posts/view.html", post=post, form=form, page_title=post.title, accent="orange"
        )

    comment = Comment(author=current_user, post=post, body=form.body.data)
    db.session.add(comment)
    db.session.commit()

    if wants_fragment():
        # A fresh form goes back as an out-of-band swap so the textarea clears.
        return render_fragment(
            "partials/comment_added.html",
            post=post,
            comment=comment,
            form=CommentForm(formdata=None),
        )
    flash("Comment posted.")
    return redirect(url_for("posts.view", slug=post.slug, _anchor=f"comment-{comment.id}"))


@bp.route("/comments/<int:comment_id>/edit/", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    """Edit a comment you wrote."""
    comment = db.session.get(Comment, comment_id) or abort(404)
    _require_author(comment)

    form = CommentForm(obj=comment)
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.commit()
        flash("Comment updated.")
        return redirect(
            url_for("posts.view", slug=comment.post.slug, _anchor=f"comment-{comment.id}")
        )

    return render_template(
        "posts/edit_comment.html",
        form=form,
        comment=comment,
        page_title="EDIT-COMMENT",
        accent="purple",
    )


@bp.post("/comments/<int:comment_id>/delete/")
@login_required
def delete_comment(comment_id):
    """Delete a comment you wrote."""
    comment = db.session.get(Comment, comment_id) or abort(404)
    _require_author(comment)
    post = comment.post
    db.session.delete(comment)
    db.session.commit()

    if wants_fragment():
        # Empty body replaces the comment element; the count updates out of band.
        return render_fragment("partials/comment_removed.html", post=post)
    flash("Comment deleted.")
    return redirect(url_for("posts.view", slug=post.slug))
