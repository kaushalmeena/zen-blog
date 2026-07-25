"""Flask extension instances, created unbound so the app factory can attach them."""

from flask_compress import Compress
from flask_htmx import HTMX
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase


class Model(DeclarativeBase):
    """Base class for every ORM model."""


compress = Compress()
csrf = CSRFProtect()
db = SQLAlchemy(model_class=Model)
htmx = HTMX()
login_manager = LoginManager()
migrate = Migrate()
