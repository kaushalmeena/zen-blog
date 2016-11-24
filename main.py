#main.py
"""Python script for myapp-blog website."""

#python modules
import webapp2

from handlers.deletecomment import DeleteCommentHandler
from handlers.deletepost import DeletePostHandler
from handlers.dislike import DislikeHandler
from handlers.editcomment import EditCommentHandler
from handlers.editpost import EditPostHandler
from handlers.home import MainHandler
from handlers.like import LikeHandler
from handlers.mypost import MyPostHandler
from handlers.newpost import NewPostHandler
from handlers.permalink import PermalinkHandler
from handlers.setting import SettingHandler
from handlers.signin import SignInHandler
from handlers.signout import SignOutHandler
from handlers.signup import SignUpHandler
from handlers.welcome import WelcomeHandler


app = webapp2.WSGIApplication([('/',MainHandler),
                               ('/signup', SignUpHandler),
                               ('/signin', SignInHandler),
                               ('/signout', SignOutHandler),
                               ('/welcome', WelcomeHandler),
                               ('/newpost', NewPostHandler),
                               ('/post/([0-9]+)/edit', EditPostHandler),
                               ('/comment/([0-9]+)/edit', EditCommentHandler),
                               ('/mypost', MyPostHandler),
                               ('/setting', SettingHandler),
                               ('/post/([0-9]+)', PermalinkHandler),
                               ('/post/([0-9]+)/like', LikeHandler),
                               ('/post/([0-9]+)/dislike', DislikeHandler),
                               ('/post/([0-9]+)/delete', DeletePostHandler),
                               ('/comment/([0-9]+)/delete', DeleteCommentHandler)], debug = True)
