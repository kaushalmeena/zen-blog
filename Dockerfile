# syntax=docker/dockerfile:1

# Multi-stage build. The first stage resolves dependencies with uv into a
# self-contained virtualenv; the runtime stage copies that venv and the app, so
# neither uv nor a build toolchain ships in the final image.

FROM ghcr.io/astral-sh/uv:0.11-python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies are installed before the source is copied so this layer stays
# cached until pyproject.toml or uv.lock actually change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY pyproject.toml uv.lock README.md ./
COPY blog ./blog
COPY migrations ./migrations

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    APP_CONFIG=production \
    FLASK_APP=blog

RUN useradd --create-home --uid 10001 blog

WORKDIR /app
COPY --from=builder --chown=blog:blog /app /app

# SQLite lives here; mount a volume over it to make data outlive the container.
RUN mkdir -p /app/instance && chown blog:blog /app/instance
VOLUME ["/app/instance"]

USER blog
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/robots.txt').read()"

# Apply migrations, then hand off to gunicorn using the app factory.
CMD ["sh", "-c", "flask db upgrade && exec gunicorn 'blog:create_app()' --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -"]
