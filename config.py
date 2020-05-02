"""Contains configurations to be used while running blog app."""

from os.path import abspath, dirname, join

from dotenv import load_dotenv

BASE_DIR = abspath(dirname(__file__))

# Create SQLite URI
sqlite_uri = "sqlite:///" + join(BASE_DIR, "database", "blog.db")

# Load environment variables from '.env' file
load_dotenv()

print(sqlite_uri)


class BaseConfig:
    """Contains base configuration to be inherited by both dev/prod configurations."""

    SQLALCHEMY_DATABASE_URI = sqlite_uri


class ProductionConfig(BaseConfig):
    """Contains configuration to be used while running app in production mode."""

    ENV = "production"


class DevelopmentConfig(BaseConfig):
    """Contains configuration to be used while running app in development mode."""

    ENV = "development"
    DEBUG = True
