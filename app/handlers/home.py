# home.py
"""Contains class defination for handler class HomeHandler."""

from base import BaseHandler
from app.database.setup import POST
from app.helpers.helper import get_page_color


class HomeHandler(BaseHandler):
    """Handler for HOME page which displays the blog posts along
       with their comments."""

    def get(self):
        """Renders HOME page after querying appropriate data for
           comments and post."""

        posts = POST.query.order_by(POST.created.desc()).limit(20)

        if self.user:
            self.render("home.html",
                        posts=posts,
                        user=self.user,
                        page_title="HOME",
                        page_color=get_page_color("HOME"))
        else:
            self.render("home.html",
                        posts=posts,
                        page_title="HOME",
                        page_color='black')
