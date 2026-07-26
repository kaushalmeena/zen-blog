"""Header structure and the action row."""


def squash(html: bytes) -> str:
    return " ".join(html.decode().split())


def test_nav_links_are_plain_text_without_icons(client):
    """The nav used icon buttons; it is now text, underlined when current."""
    html = squash(client.get("/").data)

    assert '<a class="navlink" href="/" aria-current="page">home</a>' in html
    assert '<a class="navlink" href="/tags/">tags</a>' in html
    # No icon sprite references inside the nav element.
    nav = html.split('<nav class="site-nav"')[1].split("</nav>")[0]
    assert "icons.svg" not in nav


def test_current_page_is_marked_on_the_nav(client):
    tags_page = squash(client.get("/tags/").data)
    assert '<a class="navlink" href="/tags/" aria-current="page">tags</a>' in tags_page
    assert '<a class="navlink" href="/">home</a>' in tags_page


def test_tagline_is_not_in_the_header(client):
    """The strapline was dropped to give the top row back to the brand and account."""
    html = squash(client.get("/").data)
    header = html.split("<header")[1].split("</header>")[0]
    assert "A minimal, JavaScript-free" not in header
    # It survives as the meta description, which is where it earns its keep.
    assert 'name="description" content="A minimal, JavaScript-free' in html


def test_account_menu_is_a_native_popover(client, log_in, alice):
    log_in("alice")
    html = squash(client.get("/").data)

    assert 'popovertarget="account-menu"' in html
    assert 'id="account-menu" popover' in html


def account_menu(html: str) -> str:
    """The popover's markup only.

    Bounded by the nav that follows it in the DOM — without that bound the nav's
    own saved/drafts links would count as menu contents.
    """
    after_open = html.split('id="account-menu" popover>')[1]
    return after_open.split('<nav class="site-nav"')[0]


def test_account_menu_holds_only_account_level_items(client, log_in, alice):
    """Saved and drafts have nav links, so repeating them in the menu is noise."""
    log_in("alice")
    html = squash(client.get("/").data)
    menu = account_menu(html)

    assert "<span>profile</span>" in menu
    assert "<span>settings</span>" in menu
    assert "<span>logout</span>" in menu

    assert "saved posts" not in menu
    assert "drafts" not in menu
    assert "your profile" not in menu

    # They stay reachable from the nav.
    nav = html.split('<nav class="site-nav"')[1].split("</nav>")[0]
    assert 'href="/saved/"' in nav
    assert 'href="/drafts/"' in nav


def test_account_trigger_shows_the_username_next_to_the_avatar(client, log_in, alice):
    log_in("alice")
    html = squash(client.get("/").data)

    trigger = html.split('class="user-trigger"')[1].split("</button>")[0]
    assert "alice avatar" in trigger  # the identicon
    assert '<span class="user-trigger__name">alice</span>' in trigger
    # Static URLs carry a cache-busting stamp, so the query sits before the fragment.
    assert "icons.svg?v=" in trigger
    assert "#chevron-down" in trigger


def test_account_menu_is_absent_for_anonymous_visitors(client):
    html = client.get("/").data.decode()
    assert "account-menu" not in html
    assert "login" in html


def test_auth_links_sit_in_the_nav_styled_like_the_other_links(client):
    """They were buttons in the top bar; now they are nav links on the right."""
    nav = squash(client.get("/").data).split('<nav class="site-nav"')[1].split("</nav>")[0]

    assert '<a class="navlink" href="/login/">login</a>' in nav
    assert '<a class="navlink navlink--accent" href="/register/">register</a>' in nav
    # No button treatment anywhere in the nav.
    assert "btn" not in nav


def test_new_post_link_sits_in_the_nav_for_logged_in_users(client, log_in, alice):
    log_in("alice")
    html = squash(client.get("/").data)
    nav = html.split('<nav class="site-nav"')[1].split("</nav>")[0]

    assert '<a class="navlink navlink--accent" href="/posts/new/">new post</a>' in nav
    assert "btn" not in nav
    # And it is no longer duplicated in the top bar.
    bar = html.split('<div class="site-header__bar">')[1].split('<nav class="site-nav"')[0]
    assert "/posts/new/" not in bar


def test_primary_action_is_pushed_to_the_trailing_edge(client):
    nav = squash(client.get("/").data).split('<nav class="site-nav"')[1].split("</nav>")[0]
    spacer = nav.index('class="site-nav__spacer"')
    assert nav.index('href="/tags/"') < spacer < nav.index('href="/login/"')


def test_popover_needs_no_javascript(client, log_in, alice):
    """The Popover API is declarative, so the menu must not add a script."""
    log_in("alice")
    html = client.get("/").data.decode()
    assert html.count("<script") == 1  # vendored htmx only
    assert "onclick" not in html


def test_action_row_slots_share_one_shape(client, log_in, alice, bob, make_post):
    """Uneven buttons came from the active state adding a box the others lacked."""
    post = make_post(bob, title="A post to react to")
    log_in("alice")

    off = squash(client.get(f"/posts/{post.slug}/").data)
    row = off.split('<div class="actions"')[1].split("</div>")[0]
    assert row.count('class="action"') >= 1

    client.post(f"/posts/{post.slug}/like/")
    on = squash(client.get(f"/posts/{post.slug}/").data)
    on_row = on.split('<div class="actions" id=')[1].split('<div class="actions">')[0]

    # Toggling on adds only a modifier class, never a different element shape.
    assert 'class="action action--on"' in on_row
    # The old mixed shapes are gone from the row.
    assert "btn--quiet" not in on_row
    assert "meta-item" not in on_row


def test_action_row_uses_equal_width_slots():
    """The evenness is a CSS guarantee; assert the rule that provides it."""
    from pathlib import Path

    css = Path("blog/static/styles/main.css").read_text()
    action_block = css.split(".action {")[1].split("}")[0]
    # Slots are content-sized and left-aligned; centring inside a fixed width is
    # what made the icons sit at different offsets.
    assert "justify-content: center" not in action_block
    assert "min-width" not in action_block
    # The count carries the width reservation instead.
    count_block = css.split(".action__count {")[1].split("}")[0]
    assert "min-width:" in count_block
    assert "tabular-nums" in count_block

    # The on-state must not add border or background, which would change size.
    on_block = css.split(".action--on {")[1].split("}")[0]
    assert "border" not in on_block
    assert "background" not in on_block


def test_paper_background_is_a_plain_colour():
    """The zen redesign: warm paper, no texture image and no drawn pattern."""
    from pathlib import Path

    css = Path("blog/static/styles/main.css").read_text()
    assert "--color-light-bg: #f7f5f0" in css
    assert "--color-dark-bg: #181716" in css
    # No image, and no generated graph-paper grid either.
    assert "texture.png" not in css
    assert "--color-light-grid" not in css
    body_block = css.split("\nbody {")[1].split("}")[0]
    assert "background-image" not in body_block
