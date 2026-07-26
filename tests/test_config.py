"""Configuration wiring, mostly the database URL.

`database_url` exists because managed Postgres hosts hand out a scheme that
SQLAlchemy resolves to a driver this project does not install.
"""

import pytest

from blog.config import database_url

SUPABASE = "postgres:pw@db.example.supabase.co:5432/postgres"


@pytest.mark.parametrize("prefix", ["postgres://", "postgresql://"])
def test_postgres_urls_are_pointed_at_psycopg(monkeypatch, prefix):
    monkeypatch.setenv("DATABASE_URL", prefix + SUPABASE)

    assert database_url() == f"postgresql+psycopg://{SUPABASE}"


def test_an_explicit_driver_is_left_alone(monkeypatch):
    """Someone who names a driver means it."""
    url = f"postgresql+psycopg2://{SUPABASE}"
    monkeypatch.setenv("DATABASE_URL", url)

    assert database_url() == url


def test_sqlite_urls_are_left_alone(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///local.db")

    assert database_url() == "sqlite:///local.db"


@pytest.mark.parametrize("value", ["", None])
def test_missing_url_stays_falsy(monkeypatch, value):
    """The instance-folder SQLite fallback keys off this being empty."""
    if value is None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("DATABASE_URL", value)

    assert not database_url()
