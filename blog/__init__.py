"""Contains app factory for blog app."""

from flask import Flask

from blog.extensions import compress, db, login_manager
from blog.views import app_blueprint, error400, error404, error500


def create_app(app_config):
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(app_config)

    # Initialize plugins
    compress.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)

    with app.app_context():
        # Register blueprints
        app.register_blueprint(app_blueprint)

        # Register error pages
        app.register_error_handler(400, error400)
        app.register_error_handler(404, error404)
        app.register_error_handler(500, error500)

        # Create database tables for our data models
        db.create_all()

        return app
