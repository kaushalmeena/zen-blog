# dislike.py
"""Contains class defination for handler class DislikeHandler."""

from base import BaseHandler
from app.database.setup import POST


class DislikeHandler(BaseHandler):
    """Handler for DISLIKING a blog post."""

    def get(self, post_id):
        """Deletes the passed post_id from user's list of liked_posts
           and redirects the page accordingly."""

        post_id = int(post_id)

        if self.user:
            post = self.session.query(POST).filter_by(id=post_id).first()
            if post:
                if not post.user_id == self.user.id:
                    if post in self.user.liked_posts:
                        self.user.liked_posts.remove(post)

                        self.session.add(self.user)
                        self.session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
                else:
                    page_error = "You can't dislike your own post."
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
