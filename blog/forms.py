"""Contains forms for blog app."""
from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class SignInForm(FlaskForm):
    """User Login Form."""

    username = StringField("USERNAME :", validators=[DataRequired()])
    password = PasswordField("PASSWORD :", validators=[DataRequired()])


class SignUpForm(FlaskForm):
    """User Signup Form."""

    username = StringField("USERNAME", validators=[DataRequired()])
    password = PasswordField(
        "PASSWORD",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must consists of 6-30 characters."),
        ],
    )
    confirm = PasswordField(
        "Confirm Your PASSWORD",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
