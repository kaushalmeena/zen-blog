# setting.py
"""Contains class defination for handler class SettingHandler."""

from base import BaseHandler
from app.helpers.helper import valid_email


class SettingHandler(BaseHandler):
    """Handler for SETTING page a which allows users to change
       their profile settings and passwords and also allows users
       to delete all their post, comments or even acount."""

    def get(self):
        """Renders SETTING page in if user has logged in otherwise
           redirects to SIGN-IN page after fetching appropriate data."""

        if self.user:
            self.render("setting.html",
                        name=self.user.name,
                        email=self.user.email)
        else:
            self.redirect("/sign-in")

    def post(self):
        """Checks the posted setting's form information for errors
           and accordingly changes the values of appropriate entities
           and redirects the page. Also perform the task of deleting
           all their posts, comments or even account if specified."""

        name = self.request.get("name")
        email = self.request.get("email")
        delete1 = self.request.get("delete1")
        delete2 = self.request.get("delete2")
        delete3 = self.request.get("delete3")

        template_values = {
            'name': name,
            'email': email
        }

        setting_err = False

        if not name == self.user.name:
            if len(name) < 6 or len(name) > 256:
                setting_err = True
                template_values['err_name'] = \
                    "Name must be of 6 to 256 characters!"
            else:
                self.user.name = name

                self.session.add(self.user)
                self.session.commit()

        if not email == self.user.email:
            if len(email) < 6 or len(email) > 256:
                setting_err = True
                template_values['err_email'] = \
                    "Email must be of 6 to 256 characters!"
            elif not valid_email(email):
                setting_err = True
                template_values['err_email'] = \
                    "Please enter valid e-mail !"
            else:
                self.user.email = email

                self.session.add(self.user)
                self.session.commit()

        if not setting_err:
            if delete1:
                for post in self.user.posts:
                    post.comments = []

                    self.session.add(post)

                self.session.commit()

            if delete2:
                self.user.posts = []

                self.session.add(self.user)
                self.session.commit()

            if delete3:
                self.session.delete(self.user)
                self.session.commit()

                self.logout()
                self.redirect("/")
            else:
                self.redirect("/setting")
        else:
            self.render_template("setting.html", template_values)
