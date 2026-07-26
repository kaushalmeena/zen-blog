"""Caching rules for static assets and for signed-in pages.

Two opposite requirements. Static files are identical for everyone and should be
cached hard; pages rendered for a signed-in user must not be cached at all.
"""

import re
from pathlib import Path

import pytest
from flask import url_for

from blog import create_app
from blog.assets import stamp


def static_url(app, filename):
    with app.test_request_context():
        return url_for("static", filename=filename)


def test_static_urls_carry_a_content_stamp(app):
    url = static_url(app, "styles/main.css")
    assert re.fullmatch(r"/static/styles/main\.css\?v=[0-9a-f]{10}", url), url


def test_stamp_follows_the_file_contents(tmp_path):
    asset = tmp_path / "a.css"
    asset.write_text("a {}")
    first = stamp(asset)

    asset.write_text("b {}")
    assert stamp(asset) != first, "editing a file must change its stamp"

    asset.write_text("a {}")
    assert stamp(asset) == first, "identical contents must give an identical stamp"


def test_stamp_is_absent_for_a_missing_file(tmp_path):
    assert stamp(tmp_path / "nope.css") is None


def test_missing_asset_still_produces_a_usable_url(app):
    """A typo in a filename must not break URL building."""
    assert static_url(app, "styles/nope.css") == "/static/styles/nope.css"


def test_every_referenced_asset_exists(client, app):
    """Since the stamp is skipped for missing files, a typo would go unnoticed."""
    html = client.get("/").data.decode()
    referenced = set(re.findall(r"/static/([^\s\"'?#]+)", html))
    assert referenced, "no static references found"

    for filename in referenced:
        assert (Path(app.static_folder) / filename).exists(), filename


def test_static_responses_do_not_vary_by_cookie(client, app):
    """A cookie-varying asset cannot be shared between visitors in a cache."""
    response = client.get(static_url(app, "styles/main.css"))
    assert response.status_code == 200
    assert "Cookie" not in response.headers.get("Vary", "")
    assert "Set-Cookie" not in response.headers


def test_static_does_not_vary_by_cookie_when_logged_in(client, app, log_in, alice):
    log_in("alice")
    response = client.get(static_url(app, "styles/main.css"))
    assert "Cookie" not in response.headers.get("Vary", "")
    # The private page policy must not leak onto public assets.
    assert "no-store" not in response.headers.get("Cache-Control", "")


def test_production_caches_static_immutably(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "not-a-real-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    app = create_app("production")

    response = app.test_client().get(static_url(app, "styles/main.css"))
    cache_control = response.headers["Cache-Control"]
    assert "public" in cache_control
    assert "immutable" in cache_control
    assert "max-age=31536000" in cache_control


def test_development_still_revalidates_static(monkeypatch):
    """Long-lived caching in development would hide edits behind a stale copy."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = create_app("development")
    assert app.config["STATIC_MAX_AGE"] == 0

    response = app.test_client().get(static_url(app, "styles/main.css"))
    assert "immutable" not in response.headers.get("Cache-Control", "")


@pytest.mark.parametrize("path", ["/", "/tags/"])
def test_pages_for_anonymous_visitors_are_cacheable(client, path):
    assert "no-store" not in client.get(path).headers.get("Cache-Control", "")
