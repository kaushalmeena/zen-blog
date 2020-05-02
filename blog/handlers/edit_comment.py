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

        comment_id = int(comment_id)

        if self.user:
            comment = self.session.query(
                COMMENT).filter_by(id=comment_id).first()
            if comment:
                if comment.user_id == self.user.id:
                    self.render("edit-comment.html",
                                name=comment.name,
                                email=comment.email,
                                content=comment.content,
                                post_id=comment.post_id)
                else:
                    page_error = "ERROR 500 : You don't own this comment."
                    self.render("error.html",
                                page_error=page_error)
            else:
                page_error = "ERROR 404 : Comment post not found."
                self.render("error.html",
                            page_error=page_error)

        else:
            self.redirect("/sign-in")

    def post(self, comment_id):
        """Checks the posted comment's form information for errors and
           accordingly changes the values of appropriate entities
           and redirects the page."""

        comment_id = int(comment_id)

        name = self.request.get("name")
        email = self.request.get("email")
        content = self.request.get("content")
        post_id = self.request.get("post_id")

        template_values = {
            'name': name,
            'email': email,
            'content': content,
            'post_id': post_id
        }

        comment_err = False

        if len(name) < 6 or len(name) > 256:
            comment_err = True
            template_values['err_name'] = \
                "Name must be of 6 to 256 characters!"

        if len(email) < 6 or len(email) > 256:
            comment_err = True
            template_values['err_email'] = \
                "Email must be of 6 to 256 characters!"
        elif not valid_email(email):
            template_values['err_email'] = "Please enter valid e-mail!"
            comment_err = True

        if not content:
            comment_err = True
            template_values['err_content'] = "Content is required field!"

        if not comment_err:
            comment = self.session.query(
                COMMENT).filter_by(id=comment_id).first()
            if comment.user_id == self.user.id:
                comment.name = name
                comment.email = email
                comment.content = content

                self.session.add(comment)
                self.session.commit()

                self.redirect("/post/" + post_id)
            else:
                page_error = "You don't own this comment."
                self.render("error.html",
                            page_error=page_error,
                            page_status=500)
        else:
            self.render_template("edit-comment.html", template_values)
