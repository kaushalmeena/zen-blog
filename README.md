<div align="center">

# Blog

**A multi-user blogging platform with sign-in, posts, likes, and comments.**

A simple multi-user blogging site where users can sign in, create blog posts,
and interact with others through likes and comments — deployed on Heroku.

[![License: MIT](https://img.shields.io/badge/License-MIT-3DA639?logo=opensourceinitiative&logoColor=white)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-latest-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/) [![Heroku](https://img.shields.io/badge/Heroku-deployed-430098?logo=heroku&logoColor=white)](https://heroku.com/)

</div>

---

## Features

- **User authentication** — sign in to create and manage your own posts.
- **Blog posts** — create, edit, and publish blog entries.
- **Likes and comments** — interact with other users' posts.
- **Heroku deployment** — one-click deploy with the Heroku button.

## Tech Stack

| Area          | Tools                                                                 |
| ------------- | --------------------------------------------------------------------- |
| **Framework** | [Django](https://www.djangoproject.com/) · [Python 3.10+](https://www.python.org/) |
| **Database**  | SQLite (default) / PostgreSQL (production)                             |
| **Tooling**   | [Poetry](https://python-poetry.org/)                                  |
| **Hosting**   | [Heroku](https://heroku.com/)                                         |

## Getting Started

These instructions will get you a copy of the project up and running on your
local machine for development purposes.

### Requirements

To install and run this project you need:

- [Python 3.10+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/)
- [git](https://git-scm.com/downloads) (only to clone this repository)

### Installation

To set up everything on your local machine, follow these steps:

1. Clone this repo and then change directory to the `myapp-blog` folder:

```bash
git clone https://github.com/kaushalmeena/myapp-blog.git
cd myapp-blog
```

2. Install project dependencies using Poetry:

```bash
poetry install
```

### Running

To run the project simply run:

```bash
poetry run python wsgi.py
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Deployment

To push to Heroku you need to install the
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Afterwards, you
can run these commands after setting up the project locally:

```bash
heroku login
heroku create
heroku config:set SECRET_KEY='<YOUR-SECRET-KEY-HERE>'
git push heroku master
heroku open
```

Or use the one-click deploy button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please
[open an issue](https://github.com/kaushalmeena/myapp-blog/issues/new/choose)
first to discuss it. For code changes, fork the repository, create a branch,
and open a pull request.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE)
file for details.
