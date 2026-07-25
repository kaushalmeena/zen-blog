"""Application factory for the blog."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask

from blog.config import CONFIGS, BaseConfig
from blog.extensions import compress, csrf, db, htmx, login_manager, migrate

__all__ = ["create_app"]


def create_app(config: str | type[BaseConfig] | None = None) -> Flask:
    """Build and configure a :class:`~flask.Flask` application.

    Args:
        config: A key from :data:`blog.config.CONFIGS` (``"development"``,
            ``"testing"``, ``"production"``), a config class, or ``None`` to read
            the ``APP_CONFIG`` environment variable.
    """
    load_dotenv()

    config_class = _resolve_config(config)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    config_class.init_app(app)

    _register_extensions(app)
    _register_blueprints(app)

    from blog import cli, errors, template_filters

    cli.register(app)
    errors.register(app)
    template_filters.register(app)
    _register_cache_policy(app)

    return app


def _register_cache_policy(app: Flask) -> None:
    """Keep signed-in pages out of the browser cache.

    Pages rendered for a signed-in user contain controls only that user may use
    (edit, delete, unfollow). Without this header the browser is free to redisplay
    such a page from cache after a different account signs in — the buttons still
    fail with 403, but the page looks like it grants access it does not.
    """
    from flask_login import current_user

    @app.after_request
    def add_cache_headers(response):
        if current_user.is_authenticated:
            response.headers.setdefault("Cache-Control", "no-store, private")
            response.headers.setdefault("Vary", "Cookie")
        return response


def _resolve_config(config: str | type[BaseConfig] | None) -> type[BaseConfig]:
    if config is None:
        config = os.environ.get("APP_CONFIG", "development")
    if not isinstance(config, str):
        return config
    try:
        return CONFIGS[config.lower()]
    except KeyError:
        raise RuntimeError(
            f"Unknown APP_CONFIG {config!r}; expected one of {sorted(CONFIGS)}."
        ) from None


def _register_extensions(app: Flask) -> None:
    compress.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    htmx.init_app(app)
    login_manager.init_app(app)

    from blog import models  # noqa: F401  imported so Alembic can see the tables

    migrate.init_app(app, db)

    login_manager.login_view = "auth.sign_in"
    login_manager.login_message = "You must be signed in to do that."


def _register_blueprints(app: Flask) -> None:
    from blog.blueprints import auth, feeds, main, posts, users

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(feeds.bp)
