# edit_post.py
"""Contains class defination for handler class EditPostHandler."""

from base import BaseHandler
from app.database.setup import POST


class EditPostHandler(BaseHandler):
    """Handler for EDITING a blog post of user."""

    def get(self, post_id):
        """Renders EDIT-POST page if user has logged in after querying
           appropriate data otherwise redirects to SIGN-IN page."""

        if self.user:
            post = POST.by_id(int(post_id))
            if post:
                if post.user_id == str(self.user.id):
                    self.render("edit-post.html",
                                subject=post.subject,
                                content=post.content,
                                username=self.user.username,
                                page_title="EDIT-POST")
                else:
                    page_error = "ERROR 500 : You don't own this post."
                    self.render("error.html",
                                page_error=page_error,
                                username=self.user.username,
                                page_title="ERROR")
            else:
                page_error = "ERROR 404 : Blog post not found."
                self.render("error.html",
                            page_error=page_error,
                            username=self.user.username,
                            page_title="ERROR")

        else:
            self.redirect("/sign-in")

    def post(self, post_id):
        """Checks the posted blog post's form information for
           errors and accordingly changes the values of appropriate
           entities and redirects the page."""

        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = POST.by_id(int(post_id))

            if post.user_id == str(self.user.id):
                post.subject = subject
                post.content = content
                post.put()
                self.redirect("/my-post")
            else:
                page_error = "ERROR 500 : You don't own this post."
                self.render("error.html",
                            page_error=page_error,
                            username=self.user.username,
                            page_title="ERROR")

        else:
            err_msg = "Both SUBJECT and CONTENT can't be left empty."
            self.render("edit-post.html",
                        err_msg=err_msg,
                        subject=subject,
                        content=content,
                        page_title="EDIT-POST")
