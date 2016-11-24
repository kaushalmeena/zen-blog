#post.py
"""Contains class defination for model class POST."""

from google.appengine.ext import db

from helper.helper import posts_key

class POST(db.Model):
    """Provides way to store blog's post related information."""

    user_id = db.StringProperty(required = True)
    post_subject = db.StringProperty(required = True)
    post_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    @classmethod
    def by_id(cls, post_id):
        """Returns a list of POST entities which have post_id same
           as passed parameter."""
        return POST.get_by_id(post_id, parent = posts_key())

    @classmethod
    def by_user_id(cls, user_id):
        """Returns a list of POST entities which have user_id same
           as passed parameter."""

        posts = db.GqlQuery("SELECT * FROM POST WHERE user_id = '%s'"
                            % user_id)
        return posts

    @classmethod
    def create_post(cls, user_id, post_subject, post_content):
        """Creates a new POST entitiy using passed parameters."""

        return POST(parent = posts_key(),
                    user_id = user_id,
                    post_subject = post_subject,
                    post_content = post_content)
