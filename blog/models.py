"""ORM models for the blog."""

from __future__ import annotations

from datetime import UTC, datetime

from flask_login import UserMixin
from slugify import slugify
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from blog.extensions import db
from blog.rendering import excerpt, reading_time, render_markdown


def utcnow() -> datetime:
    """Return the current UTC time as an aware datetime."""
    return datetime.now(UTC)


likes = Table(
    "likes",
    db.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("post_id", ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
)

saves = Table(
    "saves",
    db.metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("post_id", ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
)

follows = Table(
    "follows",
    db.metadata,
    Column("follower_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("followed_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
)

post_tags = Table(
    "post_tags",
    db.metadata,
    Column("post_id", ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class User(UserMixin, db.Model):
    """A registered author."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    bio: Mapped[str] = mapped_column(String(280), default="")
    created: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    posts: Mapped[list[Post]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    liked_posts: Mapped[set[Post]] = relationship(
        secondary=likes, back_populates="liked_by", collection_class=set
    )
    saved_posts: Mapped[set[Post]] = relationship(
        secondary=saves, back_populates="saved_by", collection_class=set
    )
    following: Mapped[set[User]] = relationship(
        secondary=follows,
        primaryjoin=id == follows.c.follower_id,
        secondaryjoin=id == follows.c.followed_id,
        back_populates="followers",
        collection_class=set,
    )
    followers: Mapped[set[User]] = relationship(
        secondary=follows,
        primaryjoin=id == follows.c.followed_id,
        secondaryjoin=id == follows.c.follower_id,
        back_populates="following",
        collection_class=set,
    )

    def set_password(self, password: str) -> None:
        """Store a salted hash of ``password``."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return whether ``password`` matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"<User {self.username}>"


class Post(db.Model):
    """A blog post written by a :class:`User`."""

    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(280), unique=True, index=True)
    body: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    author: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list[Comment]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Comment.created",
    )
    liked_by: Mapped[set[User]] = relationship(
        secondary=likes, back_populates="liked_posts", collection_class=set
    )
    saved_by: Mapped[set[User]] = relationship(
        secondary=saves, back_populates="saved_posts", collection_class=set
    )
    tags: Mapped[set[Tag]] = relationship(
        secondary=post_tags, back_populates="posts", collection_class=set
    )

    __table_args__ = (Index("ix_post_published_created", "published", "created"),)

    @property
    def html(self) -> str:
        """Return the post body rendered as sanitized HTML."""
        return render_markdown(self.body)

    @property
    def summary(self) -> str:
        """Return a short plain-text teaser for listings and feeds."""
        return excerpt(self.body)

    @property
    def reading_time(self) -> int:
        """Return the estimated reading time in whole minutes (minimum 1)."""
        return reading_time(self.body)

    def assign_slug(self, session) -> None:
        """Derive a unique slug from the current title, suffixing on collisions."""
        base = slugify(self.title, max_length=200) or "post"
        candidate, suffix = base, 2
        # A pending post has no id yet, and `Post.id != None` compiles to
        # `post.id != NULL`, which is never true — so the self-exclusion clause is
        # only added once there is an id to exclude.
        while True:
            query = select(Post.id).where(Post.slug == candidate)
            if self.id is not None:
                query = query.where(Post.id != self.id)
            with session.no_autoflush:
                clash = session.scalar(query)
            if clash is None:
                break
            candidate, suffix = f"{base}-{suffix}", suffix + 1
        self.slug = candidate

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"<Post {self.slug}>"


class Comment(db.Model):
    """A comment left on a :class:`Post`."""

    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    author: Mapped[User] = relationship(back_populates="comments")
    post: Mapped[Post] = relationship(back_populates="comments")

    @property
    def html(self) -> str:
        """Return the comment body rendered as sanitized HTML.

        Comments keep soft line breaks: people type them casually and expect
        Enter to show up as a new line.
        """
        return render_markdown(self.body, soft_breaks=True)

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"<Comment {self.id}>"


class Tag(db.Model):
    """A topic label attached to posts."""

    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(48), unique=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    posts: Mapped[set[Post]] = relationship(
        secondary=post_tags, back_populates="tags", collection_class=set
    )

    @classmethod
    def get_or_create(cls, session, name: str) -> Tag:
        """Return the tag named ``name``, creating it if it does not exist yet."""
        slug = slugify(name, max_length=64)
        # no_autoflush: this runs while a Post is still being assembled, and an
        # autoflush here would try to persist that half-built object.
        with session.no_autoflush:
            tag = session.scalar(select(cls).where(cls.slug == slug))
        if tag is None:
            # Because that lookup cannot autoflush, a tag added earlier in the same
            # transaction is invisible to it. Without this second pass, two posts
            # sharing a tag insert it twice and the unique index rejects the commit.
            tag = next(
                (
                    pending
                    for pending in session.new
                    if type(pending) is cls and pending.slug == slug
                ),
                None,
            )
        if tag is None:
            tag = cls(name=name.strip().lower(), slug=slug)
            session.add(tag)
        return tag

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"<Tag {self.slug}>"


# Aggregate counts are attached after mapping so the subqueries can reference the
# mapped tables directly. Post counts load with the row because every listing shows
# them; user counts are deferred since only profile pages ask for them.
#
# Each subquery calls correlate() explicitly. Without it SQLAlchemy auto-correlates
# any table the enclosing query also mentions, which strips the subquery's own FROM
# clause the moment one of these is loaded from a query that touches the same table
# (for example lazy-loading User.liked_posts, which itself joins `likes`).
Post.like_count = column_property(
    select(func.count())
    .select_from(likes)
    .where(likes.c.post_id == Post.id)
    .correlate(Post.__table__)
    .scalar_subquery()
    .label("like_count")
)
Post.comment_count = column_property(
    select(func.count())
    .select_from(Comment.__table__)
    .where(Comment.post_id == Post.id)
    .correlate(Post.__table__)
    .scalar_subquery()
    .label("comment_count")
)
User.post_count = column_property(
    select(func.count())
    .select_from(Post.__table__)
    .where(Post.user_id == User.id, Post.published.is_(True))
    .correlate(User.__table__)
    .scalar_subquery()
    .label("post_count"),
    deferred=True,
)
User.like_count = column_property(
    select(func.count())
    .select_from(likes.join(Post.__table__, likes.c.post_id == Post.id))
    .where(Post.user_id == User.id)
    .correlate(User.__table__)
    .scalar_subquery()
    .label("like_count"),
    deferred=True,
)
User.follower_count = column_property(
    select(func.count())
    .select_from(follows)
    .where(follows.c.followed_id == User.id)
    .correlate(User.__table__)
    .scalar_subquery()
    .label("follower_count"),
    deferred=True,
)
User.following_count = column_property(
    select(func.count())
    .select_from(follows)
    .where(follows.c.follower_id == User.id)
    .correlate(User.__table__)
    .scalar_subquery()
    .label("following_count"),
    deferred=True,
)
