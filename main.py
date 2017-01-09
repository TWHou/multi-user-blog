import webapp2

from models import *
from handlers import *


app = webapp2.WSGIApplication([
    ('/signup', SignUp),
    ('/login', Login),
    ('/logout', Logout),
    ('/blog/?', Blog),
    ('/blog/new', NewPost),
    ('/blog/([0-9]+)', Post),
    ('/blog/like', LikePost),
    ('/blog/dislike', DislikePost),
    ('/blog/edit/([0-9]+)', EditPost),
    ('/blog/delete/([0-9]+)', DeletePost),
    ('/comment/new/([0-9]+)', NewComment),
    ('/comment/edit/([0-9]+)', EditComment),
    ('/comment/delete/([0-9]+)', DeleteComment),
], debug=True)
