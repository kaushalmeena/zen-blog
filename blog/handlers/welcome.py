# welcome.py
"""Contains class defination for handler class WelcomeHandler."""

from base import BaseHandler


class WelcomeHandler(BaseHandler):
    """Handler for WELCOME page which is showed to users after login."""

    def get(self):
        """Renders WELCOME page if user has logged in otherwise
           renders SIGN-IN page."""

        if self.user:
            self.render("welcome.html")
        else:
            self.redirect("/sign-in")
