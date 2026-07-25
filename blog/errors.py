"""HTTP error handlers.

The previous implementation registered handlers that took no arguments, so any
404 or 500 raised a ``TypeError`` inside the handler itself. Flask always passes
the exception, so each handler accepts it.
"""

from __future__ import annotations

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException, default_exceptions

from blog.extensions import db

TITLES = {
    400: "Bad request",
    403: "Not allowed",
    404: "Not found",
    500: "Something broke",
}

MESSAGES = {
    400: "That request could not be understood.",
    403: "You do not have permission to do that.",
    404: "The page you are looking for does not exist.",
    500: "An unexpected error occurred. It has been logged.",
}


def _custom_description(code: int, error: Exception | None) -> str | None:
    """Return the caller's own message, if they passed one to ``abort()``.

    ``abort(403, "You cannot like your own post.")`` should show that sentence;
    a bare ``abort(403)`` should show ours rather than Werkzeug's boilerplate. The
    two are told apart by comparing against Werkzeug's default for the code.
    """
    if not isinstance(error, HTTPException):
        return None
    default = default_exceptions[code]().description
    return error.description if error.description != default else None


def _render(code: int, error: Exception | None = None):
    description = _custom_description(code, error)
    return (
        render_template(
            "errors/error.html",
            code=code,
            heading=TITLES[code],
            message=description or MESSAGES[code],
            page_title="ERROR",
            accent="grey",
        ),
        code,
    )


def register(app: Flask) -> None:
    """Attach the error handlers to ``app``."""

    @app.errorhandler(400)
    def bad_request(error):
        return _render(400, error)

    @app.errorhandler(403)
    def forbidden(error):
        return _render(403, error)

    @app.errorhandler(404)
    def not_found(error):
        return _render(404, error)

    @app.errorhandler(500)
    def server_error(error):
        # A failed request can leave the session dirty; roll back so the error
        # page itself can still query the database.
        db.session.rollback()
        app.logger.exception("Unhandled error", exc_info=error)
        return _render(500, error)
