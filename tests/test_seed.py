"""The ``flask seed`` command and the tag reuse it depends on.

These exist because `seed` was broken for a while and nothing noticed: it is the
only code path that creates several posts inside one transaction, so it is the
only one that hits `Tag.get_or_create` with a tag that is pending rather than
persisted.
"""

from sqlalchemy import func, select

from blog.cli import DEMO_COMMENTS, DEMO_FOLLOWS, DEMO_POSTS, DEMO_USERS
from blog.models import Comment, Post, Tag, User


def test_get_or_create_reuses_a_tag_pending_in_the_same_transaction(db, alice, make_post):
    """Two posts sharing a tag must end up pointing at one row, not two."""
    first = Post(author=alice, title="First post about agents", body="x")
    first.assign_slug(db.session)
    first.tags = {Tag.get_or_create(db.session, "agents")}
    db.session.add(first)

    # No commit in between: the tag from `first` is still pending here, which is
    # exactly the case the unique index used to reject.
    second = Post(author=alice, title="Second post about agents", body="y")
    second.assign_slug(db.session)
    second.tags = {Tag.get_or_create(db.session, "agents")}
    db.session.add(second)

    db.session.commit()

    assert db.session.scalar(select(func.count()).select_from(Tag)) == 1
    assert next(iter(first.tags)) is next(iter(second.tags))


def test_seed_populates_the_database(app, db):
    """The command runs end to end and inserts the whole demo dataset."""
    result = app.test_cli_runner().invoke(args=["seed"])

    assert result.exit_code == 0, result.output

    assert db.session.scalar(select(func.count()).select_from(User)) == len(DEMO_USERS)
    assert db.session.scalar(select(func.count()).select_from(Post)) == len(DEMO_POSTS)
    assert db.session.scalar(select(func.count()).select_from(Comment)) == len(DEMO_COMMENTS)

    # One tag row per distinct tag name, however many posts share it.
    expected_tags = {name.strip() for _, _, tags, *_ in DEMO_POSTS for name in tags.split(",")}
    assert db.session.scalar(select(func.count()).select_from(Tag)) == len(expected_tags)


def test_seed_builds_the_follow_graph(app, db):
    """Follows are what make the following feed and the profile counts non-empty."""
    app.test_cli_runner().invoke(args=["seed"])

    edges = {
        (user.username, followed.username)
        for user in db.session.scalars(select(User))
        for followed in user.following
    }
    assert edges == set(DEMO_FOLLOWS)


def test_seed_dates_the_posts_apart(app, db):
    """Timestamps are staggered so the listing has a real reading order."""
    app.test_cli_runner().invoke(args=["seed"])

    created = db.session.scalars(select(Post.created)).all()
    assert len(set(created)) == len(created)


def test_seed_is_idempotent(app, db):
    """A second run must not double the content."""
    app.test_cli_runner().invoke(args=["seed"])
    result = app.test_cli_runner().invoke(args=["seed"])

    assert "nothing to do" in result.output
    assert db.session.scalar(select(func.count()).select_from(User)) == len(DEMO_USERS)


def test_seed_includes_a_draft(app, db):
    """The drafts page needs something to show."""
    app.test_cli_runner().invoke(args=["seed"])

    drafts = db.session.scalars(select(Post).where(Post.published.is_(False))).all()
    assert len(drafts) == 1
