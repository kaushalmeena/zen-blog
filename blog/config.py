"""Application configuration objects, selected through the ``APP_CONFIG`` env var."""

import os
from datetime import timedelta
from typing import Any, ClassVar


class BaseConfig:
    """Settings shared by every environment."""

    POSTS_PER_PAGE = 10

    #: Seconds to cache static files for. Their URLs carry a content stamp, so a
    #: long lifetime is safe; 0 keeps Werkzeug's revalidate-every-time default,
    #: which is what you want while editing CSS.
    STATIC_MAX_AGE = 0

    SITE_NAME = "MYAPP-BLOG"
    SITE_TAGLINE = "A minimal, JavaScript-free blogging platform."

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict[str, Any]] = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=14)

    @staticmethod
    def init_app(app):
        """Apply settings that need a live app instance (e.g. the instance path)."""
        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            os.makedirs(app.instance_path, exist_ok=True)
            db_path = os.path.join(app.instance_path, "blog.db")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"


class DevelopmentConfig(BaseConfig):
    """Local development: debug on, throwaway secret, SQLite in ``instance/``."""

    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class TestingConfig(BaseConfig):
    """Test runs: in-memory database and no CSRF plumbing to fight with."""

    TESTING = True
    SECRET_KEY = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    POSTS_PER_PAGE = 3

    @staticmethod
    def init_app(app):
        """Skip instance-folder setup; testing always uses an in-memory database."""


class ProductionConfig(BaseConfig):
    """Production: secrets and database URL come from the environment."""

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    STATIC_MAX_AGE = 31_536_000  # one year

    @staticmethod
    def init_app(app):
        """Require a real secret key, then fall back to the shared setup."""
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY must be set when APP_CONFIG is ProductionConfig.")
        app.config["SECRET_KEY"] = secret_key
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "")
        BaseConfig.init_app(app)


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
