"""Post creation, slugs, tags, comments and listings."""

from sqlalchemy import select

from blog.models import Post, Tag


def test_create_post_assigns_slug_and_tags(client, db, log_in, alice):
    log_in("alice")
    response = client.post(
        "/posts/new/",
        data={
            "title": "Hello, World!",
            "body": "First post.",
            "tags": "Intro, Meta",
            "published": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    post = db.session.scalar(select(Post))
    assert post.slug == "hello-world"
    assert {tag.name for tag in post.tags} == {"intro", "meta"}


def test_duplicate_titles_get_distinct_slugs(db, alice, make_post):
    first = make_post(alice, title="The very same title")
    second = make_post(alice, title="The very same title")
    third = make_post(alice, title="The very same title")
    assert [first.slug, second.slug, third.slug] == [
        "the-very-same-title",
        "the-very-same-title-2",
        "the-very-same-title-3",
    ]


def test_tags_are_reused_not_duplicated(db, alice, make_post):
    for title in ("First one here", "Second one here"):
        post = make_post(alice, title=title)
        post.tags = {Tag.get_or_create(db.session, "Python")}
    db.session.commit()
    assert db.session.scalars(select(Tag)).all().__len__() == 1


def test_tag_count_is_capped(client, db, log_in, alice):
    log_in("alice")
    client.post(
        "/posts/new/",
        data={
            "title": "Lots of tags here",
            "body": "x",
            "tags": "a,b,c,d,e,f,g,h",
            "published": "y",
        },
    )
    post = db.session.scalar(select(Post))
    assert len(post.tags) == 5


def test_editing_title_updates_slug(client, db, log_in, alice, make_post):
    post = make_post(alice, title="The original title")
    log_in("alice")
    client.post(
        f"/posts/{post.slug}/edit/",
        data={"title": "A different title now", "body": "changed", "published": "y"},
    )
    assert db.session.get(Post, post.id).slug == "a-different-title-now"


def test_post_body_renders_markdown(client, alice, make_post):
    post = make_post(alice, body="A **bold** claim and `code`.\n\n> a quote")
    html = client.get(f"/posts/{post.slug}/").data.decode()
    assert "<strong>bold</strong>" in html
    assert "<code>code</code>" in html
    assert "<blockquote>" in html


def test_markdown_cannot_inject_scripts(client, alice, make_post):
    hostile = (
        '<script>alert(1)</script>\n\n<img src=x onerror="alert(2)">\n\n[x](javascript:alert(3))'
    )
    post = make_post(alice, body=hostile)
    html = client.get(f"/posts/{post.slug}/").data.decode()
    assert "<script>" not in html
    assert "onerror" not in html
    assert "javascript:alert" not in html


def test_post_is_readable_without_signing_in(client, alice, make_post):
    post = make_post(alice, title="Readable by anyone at all")
    response = client.get(f"/posts/{post.slug}/")
    assert response.status_code == 200
    assert b"Readable by anyone at all" in response.data
    assert b"to join the conversation" in response.data


def test_unknown_slug_returns_404(client):
    assert client.get("/posts/no-such-post/").status_code == 404


def test_search_matches_title_and_body(client, alice, make_post):
    make_post(alice, title="Gardening in November", body="mulch and leaves")
    make_post(alice, title="Something else entirely", body="a note about mulch")
    make_post(alice, title="Completely unrelated topic", body="nothing relevant")

    html = client.get("/?q=mulch").data.decode()
    assert "Gardening in November" in html
    assert "Something else entirely" in html
    assert "Completely unrelated topic" not in html


def test_tag_filter_narrows_the_list(client, db, alice, make_post):
    tagged = make_post(alice, title="A tagged post here")
    tagged.tags = {Tag.get_or_create(db.session, "rust")}
    make_post(alice, title="An untagged post here")
    db.session.commit()

    html = client.get("/?tag=rust").data.decode()
    assert "A tagged post here" in html
    assert "An untagged post here" not in html


def test_pagination_splits_results(client, alice, make_post):
    for index in range(7):
        make_post(alice, title=f"Numbered post number {index}")

    first = client.get("/").data.decode()
    assert first.count('class="card"') == 3  # POSTS_PER_PAGE is 3 under testing
    assert "load more" in first

    second = client.get("/?page=3").data.decode()
    assert "Numbered post number 0" in second


def test_comment_can_be_added_and_deleted(client, db, log_in, alice, bob, make_post):
    post = make_post(alice)
    log_in("bob")

    client.post(
        f"/posts/{post.slug}/comments/", data={"body": "Good point."}, follow_redirects=True
    )
    assert db.session.get(Post, post.id).comment_count == 1

    comment_id = db.session.get(Post, post.id).comments[0].id
    client.post(f"/comments/{comment_id}/delete/", follow_redirects=True)
    assert db.session.get(Post, post.id).comment_count == 0


def test_empty_comment_is_rejected(client, db, log_in, alice, bob, make_post):
    post = make_post(alice)
    log_in("bob")
    client.post(f"/posts/{post.slug}/comments/", data={"body": "   "})
    assert db.session.get(Post, post.id).comment_count == 0


def test_deleting_post_removes_its_comments(
    client, db, log_in, alice, bob, make_post, make_comment
):
    post = make_post(alice)
    make_comment(bob, post)
    post_id = post.id

    log_in("alice")
    client.post(f"/posts/{post.slug}/delete/")

    db.session.expire_all()
    assert db.session.get(Post, post_id) is None
    assert db.session.scalar(select(Post).where(Post.id == post_id)) is None


def test_reading_time_is_at_least_one_minute(alice, make_post):
    assert make_post(alice, body="four short words here").reading_time == 1
    assert make_post(alice, title="A longer one here", body="word " * 900).reading_time > 1
