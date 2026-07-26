"""Cache-busting version stamps for static files.

There is no build step, so static filenames never change and a browser cannot
tell a new stylesheet from the one it already has. Without help the only safe
policy is "revalidate every time", which is what Flask does by default: every
page load spends a conditional request per asset just to be told 304.

So every ``url_for('static', ...)`` gains a ``v=`` stamp derived from the file's
contents. The URL changes exactly when the file does, which makes it safe to
serve the asset with a long, immutable cache lifetime in production.

The digest is only for cache identity, never for security, so a short
non-cryptographic hash is the right tool. Results are memoised against the
file's mtime and size, so an edit invalidates the stamp but a request does not
re-read the file.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from flask import Flask

_STAMPS: dict[tuple[str, float, int], str] = {}


def stamp(path: Path) -> str | None:
    """Return a short content digest for ``path``, or ``None`` if unreadable."""
    try:
        stat = path.stat()
    except OSError:
        return None

    key = (str(path), stat.st_mtime, stat.st_size)
    cached = _STAMPS.get(key)
    if cached is None:
        digest = hashlib.blake2b(path.read_bytes(), digest_size=5).hexdigest()
        cached = _STAMPS[key] = digest
    return cached


def register(app: Flask) -> None:
    """Append a content stamp to every generated static URL."""
    static_root = Path(app.static_folder) if app.static_folder else None

    @app.url_defaults
    def add_stamp(endpoint: str, values: dict) -> None:
        if static_root is None or endpoint != "static":
            return
        filename = values.get("filename")
        if not filename:
            return
        digest = stamp(static_root / filename)
        if digest:
            values["v"] = digest
