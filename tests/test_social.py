"""Following, profiles, drafts and the follow-based feed."""


def test_following_feed_shows_only_followed_authors(
    client, db, sign_in, alice, bob, make_user, make_post
):
    carol = make_user("carol")
    make_post(alice, title="A post by alice here")
    make_post(carol, title="A post by carol here")

    bob.following.add(alice)
    db.session.commit()

    sign_in("bob")
    html = client.get("/following/").data.decode()
    assert "A post by alice here" in html
    assert "A post by carol here" not in html


def squash(html: bytes) -> str:
    """Collapse whitespace so assertions do not depend on template indentation."""
    return " ".join(html.decode().split())


def test_follow_counts_update(client, db, sign_in, alice, bob):
    sign_in("bob")
    client.post("/u/alice/follow/")
    db.session.expire_all()

    assert alice.follower_count == 1
    assert bob.following_count == 1
    assert "<b>1</b> followers" in squash(client.get("/u/alice/").data)


def test_follower_and_following_pages_list_people(client, db, sign_in, alice, bob):
    bob.following.add(alice)
    db.session.commit()

    assert b"bob" in client.get("/u/alice/followers/").data
    assert b"alice" in client.get("/u/bob/following/").data


def test_profile_shows_post_and_like_counts(client, db, alice, bob, make_post):
    post = make_post(alice, title="Something people liked")
    bob.liked_posts.add(post)
    db.session.commit()

    html = squash(client.get("/u/alice/").data)
    assert "Something people liked" in html
    assert "<b>1</b> posts" in html
    assert "<b>1</b> likes received" in html


def test_profile_like_count_excludes_drafts(client, alice, make_post):
    make_post(alice, title="A published post here")
    make_post(alice, title="An unpublished draft", published=False)
    assert alice.post_count == 1


def test_bio_round_trips_through_settings(client, db, sign_in, alice):
    sign_in("alice")
    client.post("/settings/", data={"bio": "Writes about slugs."}, follow_redirects=True)
    db.session.expire_all()
    assert alice.bio == "Writes about slugs."
    assert b"Writes about slugs." in client.get("/u/alice/").data


def test_drafts_page_lists_only_own_drafts(client, sign_in, alice, bob, make_post):
    make_post(alice, title="Alice private draft", published=False)
    make_post(bob, title="Bob private draft", published=False)

    sign_in("alice")
    html = client.get("/drafts/").data.decode()
    assert "Alice private draft" in html
    assert "Bob private draft" not in html


def test_clickable_stats_are_links_and_the_rest_are_not(client, alice, make_post):
    """Only followers/following navigate, so only those may look clickable."""
    make_post(alice, title="Something to count")
    html = squash(client.get("/u/alice/").data)
    stats = html.split('<div class="stats">')[1].split("</div>")[0]

    assert '<a href="/u/alice/followers/">' in stats
    assert '<a href="/u/alice/following/">' in stats
    # Post and like counts go nowhere, so they stay plain text.
    assert stats.count("<a ") == 2


def test_stat_links_are_visually_distinguished():
    """The affordance is CSS, so assert the rules that provide it."""
    from pathlib import Path

    css = Path("blog/static/css/main.css").read_text()

    link = css.split("\n.stats a {")[1].split("}")[0]
    assert "text-decoration-style: dotted" in link
    assert "cursor: pointer" in link

    # Hover and keyboard focus both promote it to a solid accent underline.
    hover = css.split(".stats a:hover,\n.stats a:focus-visible {")[1].split("}")[0]
    assert "var(--accent)" in hover
    assert "text-decoration-style: solid" in hover

    # The static stats must not pick any of that up.
    plain = css.split("\n.stats span {")[1].split("}")[0]
    assert "text-decoration" not in plain
    assert "cursor" not in plain


def test_unknown_user_returns_404(client):
    assert client.get("/u/nobody/").status_code == 404


def test_identicon_is_deterministic_and_inline(alice):
    from blog.avatars import identicon

    first = identicon("alice")
    assert first == identicon("alice")
    assert first != identicon("bob")
    assert first.startswith("<svg")
    assert "alice avatar" in first
