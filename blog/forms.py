"""WTForms definitions used by the blog's views."""

from __future__ import annotations

from flask_wtf import FlaskForm
from slugify import slugify
from wtforms import BooleanField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

MAX_TAGS = 5

USERNAME_PATTERN = r"^[A-Za-z0-9_-]+$"
USERNAME_MESSAGE = "Username may only contain letters, numbers, hyphens and underscores."


class LoginForm(FlaskForm):
    """Credentials for an existing account."""

    username = StringField("USERNAME", validators=[DataRequired()])
    password = PasswordField("PASSWORD", validators=[DataRequired()])
    remember = BooleanField("REMEMBER ME")


class RegisterForm(FlaskForm):
    """Registration details for a new account."""

    username = StringField(
        "USERNAME",
        validators=[
            DataRequired(),
            Length(min=3, max=32, message="Username must be 3-32 characters."),
            Regexp(USERNAME_PATTERN, message=USERNAME_MESSAGE),
        ],
    )
    password = PasswordField(
        "PASSWORD",
        validators=[
            DataRequired(),
            Length(min=8, max=128, message="Password must be at least 8 characters."),
        ],
    )
    confirm = PasswordField(
        "CONFIRM PASSWORD",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )


class PostForm(FlaskForm):
    """Create or edit a post."""

    title = StringField(
        "TITLE",
        validators=[
            DataRequired(),
            Length(min=6, max=250, message="Title must be 6-250 characters."),
        ],
    )
    body = TextAreaField(
        "BODY (MARKDOWN)",
        validators=[DataRequired()],
        render_kw={"rows": 16, "placeholder": "Markdown is supported: **bold**, `code`, > quotes…"},
    )
    tags = StringField(
        "TAGS",
        validators=[Optional(), Length(max=120)],
        render_kw={"placeholder": "comma,separated,topics"},
    )
    published = BooleanField("PUBLISH NOW", default=True)

    def tag_names(self) -> list[str]:
        """Return the tag field parsed into at most :data:`MAX_TAGS` unique names."""
        seen: dict[str, str] = {}
        for raw in (self.tags.data or "").split(","):
            name = raw.strip().lower()
            if not name:
                continue
            slug = slugify(name, max_length=64)
            if slug and slug not in seen:
                seen[slug] = name
            if len(seen) == MAX_TAGS:
                break
        return list(seen.values())


class CommentForm(FlaskForm):
    """Add or edit a comment."""

    body = TextAreaField(
        "COMMENT",
        validators=[DataRequired(), Length(max=2000)],
        render_kw={"rows": 4, "placeholder": "Say something…"},
    )


class ProfileForm(FlaskForm):
    """Edit the signed-in user's public profile."""

    bio = TextAreaField(
        "BIO",
        validators=[Optional(), Length(max=280)],
        render_kw={"rows": 3, "placeholder": "A sentence or two about yourself."},
    )
