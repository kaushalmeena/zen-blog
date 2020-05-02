# delete_post.py
"""Contains class defination for handler class DeletePostHandler."""

from base import BaseHandler
from app.database.setup import POST


class DeletePostHandler(BaseHandler):
    """Handler for DELETING a blog post of user."""

    def get(self, post_id):
        """Validates the posted blog post's form information for
           errors and accordingly deletes the values of appropriate
           entities and redirects the page."""

        post_id = int(post_id)

        if self.user:
            post = self.session.query(POST).filter_by(id=post_id).first()
            if post:
                if post.user_id == self.user.id:
                    self.user.liked_posts.remove(post)

                    self.session.add(self.user)
                    self.session.delete(post)
                    self.session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
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
