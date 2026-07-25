"""The cookie-backed light/dark switch."""

import pytest

from blog.theming import COOKIE_NAME


def test_default_is_auto(client):
    html = client.get("/").data.decode()
    assert '<html lang="en" data-theme="auto">' in html


@pytest.mark.parametrize("choice", ["light", "dark", "auto"])
def test_choice_is_stored_and_applied(client, choice):
    client.post("/theme/", data={"theme": choice})
    assert client.get_cookie(COOKIE_NAME).value == choice
    assert f'data-theme="{choice}"' in client.get("/").data.decode()


def test_choice_survives_navigation(client, alice, make_post):
    post = make_post(alice)
    client.post("/theme/", data={"theme": "dark"})

    for path in ("/", f"/posts/{post.slug}/", "/tags/", "/sign-in/"):
        assert 'data-theme="dark"' in client.get(path).data.decode(), path


def test_switch_cycles_through_all_three_states(client):
    """One button, three states: auto to light to dark and back."""

    def offered():
        html = client.get("/").data.decode()
        start = html.index('action="/theme/"')
        return html[start : start + 400].split('name="theme" value="')[1].split('"')[0]

    assert offered() == "light"
    client.post("/theme/", data={"theme": "light"})
    assert offered() == "dark"
    client.post("/theme/", data={"theme": "dark"})
    assert offered() == "auto"


def test_unknown_theme_is_rejected(client):
    assert client.post("/theme/", data={"theme": "neon"}).status_code == 400
    assert client.get_cookie(COOKIE_NAME) is None


def test_garbage_cookie_falls_back_to_auto(client):
    client.set_cookie(COOKIE_NAME, "../../etc/passwd")
    assert 'data-theme="auto"' in client.get("/").data.decode()


def test_switch_returns_the_visitor_to_the_same_page(client, alice, make_post):
    post = make_post(alice)
    response = client.post(
        "/theme/",
        data={"theme": "dark"},
        headers={"Referer": f"http://localhost/posts/{post.slug}/"},
    )
    assert response.headers["Location"] == f"http://localhost/posts/{post.slug}/"


def test_switch_ignores_an_off_site_referrer(client):
    """Otherwise the switch becomes an open redirect."""
    response = client.post(
        "/theme/", data={"theme": "dark"}, headers={"Referer": "https://evil.example/landing"}
    )
    assert response.headers["Location"] == "/"


def test_switch_is_available_to_anonymous_visitors(client):
    assert b'action="/theme/"' in client.get("/").data
