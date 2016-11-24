#comment.py
"""Contains class defination for model class COMMENT."""

from google.appengine.ext import db
from helper.helper import comments_key

class COMMENT(db.Model):
    """Provides way to store blog's comment related information."""

    user_id = db.StringProperty(required = True)
    post_id = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    email = db.StringProperty(required = True)
    comment_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, comment_id):
        """Returns a list of COMMENT entities which have comment_id
        same as passed parameter."""

        return COMMENT.get_by_id(comment_id, parent = comments_key())

    @classmethod
    def by_post_id(cls, post_id):
        """Returns a list of COMMENT entities which have comment_id
        same as passed parameter."""

        comments = db.GqlQuery("SELECT * FROM COMMENT WHERE post_id = '%s'"
                               % post_id)
        return comments

    @classmethod
    def by_user_id(cls, user_id):
        """Returns a list of COMMENT entities which have user_id
           same as passed parameter."""

        comments = db.GqlQuery("SELECT * FROM COMMENT WHERE user_id = '%s'"
                               % user_id)
        return comments

    @classmethod
    def create_comment(cls,
                       user_id,
                       post_id,
                       name,
                       email,
                       comment_content):
        """Creates a new COMMENT entitiy using passed parameters."""

        return COMMENT(parent = comments_key(),
                       user_id = user_id,
                       post_id = post_id,
                       name = name,
                       email = email,
                       comment_content = comment_content)
