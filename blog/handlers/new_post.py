# new_post.py
"""Contains class defination for handler class NewPostHandler."""

from base import BaseHandler
from app.database.setup import POST


class NewPostHandler(BaseHandler):
    """Handler for NEW-POST page which allows users to create
       new blog posts."""

    def get(self):
        """Renders NEW-POST page if user has logged in otherwise
           renders SIGN-IN page."""

        if self.user:
            self.render("new-post.html")
        else:
            self.redirect("/sign-in")

    def post(self):
        """Validates the posted blog post's form information for
           errors and accordingly creates the appropriate entities
           and redirects the page."""

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
            post = POST(user_id=self.user.id,
                        subject=subject,
                        content=content)

            self.session.add(post)
            self.session.commit()

            self.redirect("/post/" + str(post.id))
        else:
            self.render("new-post.html", template_values)
