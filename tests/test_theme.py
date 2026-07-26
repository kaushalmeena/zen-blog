"""The cookie-backed light/dark switch."""

from pathlib import Path

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

    for path in ("/", f"/posts/{post.slug}/", "/tags/", "/login/"):
        assert 'data-theme="dark"' in client.get(path).data.decode(), path


def test_anonymous_visitors_get_a_header_toggle(client):
    """They have no account menu, so the switch has to stay in the header."""
    html = client.get("/").data.decode()
    assert 'class="theme-switch theme-switch--to-dark"' in html
    assert "account-menu" not in html


def test_signed_in_users_get_the_options_in_the_account_menu(client, log_in, alice):
    log_in("alice")
    html = client.get("/").data.decode()

    # The header toggle moves into the menu, which names all three states.
    assert "theme-switch" not in html
    for value in ("light", "dark", "auto"):
        assert f'<input type="hidden" name="theme" value="{value}" />' in html


def test_active_theme_is_ticked_in_the_menu(client, log_in, alice):
    log_in("alice")
    client.post("/theme/", data={"theme": "dark"})
    html = " ".join(client.get("/").data.decode().split())

    # The dark row is marked current; the others are not.
    dark_row = html.split('name="theme" value="dark" />')[1].split("</form>")[0]
    assert 'aria-current="true"' in dark_row
    light_row = html.split('name="theme" value="light" />')[1].split("</form>")[0]
    assert 'aria-current="true"' not in light_row


def test_both_switch_directions_are_always_present(client):
    """Switching is one click from any state.

    The server cannot see the visitor's OS preference, so it cannot pick a single
    correct target while the stored theme is `auto`. Both controls ship on every
    page and CSS hides the one matching the current appearance — so going dark to
    light is never two clicks.
    """
    html = client.get("/").data.decode()

    assert 'class="theme-switch theme-switch--to-dark"' in html
    assert 'class="theme-switch theme-switch--to-light"' in html
    assert '<input type="hidden" name="theme" value="dark" />' in html
    assert '<input type="hidden" name="theme" value="light" />' in html


def test_css_hides_exactly_one_direction_per_state():
    """The one-click promise lives in CSS, so assert the rules that deliver it."""
    css = (Path("blog/static/styles/main.css")).read_text()

    # Light appearance: only the "go dark" control shows.
    assert ".theme-switch--to-light {\n  display: none;\n}" in css
    # Explicit dark: the pair flips.
    assert ':root[data-theme="dark"] .theme-switch--to-light {\n  display: inline;\n}' in css
    assert ':root[data-theme="dark"] .theme-switch--to-dark {\n  display: none;\n}' in css
    # auto on a dark OS behaves like dark, which is the case that used to need
    # two clicks.
    assert ':root[data-theme="auto"] .theme-switch--to-light' in css
    assert ':root[data-theme="auto"] .theme-switch--to-dark' in css


def test_menu_names_each_theme_state(client, log_in, alice):
    """Each option is named in words, not left to its icon alone."""
    log_in("alice")
    html = " ".join(client.get("/").data.decode().split())
    row = html.split('<div class="theme-row">')[1].split("</div>")[0]

    for label in ("light", "dark", "system"):
        assert f'<span class="theme-option__label">{label}</span>' in row, label


def test_each_theme_option_has_an_icon(client, log_in, alice):
    log_in("alice")
    row = " ".join(client.get("/").data.decode().split())
    row = row.split('<div class="theme-row">')[1].split("</div>")[0]

    assert "icons.svg?v=" in row
    for symbol in ("sun", "moon", "contrast"):
        assert f"#{symbol}" in row, symbol


def test_theme_label_is_not_styled_like_an_option():
    """It reads as a caption because it breaks the interactive text pattern."""
    from pathlib import Path

    css = Path("blog/static/styles/main.css").read_text()
    label = css.split(".popover__label {")[1].split("}")[0]
    option = css.split("\n.theme-option {")[1].split("}")[0]

    # Interactive rows are sans tracked capitals; the label is serif italic.
    assert "--font-serif" in label
    assert "font-style: italic" in label
    assert "text-transform: none" in label

    assert "--font-sans" in option
    assert "text-transform: uppercase" in option


def test_active_option_is_marked_for_every_state(client, log_in, alice):
    """Exactly one theme option carries aria-current, and it is the stored one."""
    log_in("alice")

    for choice in ("light", "dark", "auto"):
        client.post("/theme/", data={"theme": choice})
        html = " ".join(client.get("/").data.decode().split())
        row = html.split('<div class="theme-row">')[1].split("</div>")[0]
        active = row.split(f'name="theme" value="{choice}" />')[1].split("</form>")[0]
        assert 'aria-current="true"' in active, choice
        assert row.count('aria-current="true"') == 1, choice


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
