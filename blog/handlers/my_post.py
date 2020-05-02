# my_post.py
"""Contains class defination for handler class MyPostHandler."""

from base import BaseHandler
from app.database.setup import POST


class MyPostHandler(BaseHandler):
    """Handler for MY-POST page which show users their own blog posts."""

    def get(self):
        """Renders MY-POST page if user has logged in after querying
           appropriate data otherwise renders SIGN-IN page."""

        if self.user:
            posts = self.session.query(POST).filter_by(user_id=self.user.id)
            self.render("my-post.html", posts=posts)
        else:
            self.redirect("/sign-in")
