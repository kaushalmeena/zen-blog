# sign_in.py
"""Contains class defination for handler class SignInHandler."""

from base import BaseHandler
from app.database.setup import USER
from app.helpers.helper import validate_password


class SignInHandler(BaseHandler):
    """Handler for SIGN-IN page which allows users to login."""

    def get(self):
        """Renders SIGN-IN page if user has not logged in otherwise
           renders WELCOME page."""

        if self.user:
            self.redirect("/welcome")
        else:
            self.render("sign-in.html")

    def post(self):
        """Validates user sign-in's form information for errors and
           accordingly redirects the page."""

        username = self.request.get("username")
        password = self.request.get("password")

        template_values = {
            'username': username,
            'password': password
        }

        signin_err = False

        if len(username) < 6 or len(username) > 30:
            signin_err = True
            template_values['err_username'] = \
                "Username must be of 6 to 30 characters!"

        if len(password) < 6 or len(password) > 30:
            signin_err = True
            template_values['err_password'] = \
                "Password must be of 6 to 30 characters!"

        if not signin_err:
            user = self.session.query(USER).filter_by(
                username=username).one_or_none()
            if user and validate_password(
                    username, password, user.password_hash):
                self.login(user)
                self.redirect("/welcome")
            else:
                template_values['err_login'] = "Invalid username or password."
                self.render_template("sign-in.html", template_values)

        else:
            self.render_template("sign-in.html", template_values)
