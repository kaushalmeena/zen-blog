"""Contains configurations to be used while running blog app."""

from os import environ
from os.path import abspath, dirname, join

from dotenv import load_dotenv

BASE_DIR = abspath(dirname(__file__))

# Create SQLite URI
sqlite_uri = "sqlite:///" + join(BASE_DIR, "database", "blog.db")

# Load environment variables from '.env' file
load_dotenv()


class BaseConfig:
    """Contains base configuration to be inherited by both dev/prod configurations."""

    SQLALCHEMY_DATABASE_URI = sqlite_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(BaseConfig):
    """Contains configuration to be used while running app in production mode."""

    ENV = "production"
    SECRET_KEY = environ.get("SECRET_KEY")


class DevelopmentConfig(BaseConfig):
    """Contains configuration to be used while running app in development mode."""

    ENV = "development"
    SECRET_KEY = "dev"
    DEBUG = True
