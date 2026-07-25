"""htmx fragments and the no-JavaScript fallback for the same routes.

Every interaction has to work twice: once as a fragment swap for htmx, and once
as a plain form post for a browser with JavaScript switched off.
"""


def test_search_returns_only_the_list_fragment(client, htmx, alice, make_post):
    make_post(alice, title="Findable by search here")
    response = client.get("/?q=Findable", headers=htmx)
    body = response.data.decode()

    assert response.status_code == 200
    assert 'id="post-list"' in body
    assert "Findable by search here" in body
    assert "<!doctype html>" not in body.lower()
    assert 'id="messages"' in body  # out-of-band flash region


def test_load_more_returns_the_next_batch_without_the_container(client, htmx, alice, make_post):
    for index in range(5):
        make_post(alice, title=f"Batch post number {index}")

    response = client.get("/?page=2&partial=page", headers=htmx)
    body = response.data.decode()

    assert 'id="post-list"' not in body
    assert 'class="card"' in body


def test_load_more_href_does_not_leak_the_partial_flag(client, htmx, alice, make_post):
    for index in range(5):
        make_post(alice, title=f"Batch post number {index}")

    body = client.get("/?page=1&partial=page", headers=htmx).data.decode()
    assert 'href="/?page=2"' in body
    assert "partial=page&" not in body


def test_like_toggle_returns_the_action_bar(client, htmx, sign_in, alice, bob, make_post):
    post = make_post(alice)
    sign_in("bob")

    on = client.post(f"/posts/{post.slug}/like/", headers=htmx).data.decode()
    assert f'id="post-actions-{post.id}"' in on
    assert 'aria-pressed="true"' in on
    assert "heart-solid" in on

    off = client.post(f"/posts/{post.slug}/like/", headers=htmx).data.decode()
    assert 'aria-pressed="true"' not in off


def test_like_without_htmx_redirects_to_the_post(client, sign_in, alice, bob, make_post):
    post = make_post(alice)
    sign_in("bob")
    response = client.post(f"/posts/{post.slug}/like/")
    assert response.status_code == 302
    assert response.headers["Location"] == f"/posts/{post.slug}/"


def test_save_toggle_updates_the_reading_list(client, htmx, sign_in, alice, bob, make_post):
    post = make_post(alice, title="Worth saving for later")
    sign_in("bob")

    client.post(f"/posts/{post.slug}/save/", headers=htmx)
    assert b"Worth saving for later" in client.get("/saved/").data

    client.post(f"/posts/{post.slug}/save/", headers=htmx)
    assert b"Worth saving for later" not in client.get("/saved/").data


def test_comment_fragment_carries_the_out_of_band_swaps(
    client, htmx, sign_in, alice, bob, make_post
):
    post = make_post(alice)
    sign_in("bob")

    body = client.post(
        f"/posts/{post.slug}/comments/", data={"body": "Adding a thought."}, headers=htmx
    ).data.decode()

    assert "Adding a thought." in body
    assert 'id="comment-count" hx-swap-oob="true"' in body
    assert 'hx-swap-oob="outerHTML"' in body  # the cleared form
    assert 'id="comments-empty" hx-swap-oob="delete"' in body


def test_invalid_comment_fragment_returns_the_form_with_errors(
    client, htmx, sign_in, alice, bob, make_post
):
    post = make_post(alice)
    sign_in("bob")
    body = client.post(
        f"/posts/{post.slug}/comments/", data={"body": ""}, headers=htmx
    ).data.decode()

    assert 'id="comment-form"' in body
    assert 'hx-swap-oob="outerHTML"' in body
    assert "This field is required" in body


def test_comment_delete_fragment_is_only_out_of_band(
    client, htmx, sign_in, alice, bob, make_post, make_comment
):
    post = make_post(alice)
    comment = make_comment(bob, post)
    sign_in("bob")

    body = client.post(f"/comments/{comment.id}/delete/", headers=htmx).data.decode()
    assert 'id="comment-count"' in body
    assert f'id="comment-{comment.id}"' not in body  # nothing to swap in its place


def test_post_delete_uses_hx_redirect(client, htmx, sign_in, alice, make_post):
    post = make_post(alice)
    sign_in("alice")
    response = client.post(f"/posts/{post.slug}/delete/", headers=htmx)
    assert response.headers["HX-Redirect"] == "/"


def test_follow_toggle_returns_the_button(client, htmx, sign_in, alice, bob):
    sign_in("bob")

    on = client.post("/u/alice/follow/", headers=htmx).data.decode()
    assert f'id="follow-{alice.id}"' in on
    assert 'aria-pressed="true"' in on
    assert "following" in on

    off = client.post("/u/alice/follow/", headers=htmx).data.decode()
    assert 'aria-pressed="false"' in off


def test_every_mutating_control_is_a_form_not_a_link(client, sign_in, alice, bob, make_post):
    """Progressive enhancement: state changes must survive JavaScript being off."""
    post = make_post(alice)
    sign_in("bob")
    html = client.get(f"/posts/{post.slug}/").data.decode()

    for action in ("/like/", "/save/"):
        assert f'action="/posts/{post.slug}{action}"' in html
        assert f'href="/posts/{post.slug}{action}"' not in html


def test_pages_reference_no_inline_javascript(client, sign_in, alice, make_post):
    """The old templates used onclick= handlers and a hand-written index.js."""
    post = make_post(alice)
    sign_in("alice")

    for path in ("/", f"/posts/{post.slug}/", "/posts/new/", "/u/alice/", "/settings/"):
        html = client.get(path).data.decode()
        assert "onclick" not in html, path
        assert "onkeyup" not in html, path
        assert "javascript:" not in html, path
        assert html.count("<script") == 1, path  # vendored htmx, nothing else
