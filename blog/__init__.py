"""Application factory for the blog."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask, request
from flask.sessions import SecureCookieSessionInterface

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

    from blog import assets, cli, errors, template_filters

    assets.register(app)
    cli.register(app)
    errors.register(app)
    template_filters.register(app)
    _register_cache_policy(app)

    return app


def _register_cache_policy(app: Flask) -> None:
    """Split caching into two rules: public assets, and private pages.

    Static files are identical for everyone and their URLs carry a content stamp
    (see blog/assets.py), so they can be cached hard and never revalidated. They
    must also shed the ``Vary: Cookie`` that Flask's session adds to every
    response — an asset that varies by cookie cannot be reused across visitors in
    a shared cache, which would undo the caching entirely.

    Pages rendered for a signed-in user are the opposite case: they contain
    controls only that user may use (edit, delete, unfollow). Without ``no-store``
    the browser may redisplay such a page from cache after a different account
    logs in. The buttons still fail with 403, but the page looks like it grants
    access it does not.
    """
    from flask_login import current_user

    static_max_age = app.config["STATIC_MAX_AGE"]

    app.session_interface = _StaticFriendlySession()

    @app.after_request
    def add_cache_headers(response):
        if request.endpoint == "static":
            if static_max_age:
                response.headers["Cache-Control"] = f"public, max-age={static_max_age}, immutable"
            return response

        if current_user.is_authenticated:
            response.headers.setdefault("Cache-Control", "no-store, private")
            response.vary.add("Cookie")
        return response


class _StaticFriendlySession(SecureCookieSessionInterface):
    """Leaves the session out of static file responses.

    Flask adds ``Vary: Cookie`` to any response whose session was touched, and
    Flask-Login touches it on every request — including requests for CSS. That
    happens in ``save_session``, which runs *after* ``after_request``, so an
    ``after_request`` hook cannot remove it.

    A static file is byte-identical for every visitor, so varying it by cookie is
    both untrue and expensive: a shared cache has to store one copy per session.
    Nothing legitimately mutates the session while serving a file, so skipping the
    save for those requests costs nothing.
    """

    def save_session(self, app, session, response):
        if request.endpoint == "static":
            return
        super().save_session(app, session, response)


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

    login_manager.login_view = "auth.login"
    login_manager.login_message = "You must be logged in to do that."


def _register_blueprints(app: Flask) -> None:
    from blog.blueprints import auth, feeds, main, posts, users

    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(feeds.bp)
