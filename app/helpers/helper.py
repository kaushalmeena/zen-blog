# helper.py
"""Python function definations for helper function."""

# python modules
import os
import jinja2
import re
import hashlib
import hmac
import random
import string

from app.secrets.secret import get_secret

# secret string
SECRET = get_secret()

# regular expression patterns
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

# jinja environment defination
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=True
)

# page color mapping
PAGE_COLOR = {
    'HOME': 'red',
    'NEW-POST': 'blue',
    'MY-POST': 'green',
    'SETTING': 'orange',
    'WELCOME': 'purple',
    'EDIT-POST': 'purple',
    'EDIT-COMMENT': 'purple',
    'PERMALINK': 'purple'
}


def count_likes(post_id, liked_posts):
    """Counts the no. likes using passed parameters."""

    post_id = str(post_id)

    if liked_posts:
        like_count = 0
        for liked_post_id in liked_posts:
            if post_id == liked_post_id:
                like_count += 1

        return like_count

    else:
        return 0


def user_liked_post(post_id, liked_posts):
    """Returns True post_id is present in liked_posts otherwise
       returns False."""

    post_id = str(post_id)

    user_liked_post = False
    if liked_posts:
        for liked_post_id in liked_posts:
            if post_id == liked_post_id:
                user_liked_post = True
                break

        return user_liked_post

    else:
        return user_liked_post


def count_comments(post_id, comments):
    """Counts the no. likes using passed parameters."""

    post_id = str(post_id)

    if comments:
        comment_count = 0
        for comment in comments:
            if post_id == comment.post_id:
                comment_count += 1

        return comment_count

    else:
        return 0


JINJA_ENVIRONMENT.globals['count_likes'] = count_likes
JINJA_ENVIRONMENT.globals['user_liked_post'] = user_liked_post
JINJA_ENVIRONMENT.globals['count_comments'] = count_comments


def render_str(template, **params):
    """Renders the template using passed parameters."""

    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(params)


def render_template_str(template, template_values):
    """Renders the template using dictionary."""

    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(template_values)


def make_salt(length=5):
    """Creates random string of length same as passed parameter."""

    return ''.join(random.choice(string.letters) for x in xrange(length))


def make_password_hash(username, password, salt=None):
    """Creates hash using passed parameters."""

    if not salt:
        salt = make_salt()
    hash_val = hashlib.sha256(username + password + salt).hexdigest()

    return '%s,%s' % (salt, hash_val)


def validate_password(username, password, hash_val):
    """Validates username and password using hash value."""

    salt = hash_val.split(',')[0]
    return hash_val == make_password_hash(username, password, salt)


def hash_str(string):
    """Returns a hash value of passed string."""

    return hmac.new(SECRET, string).hexdigest()


def make_secure_val(string):
    """Creates a password hash using passed string."""

    return "%s|%s" % (string, hash_str(string))


def check_secure_val(hash_val):
    """Checks if passed hash value is correct or not."""

    val = hash_val.split('|')[0]
    if hash_val == make_secure_val(val):
        return val


def valid_username(username):
    """Validates username using regular expressions."""

    return USERNAME_RE.match(username)


def valid_password(password):
    """Validates password using regular expressions."""

    return PASSWORD_RE.match(password)


def valid_email(email):
    """Validates email using regular expressions."""

    return EMAIL_RE.match(email)


def get_page_color(template):
    """Returns page color for a template."""

    return PAGE_COLOR.get(template, "black")


def get_page_tile(template):
    """Returns page title for a template."""

    return os.path.splitext(template)[0].upper()
