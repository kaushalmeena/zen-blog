# like.py
"""Contains class defination for handler class LikeHandler."""

from base import BaseHandler
from app.database.setup import POST


class LikeHandler(BaseHandler):
    """Handler for LIKING a blog post."""

    def get(self, post_id):
        """Adds the passed post_id in user's list of liked_posts
           and redirects the page accordingly."""

        post_id = int(post_id)

        if self.user:
            post = self.session.query(POST).filter_by(id=post_id).first()
            if post:
                if not post.user_id == self.user.id:
                    if post not in self.user.liked_posts:
                        self.user.liked_posts.append(post_id)

                        self.session.add(self.user)
                        self.session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
                else:
                    page_error = "You can't like your own post."
                    self.render("error.html",
                                page_error=page_error,
                                page_status=500)

            else:
                page_error = "Blog post not found."
                self.render("error.html",
                            page_error=page_error,
                            page_title=4040)

        else:
            self.redirect("/sign-in")
