# Blog

A simple multi user blog where users can sign in and post blog posts as well as 'Like' and 'Comment' on other posts made on the blog.

## Requirements

To install and run this project you need:

- [Python 3.7+](https://www.python.org/downloads/ "Python 3.7+")
- [Poetry](https://python-poetry.org/ "Poetry")
- [git](https://git-scm.com/downloads "git") (only to clone this repository)

## Installation

To set up everything in your local machine, you need to follow these steps:

1. Clone this repo and then change directory to the `myapp-blog` folder:

```bash
$ git clone https://github.com/kaushalmeena1996/myapp-blog.git
$ cd myapp-blog
```

2. Install project dependencies using poetry:

```bash
$ poetry install
```

## Usage

To run the project simply run:

```bash
$ poetry run python wsgi.py
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Deployment

To push to Heroku you need to install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) afterwards, you can run these commands:

```bash
$ heroku create
$ heroku config:set SECRET_KEY='<YOUR-SECRET-KEY-HERE>'
$ git push heroku master
$ heroku open
```

or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
