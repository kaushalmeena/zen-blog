"""Contains extensions for textsuite app."""

from flask_compress import Compress

from flask_sqlalchemy import SQLAlchemy

compress = Compress()
db = SQLAlchemy()
