# sign_in.py
"""Contains class defination for handler class SignInHandler."""

from base import BaseHandler
from app.database.setup import USER
from app.helpers.helper import valid_username, valid_password


class SignInHandler(BaseHandler):
    """Handler for SIGN-IN page which allows users to login."""

    def get(self):
        """Renders SIGN-IN page if user has not logged in otherwise
           renders WELCOME page."""

        if self.user:
            self.redirect("/welcome")
        else:
            self.render("sign-in.html", page_title="SIGN-IN")

    def post(self):
        """Validates user sign-in's form information for errors and
           accordingly redirects the page."""

        username = self.request.get("username")
        password = self.request.get("password")

        err_username = ''
        err_password = ''

        signin_err = False

        if not valid_username(username):
            err_username = "Please enter valid username !"
            signin_err = True

        if not valid_password(password):
            err_password = "Password must contain atleast 3 characters !"
            signin_err = True

        template_values = {
            'page_title': 'SIGN-IN',
            'err_username': err_username,
            'err_password': err_password,
            'input_username': username,
            'input_password': password
        }

        if not signin_err:
            user = USER.login(username, password)

            if user:
                self.login(user)
                self.redirect("/welcome")
            else:
                self.render("sign-in.html",
                            err_login="Invalid username or password.",
                            input_username=username,
                            input_password=password,
                            page_title="SIGN-IN")
        else:
            self.render_template("sign-in.html", template_values)
