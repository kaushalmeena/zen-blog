# delete_comment.py
"""Contains class defination for handler class DeleteCommentHandler."""

from base import BaseHandler
from app.database.setup import COMMENT


class DeleteCommentHandler(BaseHandler):
    """Handler for DELETING a comment post of user."""

    def get(self, comment_id):
        """Validates the posted comment's form information for
           errors and accordingly deletes the values of appropriate
           entities and redirects the page."""

        comment_id = int(comment_id)

        if self.user:
            comment = self.session.query(
                COMMENT).filter_by(id=comment_id).first()
            if comment:
                if comment.user_id == self.user.id:
                    self.session.delete(comment)
                    self.session.commit()

                    referrer = self.request.headers.get('referer')
                    if referrer:
                        self.redirect(referrer)
                    else:
                        self.redirect('/')
                else:
                    page_error = "You don't own this comment."
                    self.render("error.html",
                                page_error=page_error,
                                page_status=500)
            else:
                page_error = "Comment post not found."
                self.render("error.html",
                            page_error=page_error,
                            page_status=404)

        else:
            self.redirect("/sign-in")
