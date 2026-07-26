"""Registration, login and logout."""

from blog.models import User
from tests.conftest import PASSWORD


def test_register_creates_account_and_logs_in(client, db):
    response = client.post(
        "/register/",
        data={"username": "newcomer", "password": "longenoughpw", "confirm": "longenoughpw"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert db.session.query(User).filter_by(username="newcomer").one()
    assert b"Welcome, newcomer" in response.data


def test_register_rejects_duplicate_username(client, alice):
    response = client.post(
        "/register/",
        data={"username": "alice", "password": "longenoughpw", "confirm": "longenoughpw"},
    )
    assert response.status_code == 200
    assert b"already taken" in response.data


def test_register_rejects_short_password(client):
    response = client.post(
        "/register/", data={"username": "shorty", "password": "abc", "confirm": "abc"}
    )
    assert b"at least 8 characters" in response.data


def test_register_rejects_mismatched_confirmation(client):
    response = client.post(
        "/register/",
        data={"username": "mismatch", "password": "longenoughpw", "confirm": "different-pw"},
    )
    assert b"Passwords must match" in response.data


def test_login_with_bad_password_fails(client, alice):
    response = client.post("/login/", data={"username": "alice", "password": "nope"})
    assert b"Invalid username or password" in response.data


def test_login_succeeds(log_in, alice):
    response = log_in("alice")
    assert b"Logged in as alice" in response.data


def test_password_is_hashed_not_stored(alice):
    assert alice.password_hash != PASSWORD
    assert alice.check_password(PASSWORD)
    assert not alice.check_password("something else")


def test_logout_requires_post(client, log_in, alice):
    """A GET logout URL could be triggered by a prefetch or an <img> tag."""
    log_in("alice")
    assert client.get("/logout/").status_code == 405
    assert client.post("/logout/", follow_redirects=True).status_code == 200


def test_next_parameter_cannot_redirect_off_site(client, alice):
    response = client.post(
        "/login/?next=https://evil.example/steal",
        data={"username": "alice", "password": PASSWORD},
    )
    assert response.headers["Location"] == "/"


def test_next_parameter_allows_local_path(client, alice):
    response = client.post("/login/?next=/saved/", data={"username": "alice", "password": PASSWORD})
    assert response.headers["Location"] == "/saved/"


def test_protected_pages_redirect_anonymous_users(client):
    for path in ("/posts/new/", "/saved/", "/drafts/", "/settings/", "/following/"):
        response = client.get(path)
        assert response.status_code == 302, path
        assert "/login/" in response.headers["Location"], path
