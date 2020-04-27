# base.py
"""Contains class defination for handler class BaseHandler."""

import webapp2

from app.database.setup import session, USER
from app.helpers.helper import render_str, render_template_str
from app.helpers.helper import make_secure_val, check_secure_val
from app.helpers.helper import get_page_title, get_page_color


class BaseHandler(webapp2.RequestHandler):
    """Main handler for BLOG website which is parent of all other
       handler classes."""

    def write(self, *a, **kw):
        """Writes the passed parameters in webpage."""

        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Renders template using passed parameters in webpage."""

        params['page_title'] = get_page_title(template)

        page_color = 'black'
        if self.user:
            page_color = get_page_color(template)
            params['user'] = self.user

        if 'page_color' not in params:
            params['page_color'] = page_color

        return render_str(template, **params)

    def render_template_str(self, template, template_values):
        """Renders template using passed dictionary in webpage."""

        return render_template_str(template, template_values)

    def render(self, template, **kw):
        """Writes template using passed parameters in webpage."""

        self.write(self.render_str(template, **kw))

    def render_template(self, template, template_values):
        """Writes template using passed dictionary in webpage."""

        self.write(self.render_template_str(template, template_values))

    def set_secure_cookie(self, key, val):
        """Sets cookie for current user in browser."""

        cookie_val = make_secure_val(val)

        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/'
                                         % (key, cookie_val))

    def read_secure_cookie(self, key):
        """Reads cookie from browser for passed parameters."""

        cookie_val = self.request.cookies.get(key)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """Sets cookie in browser for passed parameter."""

        self.user = user
        self.set_secure_cookie('user_id', str(user.id))

    def logout(self):
        """Deletes cookie from browser for current user."""

        self.response.headers.add_header('Set-Cookie',
                                         'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """Initializes class's USER entitity from cookie info
           stored in browser."""

        webapp2.RequestHandler.initialize(self, *a, **kw)
        user_id = self.read_secure_cookie('user_id')

        if user_id:
            self.user = session.query(USER).filter_by(id=int(user_id)).first()
