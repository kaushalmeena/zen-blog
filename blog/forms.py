"""Contains forms for blog app."""
from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length


class SignInForm(FlaskForm):
    """User sign-in form."""

    username = StringField("USERNAME :", validators=[DataRequired()])
    password = PasswordField("PASSWORD :", validators=[DataRequired()])


class SignUpForm(FlaskForm):
    """User sign-up form."""

    username = StringField("USERNAME :", validators=[DataRequired()])
    password = PasswordField(
        "PASSWORD :",
        validators=[
            DataRequired(),
            Length(min=6, max=30, message="Password must consists of 6-30 characters."),
        ],
    )
    confirm = PasswordField(
        "Confirm PASSWORD :",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )


class PostForm(FlaskForm):
    """Post add/edit form."""

    title = StringField(
        "TITLE :",
        validators=[
            DataRequired(),
            Length(min=6, max=250, message="Title must consists of 6-250 characters."),
        ],
    )
    body = TextAreaField("BODY :", validators=[DataRequired()], render_kw={"rows": 8})


class CommentForm(FlaskForm):
    """Comment add/edit form."""

    body = TextAreaField(
        "COMMENT :", validators=[DataRequired()], render_kw={"rows": 4}
    )
