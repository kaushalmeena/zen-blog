# edit_comment.py
"""Contains class defination for handler class EditCommentHandler."""

from base import BaseHandler
from app.database.setup import COMMENT
from app.helpers.helper import valid_email


class EditCommentHandler(BaseHandler):
    """Handler for EDITING a comment post of user."""

    def get(self, comment_id):
        """Renders EDIT-COMMENT page if user has logged in after
           querying appropriate data otherwise redirects to SIGN-IN page."""

        if self.user:
            comment = COMMENT.by_id(int(comment_id))
            if comment:
                if comment.user_id == str(self.user.id):
                    self.render("edit-comment.html",
                                input_name=comment.name,
                                input_email=comment.email,
                                content=comment.content,
                                post_id=comment.post_id,
                                page_title="EDIT-COMMENT")
                else:
                    page_error = "ERROR 500 : You don't own this comment."
                    self.render("error.html",
                                page_error=page_error,
                                username=self.user.username,
                                page_title="ERROR")
            else:
                page_error = "ERROR 404 : Comment post not found."
                self.render("error.html",
                            page_error=page_error,
                            username=self.user.username,
                            page_title="ERROR")

        else:
            self.redirect("/sign-in")

    def post(self, comment_id):
        """Checks the posted comment's form information for errors and
           accordingly changes the values of appropriate entities
           and redirects the page."""

        input_name = self.request.get("name")
        input_email = self.request.get("email")
        content = self.request.get("content")
        post_id = self.request.get("post_id")

        comment_err = False
        err_email = ''

        if not valid_email(input_email):
            err_email = "Please enter valid e-mail !"
            comment_err = True

        template_values = {
            'page_title': 'PERMALINK',
            'post_id': post_id,
            'username': self.user.username,
            'err_email': err_email,
            'input_name': input_name,
            'input_email': input_email,
            'content': content
        }

        if not comment_err:
            comment = COMMENT.by_id(int(comment_id))
            if comment.user_id == str(self.user.id):
                comment.name = input_name
                comment.email = input_email
                comment.content = content
                comment.put()
                self.redirect("/post/" + post_id)
            else:
                page_error = "ERROR 500 : You don't own this comment."
                self.render("error.html",
                            page_error=page_error,
                            username=self.user.username,
                            page_title="ERROR")
        else:
            self.render_template("edit-comment.html", template_values)
