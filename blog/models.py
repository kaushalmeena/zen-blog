# comment.py
"""Python script for comment model."""

from blog import db

from flask_login import UserMixin

from sqlalchemy.sql import func

from werkzeug.security import check_password_hash, generate_password_hash

# Like association table
likes = db.Table(
    "likes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)

# Save association table
saves = db.Table(
    "saves",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    """Model to store blog's user related information."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    posts = db.relationship("Post", backref="user")
    comments = db.relationship("Comment", backref="user")
    liked_posts = db.relationship(
        "Post", secondary=likes, backref="liked_by", lazy="dynamic"
    )
    saved_posts = db.relationship(
        "Post", secondary=saves, backref="saved_by", lazy="dynamic",
    )

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """Model to store blog's post related information."""

    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    comments = db.relationship("Comment", backref="post")
    created = db.Column(db.DateTime, server_default=func.now())


class Comment(db.Model):
    """Model to store blog's comment related information."""

    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    body = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, server_default=func.now())
