"""Error pages.

The handlers in the previous version were declared as ``def error404():`` with no
parameter. Flask always passes the exception, so every 404 and 500 blew up inside
the handler instead of rendering a page.
"""


def test_404_renders_the_error_page(client):
    response = client.get("/no/such/path/")
    assert response.status_code == 404
    assert b"Not found" in response.data
    assert b"does not exist" in response.data
    # Werkzeug's stock wording should not leak through.
    assert b"check your spelling" not in response.data


def test_403_shows_our_default_message(client, log_in, alice, bob, make_post):
    post = make_post(alice)
    log_in("bob")
    response = client.post(f"/posts/{post.slug}/delete/")
    assert response.status_code == 403
    assert b"do not have permission" in response.data


def test_403_shows_a_caller_supplied_message(client, log_in, alice, make_post):
    """abort(403, "...") passes a specific reason that should reach the page."""
    post = make_post(alice)
    log_in("alice")
    response = client.post(f"/posts/{post.slug}/like/")
    assert response.status_code == 403
    assert b"cannot like your own post" in response.data


def test_error_pages_keep_the_site_chrome(client):
    """The error page still queries current_user, so it must render fully."""
    body = client.get("/no/such/path/").data
    assert b"MYAPP-BLOG" in body
    assert b"Back to the home page" in body


def test_500_handler_rolls_back_and_renders(app):
    """A broken view must reach the 500 page instead of surfacing a traceback."""

    def explode():
        raise RuntimeError("deliberate failure")

    app.view_functions["main.tags"] = explode
    # Under TESTING, Flask re-raises rather than invoking the handler; turn that
    # off so this exercises the same path a production request would take.
    app.config["PROPAGATE_EXCEPTIONS"] = False

    response = app.test_client().get("/tags/")
    assert response.status_code == 500
    assert b"Something broke" in response.data
    # The handler rolled the session back, so the page's own queries still work.
    assert b"MYAPP-BLOG" in response.data
