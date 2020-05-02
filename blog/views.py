"""
Python script for TextSuite server.
"""

from flask import Flask, render_template, request
from flask_compress import Compress

from app.config import DevelopmentConfig

app = Flask(__name__)

# Compress flask app's responses with gzip
Compress(app)


@app.route("/")
def home00():
    """
    Handler for HOME page which displays the blog posts along
    with their comments.
    """

    posts = self.session.query(POST).order_by(POST.created.desc()).limit(20).all()

    return render_template("home.html", title="main-home")


def error400(exception=None):
    """Error 404 page."""
    return render_template("400.html", title="error 400"), 400


def error404(exception=None):
    """Error 404 page."""
    return render_template("404.html", title="error 404"), 404


def error500(exception=None):
    """Error 500 page."""
    return render_template("500.html", title="error 500"), 500
