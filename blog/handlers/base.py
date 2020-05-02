# base.py
"""Contains class defination for handler class BaseHandler."""

import webapp2

from app.database.setup import DBSession, USER
from app.helpers.helper import (
    render_str,
    make_secure_val,
    check_secure_val,
    get_page_title,
    get_page_color
)

# Create instance of DBSession
session = DBSession()


class BaseHandler(webapp2.RequestHandler):
    """Main handler for BLOG website which is parent of all other
       handler classes."""

    def write(self, *a, **kw):
        """Writes the passed parameters in webpage."""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Renders template using passed parameters in webpage and
           adds extra parameters according to template."""

        title = get_page_title(template)

        page_color = 'black'

        if self.user:
            page_color = get_page_color(title)
            params['user'] = self.user

        if 'page_status' in params:
            self.response.set_status = params['page_status']

        if 'page_title' not in params:
            params['page_title'] = title

        if 'page_color' not in params:
            params['page_color'] = page_color

        params['page_template'] = template

        return render_str(template, **params)

    def render(self, template, **params):
        """Writes template using passed parameters in webpage."""
        self.write(self.render_str(template, **params))

    def set_secure_cookie(self, key, val):
        """Sets cookie for current user in browser."""

        cookie_val = make_secure_val(val)

        self.response.headers.add_header('Set-Cookie',
                                         '%s=%s; Path=/'
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
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """Initializes class's USER entitity from cookie info
           stored in browser."""

        webapp2.RequestHandler.initialize(self, *a, **kw)

        # Create instance of DBSession
        self.session = DBSession()

        user_id = self.read_secure_cookie('user_id')

        if user_id:
            self.user = self.session.query(
                USER).filter_by(id=int(user_id)).first()
        else:
            self.user = None
