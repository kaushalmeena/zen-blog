# sign_up.py
"""Contains class defination for handler class SignUpHandler."""

from base import BaseHandler
from app.database.setup import USER
from app.helpers.helper import valid_email, valid_username, make_password_hash


class SignUpHandler(BaseHandler):
    """Handler for SIGN-UP page which allows users to register."""

    def get(self):
        """Renders SIGN-UP page if user has not registered otherwise
           renders WELCOME page."""

        if self.user:
            self.redirect("/welcome")
        else:
            self.render("sign-up.html", page_title="SIGN-UP")

    def post(self):
        """Validates user sign-up's form information for errors and
           accordingly redirects the page."""

        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        name = self.request.get("name")
        email = self.request.get("email")

        template_values = {
            'username': username,
            'password': password,
            'verify': verify,
            'email': email,
            'name': name,
        }

        signup_err = False

        if len(username) < 6 or len(username) > 30:
            signup_err = True
            template_values['err_username'] = \
                "Username must be of 6 to 30 characters!"
        elif not valid_username(username):
            signup_err = True
            template_values['err_username'] = \
                "Username must containe only alphanumeric characters!"

        if len(password) < 6 or len(password) > 30:
            signup_err = True
            template_values['err_password'] = \
                "Password must be of 6 to 30 characters!"
        elif not password == verify:
            signup_err = True
            template_values['err_password'] = "Passwords don't match!"

        if email:
            if len(email) < 6 or len(email) > 250:
                signup_err = True
                template_values['err_email'] = \
                    "Email must be of 6 to 250 characters!"
            elif not valid_email(email):
                signup_err = True
                template_values['err_email'] = "Please enter valid e-mail!"
            else:
                user = self.session.query(USER).filter_by(email=email).first()
                if user:
                    signup_err = True
                    template_values['err_email'] = \
                        "Specififed email already exists!"

        if name:
            if len(name) < 5 or len(name) > 251:
                signup_err = True
                template_values['err_name'] = \
                    "Name must be of 6 to 250 characters!"

        if not signup_err:
            user = self.session.query(USER).filter_by(
                username=username).first()
            if user:
                template_values['err_name'] = \
                    "Specified username alredy exits!"
                self.render("sign-up.html", template_values)
            else:
                password_hash = make_password_hash(username, password)
                user = USER(username=username,
                            password_hash=password_hash,
                            name=name,
                            email=email)

                self.session.add(user)
                self.session.commit()

                self.login(user)
                self.redirect("/welcome")
        else:
            self.render_template("sign-up.html", template_values)
