# home.py
"""Contains class defination for handler class HomeHandler."""

from base import BaseHandler
from app.database.setup import POST


class HomeHandler(BaseHandler):
    """Handler for HOME page which displays the blog posts along
       with their comments."""

    def get(self):
        """Renders HOME page after querying appropriate data for
           comments and post."""

        posts = self.session.query(POST).order_by(
            POST.created.desc()).limit(20).all()

        self.render("home.html", posts=posts)
