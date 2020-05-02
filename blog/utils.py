# helper.py
"""Python function definations for helper function."""

# python modules
import jinja2
import re
import hashlib
import hmac
import random
import string

from os.path import join, dirname, splitext

from app.secrets.secret import get_secret

# secret string
SECRET = get_secret()

# regular expression patterns
USERNAME_RE = re.compile(r"^[a-zA-Z0-9]$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

# jinja environment defination
TEMPLATE_DIR = join(dirname(__file__), "../templates")
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR), autoescape=True
)

# title-to-page-color mapping
PAGE_COLOR = {
    "HOME": "red",
    "NEW-POST": "blue",
    "MY-POST": "green",
    "SETTING": "orange",
    "WELCOME": "purple",
    "EDIT-POST": "purple",
    "EDIT-COMMENT": "purple",
    "PERMALINK": "purple",
}


def render_str(template, **params):
    """Renders the template using passed parameters."""

    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(params)


def make_salt(length=5):
    """Creates random string of length same as passed parameter."""

    return "".join(random.choice(string.letters) for x in range(length))


def make_password_hash(username, password, salt=None):
    """Creates hash using passed parameters."""

    if not salt:
        salt = make_salt()
    hash_val = hashlib.sha256(username + password + salt).hexdigest()

    return "%s,%s" % (salt, hash_val)


def validate_password(username, password, hash_val):
    """Validates username and password using hash value."""

    salt = hash_val.split(",")[0]
    return hash_val == make_password_hash(username, password, salt)


def hash_str(string):
    """Returns a hash value of passed string."""

    return hmac.new(SECRET, string).hexdigest()


def make_secure_val(string):
    """Creates a password hash using passed string."""

    return "%s|%s" % (string, hash_str(string))


def check_secure_val(hash_val):
    """Checks if passed hash value is correct or not."""

    val = hash_val.split("|")[0]
    if hash_val == make_secure_val(val):
        return val


def valid_username(username):
    """Validates username using regular expressions."""

    return USERNAME_RE.match(username)


def valid_email(email):
    """Validates email using regular expressions."""

    return EMAIL_RE.match(email)


def get_page_color(title):
    """Returns page color for a template."""

    return PAGE_COLOR.get(title, "black")


def get_page_title(template):
    """Returns page title for a template."""

    return splitext(template)[0].upper()
