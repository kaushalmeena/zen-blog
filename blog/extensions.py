"""Contains extensions for blog app."""

from flask_compress import Compress

from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy

compress = Compress()
login_manager = LoginManager()
db = SQLAlchemy()
