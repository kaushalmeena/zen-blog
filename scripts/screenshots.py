"""Capture the README screenshots with a real browser.

Drives the locally installed Google Chrome through Playwright, so nothing has to
be downloaded. Run the dev server first, then:

    uv run --with playwright python scripts/screenshots.py

The theme is a cookie the server reads (see blog/theming.py), so the script sets
it explicitly rather than relying on the machine's OS appearance — that is what
makes the shots reproducible on any host.
"""

from __future__ import annotations

import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE = "http://localhost:5001"
OUT = pathlib.Path("screenshots")

# The reading column is 680px plus up to 48px of padding a side, so a 1280-wide
# frame is mostly empty margin. 960 sits close around the content while leaving
# the design's generous whitespace visible.
VIEWPORT = {"width": 960, "height": 640}

USER, PASSWORD = "sable", "password123"

# Every shot is dark; the theme is still set explicitly so the result does not
# depend on the host machine's OS appearance.
THEME = "dark"

DRAFT_BODY = """A log is not a record of what happened. It is a record of what
I noticed at the time, which is a smaller and more useful thing.

> If I did not write down why, I will re-derive it badly.

Two rules I keep:

- Write it while it is still inconvenient.
- Leave the wrong version in place; it is evidence.
"""


def fill_editor(page) -> None:
    """An empty form photographs badly; type a real draft instead."""
    page.fill("#title", "On keeping a working log")
    page.fill("#body", DRAFT_BODY)
    page.fill("#tags", "memory, notes")
    # Drop focus so no field is left wearing an accent focus ring. Playwright's
    # fill() focuses each field in turn, and the title also carries autofocus.
    page.evaluate("document.activeElement?.blur()")
    focused = page.evaluate("document.activeElement?.tagName")
    if focused != "BODY":
        raise SystemExit(f"editor: expected focus on <body> after blur, got {focused}")

    # The ring fades out over --duration-quiet, so blurring is not enough: wait
    # for the transition to finish or the shot catches it mid-fade.
    page.wait_for_function(
        "getComputedStyle(document.querySelector('#title')).boxShadow === 'none'"
    )


# (filename, path, description, prepare)
SHOTS = [
    ("home.png", "/", "post listing", None),
    ("post.png", "/posts/a-test-that-passed-for-the-wrong-reason/", "reading a post", None),
    ("editor.png", "/posts/new/", "the Markdown editor", fill_editor),
    ("profile.png", "/u/atlas/", "an author profile", None),
]


def log_in(page) -> None:
    """Sign in as the seeded user, so the editor and drafts are reachable."""
    page.goto(f"{BASE}/login/", wait_until="networkidle")
    page.fill("#username", USER)
    page.fill("#password", PASSWORD)
    # Scoped to the form that owns the username field: the header's theme switch
    # is also a form with a submit button, and it comes first in the DOM.
    page.locator("form:has(#username) button[type=submit]").click()
    page.wait_for_load_state("networkidle")
    if page.locator('[popovertarget="account-menu"]').count() == 0:
        raise SystemExit("login failed — is the database seeded?")


def main() -> int:
    """Capture every shot in SHOTS into the screenshots/ directory."""
    OUT.mkdir(exist_ok=True)

    with sync_playwright() as p:
        # channel="chrome" uses the installed browser instead of a download.
        browser = p.chromium.launch(channel="chrome")
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = context.new_page()

        log_in(page)

        context.add_cookies([{"name": "theme", "value": THEME, "url": BASE}])

        for name, path, description, prepare in SHOTS:
            page.goto(f"{BASE}{path}", wait_until="networkidle")

            # The flash message from logging in would otherwise sit in the first
            # shot; a second navigation clears it.
            page.goto(f"{BASE}{path}", wait_until="networkidle")

            resolved = page.get_attribute("html", "data-theme")
            if resolved != THEME:
                raise SystemExit(f"{name}: expected theme {THEME!r}, got {resolved!r}")

            if prepare:
                prepare(page)

            # Typing into a field scrolls it into view, so every shot is pinned
            # back to the top of the page before it is taken.
            page.evaluate("window.scrollTo(0, 0)")
            offset = page.evaluate("window.scrollY")
            if offset:
                raise SystemExit(f"{name}: page is scrolled to {offset}, expected the top")

            page.screenshot(path=str(OUT / name))
            size = (OUT / name).stat().st_size // 1024
            print(f"  {name:<12} {size:>4} KB   {description}")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
