# sign_out.py
"""Contains class defination for handler class SignOutHandler."""

from base import BaseHandler


class SignOutHandler(BaseHandler):
    """Handler for SIGN-OUT page which allows users to logout."""

    def get(self):
        """Logout the user and redirects to HOME page."""
        self.logout()
        self.redirect('/')
