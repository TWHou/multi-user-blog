import jinja2
import webapp2
import hmac
import logging

from datetime import datetime, timedelta
from os.path import join, dirname, abspath
from models import *
from functools import wraps

TEMPLATE_DIR = join(dirname(dirname(abspath(__file__))), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


# functions for checking cookies
SECRET = 'secret'


def make_secure(val):
    return "%s|%s" % (val, hmac.new(SECRET, val).hexdigest())


def check_secure(s_val):
    val = s_val.split("|")[0]
    if s_val == make_secure(val):
        return val

class Handler(webapp2.RequestHandler):
    """Base Handler for all other handlers"""

    def write(self, *a, **kw):
        """Shortcut for response write function"""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Prepare jinja template output"""
        t = JINJA_ENV.get_template(template)
        params['user'] = self.user
        params['error'] = self.error
        return t.render(params)

    def render(self, template, **kw):
        """Writes rendered jinja template"""
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie = make_secure(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (name, cookie))

    def read_secure_cookie(self, name):
        cookie = self.request.cookies.get(name)
        return cookie and check_secure(cookie)

    def login(self, user):
        """Set cookie to identify user"""
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """Destroy user_id cookie"""
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.error = self.request.cookies.get('error')
        self.user = uid and User.by_id(int(uid))

    @staticmethod
    def user_logged_in(func):
        @wraps(func)
        def wrapper(self, *a):
            if self.user:
                return func(self, *a)
            else:
                self.redirect('/login')
        return wrapper

    @staticmethod
    def post_exist(func):
        @wraps(func)
        def wrapper(self, post_id=""):
            if not post_id:
                post_id = self.request.get('postID')
            post = Post.get_by_id(int(post_id))
            if post:
                return func(self, post_id)
            else:
                self.error(404)
                return
        return wrapper

    @staticmethod
    def comment_exist(func):
        @wraps(func)
        def wrapper(self, comment_id):
            comment = Comment.get_by_id(int(comment_id))
            if comment:
                return func(self, comment_id)
            else:
                self.error(404)
                return
        return wrapper

    @staticmethod
    def user_owns_post(boolean, error):
        def decorator(func):
            @wraps(func)
            def wrapper(self, post_id):
                post = Post.get_by_id(int(post_id))
                same_user = self.user.key().id() == post.user.key().id()
                allowed = same_user == boolean
                if allowed:
                    return func(self, post_id)
                else:
                    expire = datetime.now()+timedelta(seconds=5)
                    self.response.set_cookie('error', error, expires=expire, path="/")
                    self.redirect("/blog/%s" % post.key().id())
            return wrapper
        return decorator




