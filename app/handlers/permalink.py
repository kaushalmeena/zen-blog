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

        post = POST.by_id(int(post_id))
        comments = COMMENT.by_post_id(post_id)

        if not post:
            page_error = "ERROR 404 : Blog post not found."
            self.render("error.html",
                        username=self.user.username,
                        page_error=page_error,
                        page_title="ERROR")
        else:
            if self.user:
                show_form = True
                if post.user_id == str(self.user.id):
                    show_form = False

                liked_posts = []
                if str(post.id) in self.user.liked_posts:
                    liked_posts.append(str(post.id))

                self.render("permalink.html",
                            post=post,
                            comments=comments,
                            liked_posts=liked_posts,
                            username=self.user.username,
                            user_id=str(self.user.id),
                            show_form=show_form,
                            input_name=self.user.name,
                            input_email=self.user.email,
                            page_title="PERMALINK")
            else:
                self.render("permalink.html",
                            post=post,
                            comments=comments,
                            page_title="PERMALINK")

    def post(self, post_id):
        """Checks the posted comment's form information for errors
           and accordingly creates appropriate entity and redirects
           the page. Also incresess the appropriate blog post's
           comment count."""

        input_name = self.request.get("input_name")
        input_email = self.request.get("input_email")
        content = self.request.get("content")
        post_id = self.request.get("post_id")

        comment_err = False
        err_email = ''
        post = POST.by_id(int(post_id))

        if not valid_email(input_email):
            err_email = "Please enter valid e-mail !"
            comment_err = True

        template_values = {
            'page_title': 'PERMALINK',
            'username': self.user.username,
            'err_email': err_email,
            'input_name': input_name,
            'input_email': input_email,
            'content': content,
            'post': post
        }

        if comment_err == False:
            comment = COMMENT.create_comment(str(self.user.id),
                                             post_id,
                                             name=input_name,
                                             email=input_email,
                                             content=content)
            comment.put()
            self.redirect("/post/" + post_id)
        else:
            self.render_template("permalink.html", template_values)
