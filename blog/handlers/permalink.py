# permalink.py
"""Contains class defination for handler class PermalinkHandler."""

from base import BaseHandler
from app.database.setup import POST, COMMENT
from app.helpers.helper import valid_email


class PermalinkHandler(BaseHandler):
    """Handler for PERMALINK page a which displays individual
       blog post's information and also allows users to post their
       comments on that blog."""

    def get(self, post_id):
        """Renders PERMALINK page in after fetching appropriate data."""

        post_id = int(post_id)

        post = self.session.query(POST).filter_by(id=post_id).first()

        if not post:
            page_error = "Blog post not found."
            self.render("error.html",
                        page_error=page_error,
                        page_status=404)
        else:
            if self.user:
                show_form = True
                if post.user_id == self.user.id:
                    show_form = False

                self.render("permalink.html",
                            post=post,
                            show_form=show_form,
                            name=self.user.name,
                            email=self.user.email)
            else:
                self.render("permalink.html", post=post)

    def post(self, post_id):
        """Checks the posted comment's form information for errors
           and accordingly creates appropriate entity and redirects
           the page. Also incresess the appropriate blog post's
           comment count."""

        post_id = int(post_id)

        name = self.request.get("name")
        email = self.request.get("email")
        content = self.request.get("content")
        post_id = self.request.get("post_id")

        template_values = {
            'name': name,
            'email': email,
            'content': content
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
            comment_err = True
            template_values['err_email'] = "Please enter valid e-mail!"

        if not content:
            comment_err = True
            template_values['err_content'] = "Content is required field!"

        post = self.session.query(POST).filter_by(id=post_id).first()

        if post:
            template_values['post'] = post
            if not comment_err:
                user_id = None
                if self.user:
                    user_id = self.user.id

                comment = COMMENT(user_id=user_id,
                                  post=post,
                                  name=name,
                                  email=email,
                                  content=content)

                self.session.add(comment)
                self.session.commit()

                self.redirect("/post/" + str(post_id))
            else:
                self.render_template("permalink.html", template_values)
        else:
            page_error = "Blog post not found."
            self.render("error.html",
                        page_error=page_error,
                        page_status=404)
