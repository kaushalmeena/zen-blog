#user.py
"""Contains class defination for model class USER."""

from google.appengine.ext import db
from helper.helper import users_key, make_password_hash, validate_password

class USER(db.Model):
    """Provides way to store blog's user related information."""

    username = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    name = db.StringProperty()
    email = db.StringProperty()
    liked_post = db.StringListProperty(default=[])

    @classmethod
    def by_id(cls, user_id):
        """Returns a list of USER entities which have id same as
           passed parameter."""

        return USER.get_by_id(user_id, parent = users_key())

    @classmethod
    def by_username(cls, username):
        """Returns a list of USER entities which have username same
           as passed parameter."""

        user = USER.all().filter('username =', username).get()
        return user

    @classmethod
    def register(cls, username, password, name = None, email = None):
        """Create a new USER entitity using passed parameters."""

        password_hash = make_password_hash(username, password)
        return USER(parent = users_key(),
                    username = username,
                    password_hash = password_hash,
                    name = name,
                    email = email)
    @classmethod
    def login(cls, username, password):
        """Validates the user login information."""
        user = cls.by_username(username)
        if user and validate_password(username,
                                      password,
                                      user.password_hash):
            return user
