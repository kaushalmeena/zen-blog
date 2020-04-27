# my_post.py
"""Contains class defination for handler class MyPostHandler."""

from base import BaseHandler
from app.database.setup import session, POST, COMMENT


class MyPostHandler(BaseHandler):
    """Handler for MY-POST page which show users their own blog posts."""

    def get(self):
        """Renders MY-POST page if user has logged in after querying
           appropriate data otherwise renders SIGN-IN page."""

        if self.user:
            posts = POST.by_user_id(str(self.user.id))
            comments = []

            for post in posts:
                query_comments = session.query(COMMENT).filter(
                    post_id=post.id).limit(10)

                if query_comments:
                    for comment in query_comments:
                        comments.append(comment)

            liked_posts = []
            for post in posts:
                if str(post.id) in self.user.liked_posts:
                    liked_posts.append(str(post.id))

            self.render("my-post.html",
                        posts=posts,
                        comments=comments,
                        liked_posts=liked_posts,
                        user_id=str(self.user.id),
                        username=self.user.username,
                        page_title="MY-POST")
        else:
            self.redirect("/sign-in")
