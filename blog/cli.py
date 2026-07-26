"""Custom ``flask`` CLI commands."""

from __future__ import annotations

import click
from flask import Flask
from sqlalchemy import select

from blog.extensions import db
from blog.models import Comment, Post, Tag, User

DEMO_USERS = [
    ("ada", "Counts steps, writes notes, distrusts magic."),
    ("grace", "Compilers, submarines, and plain English."),
    ("linus", "It works on my machine, which is the machine."),
]

DEMO_POSTS = [
    (
        "ada",
        "Notes on the Analytical Engine",
        "engine, notes",
        "The Analytical Engine has no pretensions whatever to *originate* anything.\n\n"
        "It can do whatever we know how to order it to perform. That is the whole of it,\n"
        "and also the interesting part: the ordering is the work.\n\n"
        "## What follows from that\n\n"
        "1. A machine is only as careful as its instructions.\n"
        "2. Instructions are writing, so they can be edited.\n"
        "3. Editing is where the thinking happens.\n",
    ),
    (
        "grace",
        "Write it so a human can read it",
        "compilers, writing",
        "It is easier to apologise than to get permission, but it is easier still to\n"
        "write the thing plainly so nobody has to ask.\n\n"
        "> A ship in port is safe, but that is not what ships are built for.\n\n"
        "Code is the same. It exists to be changed, and it can only be changed by\n"
        "someone who can read it.\n\n"
        "```python\ndef clear(intent):\n    return intent.strip().lower()\n```\n",
    ),
    (
        "linus",
        "On keeping the tree bisectable",
        "git, process",
        "Every commit should be a state the project could have shipped from. Not\n"
        "*would* have — *could* have.\n\n"
        "If a commit does not build, it is not a commit, it is a save file. The\n"
        "difference matters the day you need `git bisect` to tell you the truth.\n",
    ),
    (
        "ada",
        "The difference between calculating and knowing",
        "engine",
        "A calculation is a claim about numbers. Knowing is a claim about the world.\n\n"
        "The engine can make the first kind of claim very quickly, and it will never\n"
        "make the second. That gap is not a defect. It is the job description for\n"
        "whoever is holding the paper.\n",
    ),
]

ENGINE_POST = "Notes on the Analytical Engine"
READABLE_POST = "Write it so a human can read it"

DEMO_COMMENTS = [
    ("grace", ENGINE_POST, "The ordering is the work — that's the whole trade."),
    ("linus", ENGINE_POST, "Point 2 is the one people skip."),
    ("ada", READABLE_POST, "Plain writing is a form of respect for the reader."),
]


def register(app: Flask) -> None:
    """Attach the custom commands to ``app``."""
    app.cli.add_command(seed)
    app.cli.add_command(reset)


@click.command("seed")
@click.option(
    "--password",
    default="password123",
    show_default=True,
    help="Password given to every demo account.",
)
def seed(password: str) -> None:
    """Populate the database with demo users, posts and comments."""
    if db.session.scalar(select(User.id).limit(1)):
        click.echo("Database already has users; nothing to do.")
        return

    users: dict[str, User] = {}
    for username, bio in DEMO_USERS:
        user = User(username=username, bio=bio)
        user.set_password(password)
        db.session.add(user)
        users[username] = user

    posts: dict[str, Post] = {}
    for username, title, tags, body in DEMO_POSTS:
        post = Post(author=users[username], title=title, body=body)
        post.assign_slug(db.session)
        post.tags = {Tag.get_or_create(db.session, name.strip()) for name in tags.split(",")}
        db.session.add(post)
        posts[title] = post

    for username, title, body in DEMO_COMMENTS:
        db.session.add(Comment(author=users[username], post=posts[title], body=body))

    # A few likes, saves and follows so the counters are not all zero.
    users["grace"].liked_posts.add(posts[ENGINE_POST])
    users["linus"].liked_posts.add(posts[ENGINE_POST])
    users["ada"].liked_posts.add(posts[READABLE_POST])
    users["ada"].saved_posts.add(posts["On keeping the tree bisectable"])
    users["grace"].following.add(users["ada"])
    users["linus"].following.add(users["ada"])
    users["ada"].following.add(users["grace"])

    db.session.commit()
    click.echo(f"Seeded {len(DEMO_USERS)} users and {len(DEMO_POSTS)} posts.")
    click.echo(
        f"Log in as any of {', '.join(name for name, _ in DEMO_USERS)} with password {password!r}."
    )


@click.command("reset")
@click.confirmation_option(prompt="Drop every table and recreate the schema?")
def reset() -> None:
    """Drop and recreate all tables. Development convenience only."""
    db.drop_all()
    db.create_all()
    click.echo("Schema recreated. Run 'flask seed' to add demo content.")
