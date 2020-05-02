"""Contains WSGI for blog app."""

from os import environ

from blog import create_app

# Load app_config from environment variable
app_config = environ.get("APP_CONFIG", "config.DevelopmentConfig")

app = create_app(app_config)


def start():
    """Start blog web server."""
    app.run()


if __name__ == "__main__":
    start()
