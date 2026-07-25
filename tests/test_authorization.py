"""Ownership checks.

The version of this app before the rewrite let any signed-in user edit or delete
any post or comment: the handlers looked the record up by id and never compared
its owner to the current user. These tests pin that shut.
"""

from blog.models import Comment, Post


def test_stranger_cannot_open_edit_form(client, sign_in, alice, bob, make_post):
    post = make_post(alice)
    sign_in("bob")
    assert client.get(f"/posts/{post.slug}/edit/").status_code == 403


def test_stranger_cannot_submit_edit(client, db, sign_in, alice, bob, make_post):
    post = make_post(alice, title="Alice wrote this one")
    sign_in("bob")
    response = client.post(
        f"/posts/{post.slug}/edit/",
        data={"title": "Bob hijacked this", "body": "mine now", "published": "y"},
    )
    assert response.status_code == 403
    assert db.session.get(Post, post.id).title == "Alice wrote this one"


def test_stranger_cannot_delete_post(client, db, sign_in, alice, bob, make_post):
    post = make_post(alice)
    sign_in("bob")
    assert client.post(f"/posts/{post.slug}/delete/").status_code == 403
    assert db.session.get(Post, post.id) is not None


def test_author_can_delete_own_post(client, db, sign_in, alice, make_post):
    post = make_post(alice)
    sign_in("alice")
    response = client.post(f"/posts/{post.slug}/delete/", follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Post, post.id) is None


def test_stranger_cannot_edit_comment(client, db, sign_in, alice, bob, make_post, make_comment):
    post = make_post(alice)
    comment = make_comment(alice, post, body="alice's words")
    sign_in("bob")

    # The edit form itself must be refused, not just the submission.
    assert client.get(f"/comments/{comment.id}/edit/").status_code == 403

    response = client.post(f"/comments/{comment.id}/edit/", data={"body": "bob's words"})
    assert response.status_code == 403
    assert db.session.get(Comment, comment.id).body == "alice's words"


def test_edit_and_delete_controls_are_hidden_on_other_peoples_comments(
    client, sign_in, alice, bob, make_post, make_comment
):
    post = make_post(alice)
    theirs = make_comment(alice, post, body="written by alice")
    mine = make_comment(bob, post, body="written by bob")

    sign_in("bob")
    html = client.get(f"/posts/{post.slug}/").data.decode()

    assert f"/comments/{theirs.id}/edit/" not in html
    assert f"/comments/{theirs.id}/delete/" not in html
    assert f"/comments/{mine.id}/edit/" in html
    assert f"/comments/{mine.id}/delete/" in html


def test_signed_in_pages_are_not_browser_cacheable(client, sign_in, alice):
    """Otherwise the back button can redisplay another account's controls."""
    assert "no-store" not in client.get("/").headers.get("Cache-Control", "")

    sign_in("alice")
    headers = client.get("/").headers
    assert "no-store" in headers["Cache-Control"]
    # Flask-Compress appends Accept-Encoding, so check membership, not equality.
    assert "Cookie" in headers["Vary"]


def test_stranger_cannot_delete_comment(client, db, sign_in, alice, bob, make_post, make_comment):
    post = make_post(alice)
    comment = make_comment(alice, post)
    sign_in("bob")
    assert client.post(f"/comments/{comment.id}/delete/").status_code == 403
    assert db.session.get(Comment, comment.id) is not None


def test_cannot_like_own_post(client, sign_in, alice, make_post):
    post = make_post(alice)
    sign_in("alice")
    assert client.post(f"/posts/{post.slug}/like/").status_code == 403


def test_cannot_follow_self(client, sign_in, alice):
    sign_in("alice")
    assert client.post("/u/alice/follow/").status_code == 403


def test_draft_is_hidden_from_other_users(client, sign_in, alice, bob, make_post):
    draft = make_post(alice, title="Not ready for anyone yet", published=False)

    assert client.get(f"/posts/{draft.slug}/").status_code == 404

    sign_in("bob")
    assert client.get(f"/posts/{draft.slug}/").status_code == 404


def test_draft_is_visible_to_its_author(client, sign_in, alice, make_post):
    draft = make_post(alice, title="Not ready for anyone yet", published=False)
    sign_in("alice")
    assert client.get(f"/posts/{draft.slug}/").status_code == 200


def test_draft_is_absent_from_listings_and_feed(client, alice, make_post):
    make_post(alice, title="A published one")
    make_post(alice, title="A secret draft here", published=False)

    for path in ("/", "/feed.xml", "/sitemap.xml", "/u/alice/"):
        assert b"A secret draft here" not in client.get(path).data, path


def test_csrf_is_enforced_when_enabled(app, alice, make_post):
    """The testing config disables CSRF; confirm the protection is really wired up."""
    app.config["WTF_CSRF_ENABLED"] = True
    post = make_post(alice)
    client = app.test_client()
    client.post("/sign-in/", data={"username": "alice", "password": "correct horse battery"})
    assert client.post(f"/posts/{post.slug}/like/").status_code == 400
