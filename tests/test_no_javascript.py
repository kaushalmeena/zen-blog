"""The site with JavaScript switched off.

The rest of the suite runs with ``WTF_CSRF_ENABLED = False``, which hid a real
bug: the hand-written forms (logout, like, save, follow, delete, theme) had no
hidden CSRF field. htmx supplies the token as a header, so those forms worked in a
browser and returned 400 the moment JavaScript was unavailable.

These tests turn CSRF on, scrape each form's own token out of the page, and post
it the way a browser without htmx would.
"""

import re

import pytest

TOKEN_IN_FORM = re.compile(r'<form[^>]*action="(?P<action>[^"]+)"(?P<rest>.*?)</form>', re.DOTALL)
HIDDEN_TOKEN = re.compile(r'name="csrf_token" value="(?P<token>[^"]+)"')


@pytest.fixture
def app(app):
    """Same app, but with CSRF protection active."""
    app.config["WTF_CSRF_ENABLED"] = True
    return app


def forms_on(client, path):
    """Return {action: csrf token} for every form on ``path``."""
    html = client.get(path).data.decode()
    found = {}
    for match in TOKEN_IN_FORM.finditer(html):
        token = HIDDEN_TOKEN.search(match.group("rest"))
        found[match.group("action")] = token.group("token") if token else None
    return found


@pytest.fixture
def signed_in(client, alice, make_user):
    """Log in without htmx, using the login form's own token."""
    html = client.get("/login/").data.decode()
    token = HIDDEN_TOKEN.search(html).group("token")
    response = client.post(
        "/login/",
        data={"csrf_token": token, "username": "alice", "password": "correct horse battery"},
        follow_redirects=True,
    )
    assert b"Logged in as alice" in response.data
    return client


def test_logout_form_carries_a_token_and_works(signed_in):
    """Regression: this form had no token, so logging out returned 400."""
    tokens = forms_on(signed_in, "/")
    assert tokens["/logout/"], "logout form is missing its CSRF field"

    response = signed_in.post(
        "/logout/", data={"csrf_token": tokens["/logout/"]}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Logged out." in response.data


def test_like_and_save_forms_work_without_htmx(signed_in, bob, make_post):
    post = make_post(bob, title="Something to react to")
    tokens = forms_on(signed_in, f"/posts/{post.slug}/")

    for action in (f"/posts/{post.slug}/like/", f"/posts/{post.slug}/save/"):
        assert tokens[action], f"{action} form is missing its CSRF field"
        response = signed_in.post(action, data={"csrf_token": tokens[action]})
        assert response.status_code == 302, action


def test_follow_form_works_without_htmx(signed_in, bob):
    tokens = forms_on(signed_in, "/u/bob/")
    action = "/u/bob/follow/"
    assert tokens[action]
    assert signed_in.post(action, data={"csrf_token": tokens[action]}).status_code == 302


def test_delete_forms_work_without_htmx(signed_in, alice, make_post, make_comment):
    post = make_post(alice, title="A post to remove")
    comment = make_comment(alice, post)

    tokens = forms_on(signed_in, f"/posts/{post.slug}/")

    comment_action = f"/comments/{comment.id}/delete/"
    assert tokens[comment_action]
    assert (
        signed_in.post(comment_action, data={"csrf_token": tokens[comment_action]}).status_code
        == 302
    )

    post_action = f"/posts/{post.slug}/delete/"
    assert tokens[post_action]
    assert signed_in.post(post_action, data={"csrf_token": tokens[post_action]}).status_code == 302


def test_theme_switch_works_without_htmx(client):
    """Anonymous visitors get the switch too, so it must not require a login."""
    tokens = forms_on(client, "/")
    assert tokens["/theme/"]

    response = client.post("/theme/", data={"csrf_token": tokens["/theme/"], "theme": "dark"})
    assert response.status_code == 302
    assert "theme=dark" in response.headers["Set-Cookie"]


def test_missing_token_is_still_rejected(signed_in, bob, make_post):
    """The tokens must be doing real work, not just decorating the markup."""
    post = make_post(bob)
    assert signed_in.post(f"/posts/{post.slug}/like/").status_code == 400


def test_search_submits_without_a_visible_button(client, alice, make_post):
    """The submit control is hidden, but Enter must still perform a search."""
    make_post(alice, title="Reachable without clicking")
    html = client.get("/").data.decode()

    assert '<button class="visually-hidden" type="submit">' in html
    assert (
        'class="btn btn--solid btn--keep-label" type="submit">\n    <span class="btn__label">search'
        not in html
    )
    assert b"Reachable without clicking" in client.get("/?q=Reachable").data
