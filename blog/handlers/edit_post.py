# edit_post.py
"""Contains class defination for handler class EditPostHandler."""

from base import BaseHandler
from app.database.setup import POST


class EditPostHandler(BaseHandler):
    """Handler for EDITING a blog post of user."""

    def get(self, post_id):
        """Renders EDIT-POST page if user has logged in after querying
           appropriate data otherwise redirects to SIGN-IN page."""

        post_id = int(post_id)

        if self.user:
            post = self.session.query(POST).filter_by(id=post_id).first()
            if post:
                if post.user_id == self.user.id:
                    self.render("edit-post.html",
                                subject=post.subject,
                                content=post.content)
                else:
                    page_error = "You don't own this post."
                    self.render("error.html",
                                page_error=page_error,
                                page_status=500)
            else:
                page_error = "Blog post not found."
                self.render("error.html",
                            page_error=page_error,
                            page_status=404)

        else:
            self.redirect("/sign-in")

    def post(self, post_id):
        """Checks the posted blog post's form information for
           errors and accordingly changes the values of appropriate
           entities and redirects the page."""

        post_id = int(post_id)

        subject = self.request.get("subject")
        content = self.request.get("content")

        template_values = {
            'subject': subject,
            'content': content
        }

        post_err = False

        if len(subject) < 6 or len(subject) > 256:
            post_err = True
            template_values['err_subject'] = \
                "Subject must be of 6 to 256 characters!"

        if not content:
            post_err = True
            template_values['err_content'] = "Content is required field!"

        if not post_err:
            post = self.session.query(POST).filter_by(id=post_id).first()
            if post:
                if post.user_id == self.user.id:
                    post.subject = subject
                    post.content = content

                    self.session.add(post)
                    self.session.commit()

                    self.redirect("/my-post")
                else:
                    page_error = "You don't own this post."
                    self.render("error.html",
                                page_error=page_error,
                                page_status=500)
            else:
                page_error = "Blog post not found."
                self.render("error.html",
                            page_error=page_error,
                            page_status=404)

        else:
            self.render("edit-post.html", template_values)
