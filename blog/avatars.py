"""Deterministic identicon avatars, generated as inline SVG.

Avoids file uploads entirely: the same username always produces the same
5x5 mirrored pattern, so avatars need no storage, no JavaScript and no
third-party service such as Gravatar.
"""

from __future__ import annotations

import hashlib

from markupsafe import Markup

GRID = 5
HALF = GRID // 2 + 1


def _digest(username: str) -> bytes:
    return hashlib.sha256(username.strip().lower().encode()).digest()


def identicon(username: str, size: int = 40) -> Markup:
    """Return an inline SVG identicon derived from ``username``."""
    digest = _digest(username)
    hue = digest[0] * 360 // 256
    fill = f"hsl({hue} 62% 45%)"

    cells = []
    for column in range(HALF):
        for row in range(GRID):
            if digest[column * GRID + row + 1] % 2:
                cells.append((column, row))
                mirrored = GRID - 1 - column
                if mirrored != column:
                    cells.append((mirrored, row))

    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for x, y in cells)
    return Markup(
        f'<svg class="avatar" viewBox="0 0 {GRID} {GRID}" width="{size}" height="{size}" '
        f'role="img" aria-label="{username} avatar" fill="{fill}">'
        f'<rect width="{GRID}" height="{GRID}" fill="hsl({hue} 62% 92%)"/>{rects}</svg>'
    )
