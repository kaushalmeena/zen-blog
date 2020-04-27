# new_post.py
"""Contains class defination for handler class NewPostHandler."""

from base import BaseHandler
from app.database.setup import POST, COMMENT


class NewPostHandler(BaseHandler):
    """Handler for NEW-POST page which allows users to create
       new blog posts."""

    def get(self):
        """Renders NEW-POST page if user has logged in otherwise
           renders SIGN-IN page."""

        if self.user:
            self.render("new-post.html",
                        username=self.user.username,
                        page_title="NEW-POST")
        else:
            self.redirect("/sign-in")

    def post(self):
        """Validates the posted blog post's form information for
           errors and accordingly creates the appropriate entities
           and redirects the page."""

        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = POST.create_post(user_id=str(self.user.id),
                                    subject=subject,
                                    content=content)
            post.put()
            self.redirect("/post/" + str(post.id))
        else:
            self.render("new-post.html",
                        err_msg="Both SUBJECT and CONTENT can't be left empty.",
                        subject=subject,
                        content=content,
                        page_title="NEW-POST")
