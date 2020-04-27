# delete_post.py
"""Contains class defination for handler class DeletePostHandler."""

from base import BaseHandler
from app.database.setup import session, POST


class DeletePostHandler(BaseHandler):
    """Handler for DELETING a blog post of user."""

    def get(self, post_id):
        """Validates the posted blog post's form information for
           errors and accordingly deletes the values of appropriate
           entities and redirects the page."""

        if self.user:
            post = POST.query.filter(id=post_id).first()
            if post:
                if self.user.id == post.user_id:
                    self.user.liked_posts.remove(post)

                    session.add(self.user)
                    session.delete(post)
                    session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
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
