"""Shared pytest fixtures."""

import pytest

from blog import create_app
from blog.extensions import db as _db
from blog.models import Comment, Post, Tag, User

PASSWORD = "correct horse battery"


@pytest.fixture
def app():
    """An application bound to a fresh in-memory database."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(db):
    def _make(username, **kwargs):
        user = User(username=username, **kwargs)
        user.set_password(PASSWORD)
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def make_post(db):
    def _make(author, title="A perfectly ordinary title", body="Some **body** text.", **kwargs):
        post = Post(author=author, title=title, body=body, **kwargs)
        post.assign_slug(db.session)
        db.session.add(post)
        db.session.commit()
        return post

    return _make


@pytest.fixture
def make_comment(db):
    def _make(author, post, body="Nicely put."):
        comment = Comment(author=author, post=post, body=body)
        db.session.add(comment)
        db.session.commit()
        return comment

    return _make


@pytest.fixture
def alice(make_user):
    return make_user("alice")


@pytest.fixture
def bob(make_user):
    return make_user("bob")


@pytest.fixture
def log_in(client):
    """Log a user in through the real login form."""

    def _log_in(username, password=PASSWORD):
        return client.post(
            "/login/",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    return _log_in


@pytest.fixture
def htmx():
    """Headers that make a request look like it came from htmx."""
    return {"HX-Request": "true"}


__all__ = ["PASSWORD", "Tag"]
