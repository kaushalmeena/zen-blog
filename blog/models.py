# comment.py
"""Python script for comment model."""


from blog.db import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Model,
    String,
    Table,
    Text,
    relationship,
)

from sqlalchemy.sql import func

from werkzeug.security import check_password_hash, generate_password_hash


# Like association table
likes = Table(
    "likes",
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("post_id", Integer, ForeignKey("post.id")),
)


class User(Model):
    """Model to store blog's user related information."""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True, unique=True)
    posts = relationship("POST", backref="user")
    liked_posts = relationship("POST", secondary=likes, backref="liked_by")

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)


class Post(Model):
    """Model to store blog's post related information."""

    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String(256), nullable=False)
    body = Column(Text, nullable=False)
    comments = relationship("COMMENT", backref="post")
    created = Column(DateTime, server_default=func.now())


class Comment(Model):
    """Model to store blog's comment related information."""

    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    post_id = Column(Integer, ForeignKey("post.id"))
    name = Column(String(32), nullable=False)
    email = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now())
