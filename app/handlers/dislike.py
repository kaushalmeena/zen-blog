# dislike.py
"""Contains class defination for handler class DislikeHandler."""

from base import BaseHandler
from app.database.setup import session, POST


class DislikeHandler(BaseHandler):
    """Handler for DISLIKING a blog post."""

    def get(self, post_id):
        """Deletes the passed post_id from user's list of liked_posts
           and redirects the page accordingly."""

        if self.user:
            post = session.query(POST).filter(id=post_id).first()
            if post:
                if not post.user_id == str(self.user.id):
                    if post in self.user.liked_posts:
                        self.user.liked_posts.remove(post)
                        session.add(self.user)
                        session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
                else:
                    page_error = "ERROR 500 : You can't dislike your own post."
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
