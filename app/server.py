# main.py
"""Python script for myapp-blog website."""

# python modules
import webapp2

from paste import httpserver

from handlers.delete_comment import DeleteCommentHandler
from handlers.delete_post import DeletePostHandler
from handlers.dislike import DislikeHandler
from handlers.edit_comment import EditCommentHandler
from handlers.edit_post import EditPostHandler
from handlers.home import HomeHandler
from handlers.like import LikeHandler
from handlers.my_post import MyPostHandler
from handlers.new_post import NewPostHandler
from handlers.permalink import PermalinkHandler
from handlers.setting import SettingHandler
from handlers.sign_in import SignInHandler
from handlers.sign_out import SignOutHandler
from handlers.sign_up import SignUpHandler
from handlers.welcome import WelcomeHandler


HANDLER_LIST = [
    ('/', HomeHandler),
    ('/sign-up', SignUpHandler),
    ('/sign-in', SignInHandler),
    ('/sign-out', SignOutHandler),
    ('/welcome', WelcomeHandler),
    ('/new-post', NewPostHandler),
    ('/post/([0-9]+)/edit', EditPostHandler),
    ('/comment/([0-9]+)/edit', EditCommentHandler),
    ('/my-post', MyPostHandler),
    ('/setting', SettingHandler),
    ('/post/([0-9]+)', PermalinkHandler),
    ('/post/([0-9]+)/like', LikeHandler),
    ('/post/([0-9]+)/dislike', DislikeHandler),
    ('/post/([0-9]+)/delete', DeletePostHandler),
    ('/comment/([0-9]+)/delete', DeleteCommentHandler)
]


def start():
    """Start server"""
    app = webapp2.WSGIApplication(HANDLER_LIST, debug=True)
    httpserver.serve(app)


if __name__ == "__main__":
    app = webapp2.WSGIApplication(HANDLER_LIST, debug=True)
    httpserver.serve(app)
