import os
import jinja2
import webapp2
import re
import hashlib
import hmac
import string
import random
import json
import logging

from google.appengine.ext import db

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
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


# validations for signup form
def verify_username(name):
    return name and re.compile(r"^[a-zA-Z0-9_-]{3,20}$").match(name)


def verify_password(pw):
    return pw and re.compile(r"^.{3,20}$").match(pw)


def verify_email(email):
    return not email or re.compile(r"^[\S]+@[\S]+.[\S]+$").match(email)


# functions for hashing password
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def hash_pw(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (salt, h)


def check_pw(name, pw, h):
    salt = h.split("|")[0]
    return h == hash_pw(name, pw, salt)


# User database
def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    """Model for user database recording name, hashed password and email"""
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        return cls.all().filter('name =', name).get()

    @classmethod
    def register(cls, name, pw, email=None):
        """Saves new user into database"""
        pw_hash = hash_pw(name, pw)
        return cls(parent=users_key(),
                   name=name,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, name, pw):
        """Checks password to log in user"""
        user = cls.by_name(name)
        if user and check_pw(name, pw, user.pw_hash):
            return user


# blog database
def blog_key(name='default'):
    return db.Key.from_path('blog', name)


class Post(db.Model):
    """Model for blog posts.

    Attributes:
        user: Reference to the User who made the post.
        subject: Title of blog post.
        content: Content of blog post.
        likes: List of users liked the post, referenced by key
        dislikes: List of users disliked the post, referenced by key
        created: Creation datetime auto added by database
        last_modified: Datetime of last modification auto updated by database
    """
    user = db.ReferenceProperty(User, collection_name='posts')
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    likes = db.ListProperty(db.Key)
    dislikes = db.ListProperty(db.Key)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        """Renders the blog post using post.html as template"""
        self._render_text = self.content.replace('\n', '<br>')
        return JINJA_ENV.get_template("post.html").render(post=self)

    def get_likes(self):
        return len(self.likes)

    def get_dislikes(self):
        return len(self.dislikes)


class Comment(db.Model):
    """Model for blog comments.

    Attributes:
        post: Reference to the Post this comment belongs to
        user: Reference to the User who made the comment.
        content: Content of comment.
        created: Creation datetime auto added by database
        last_modified: Datetime of last modification auto updated by database
    """
    post = db.ReferenceProperty(
        Post, collection_name='comments', required=True)
    user = db.ReferenceProperty(
        User, collection_name='comments', required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self):
        """Converts \n to <br>"""
        return self.content.replace('\n', '<br>')


class Handler(webapp2.RequestHandler):
    """Base Handler for all other handlers"""

    def write(self, *a, **kw):
        """Shortcut for response write function"""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Prepare jinja template output"""
        t = JINJA_ENV.get_template(template)
        params['user'] = self.user
        return t.render(params)

    def render(self, template, **kw):
        """Writes rendered jinja template"""
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, val):
        cookie = make_secure(val)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (name, cookie))

    def read_cookie(self, name):
        cookie = self.request.cookies.get(name)
        return cookie and check_secure(cookie)

    def login(self, user):
        """Set cookie to identify user"""
        self.set_cookie('user_id', str(user.key().id()))

    def logout(self):
        """Destroy user_id cookie"""
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class MainPage(Handler):

    def get(self):
        self.write("Udacity Project 2")


class SignUp(Handler):
    """Handles sign up form for new user"""

    def get(self):
        self.render("signup.html")

    def post(self):
        input_username = self.request.get('username')
        input_password = self.request.get('password')
        input_verify = self.request.get('verify')
        input_email = self.request.get('email')

        username = verify_username(input_username)
        password = verify_password(input_password)
        verify = input_password == input_verify
        email = verify_email(input_email)

        if not username or not password or not verify or not email:
            user_error = "" if username else "Please enter a valid username."
            pass_error = "" if password else "Please enter a valid password."
            verify_error = "" if verify else "The passwords must match."
            email_error = "" if email else "Please enter a valid email."
            self.render("signup.html",
                        username=input_username,
                        email=input_email,
                        user_error=user_error,
                        pass_error=pass_error,
                        verify_error=verify_error,
                        email_error=email_error)
        else:
            user = User.by_name(input_username)
            if user:
                # user already exist
                self.render("signup.html",
                            username=input_username,
                            email=input_email,
                            user_error="This username is taken.")
            else:
                user = User.register(
                    input_username, input_password, input_email)
                user.put()
                self.login(user)
                self.redirect('/blog')


class Login(Handler):
    """Handles login for users"""

    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog')
        else:
            self.render('login.html', error="Invalid login")


class Logout(Handler):
    """Handles Logout"""

    def get(self):
        self.logout()
        self.redirect('/login')


class BlogHandler(Handler):
    """Display all blog entries"""

    def get(self):
        posts = Post.all().order('-created')
        self.render("blog.html", posts=posts)


class NewPost(Handler):
    """Handle new blog post creation"""

    def get(self):
        if self.user:
            self.render("post-form.html")
        else:
            error = "you must log in before posting"
            self.render("error.html", error=error)

    def post(self):
        if self.user:
            subject = self.request.get("subject")
            content = self.request.get("content")
            if subject and content:
                p = Post(user=self.user, subject=subject, content=content)
                p.put()
                self.redirect("/blog/%s" % str(p.key().id()))
            else:
                error = "we need both a subject and some content!"
                self.render("post-form.html", subject=subject,
                            content=content, error=error)
        else:
            error = "you must log in before posting"
            self.render("error.html", error=error)


class PostHandler(Handler):
    """Display single blog entry with votes and comments"""

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        comments = post.comments.run(batch_size=1000)
        self.render("permalink.html", post=post, comments=comments)


class LikePost(Handler):
    """Toggles whether user is in the likes list"""

    def post(self):
        if self.user:
            post_id = self.request.get('postID')
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() != post.user.key().id():
                if self.user.key() in post.dislikes:
                    post.dislikes.remove(self.user.key())
                if self.user.key() not in post.likes:
                    post.likes.append(self.user.key())
                else:
                    post.likes.remove(self.user.key())
                post.put()
                likes = post.get_likes()
                dislikes = post.get_dislikes()
                self.write(json.dumps(
                    ({'like_count': likes, 'dislike_count': dislikes})))


class DislikePost(Handler):
    """Toggles whether user is in the dislikes list"""

    def post(self):
        if self.user:
            post_id = self.request.get('postID')
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() != post.user.key().id():
                if self.user.key() in post.likes:
                    post.likes.remove(self.user.key())
                if self.user.key() not in post.dislikes:
                    post.dislikes.append(self.user.key())
                else:
                    post.dislikes.remove(self.user.key())
                post.put()
                likes = post.get_likes()
                dislikes = post.get_dislikes()
                self.write(json.dumps(
                    ({'like_count': likes, 'dislike_count': dislikes})))


class EditPost(Handler):
    """Handles blog post edits"""

    def get(self, post_id):
        if self.user:
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() == post.user.key().id():
                self.render("post-form.html", subject=post.subject,
                            content=post.content)
            else:
                error = "You can only edit your own post"
                self.redirect("/blog/%s" % post_id, error=error)
        else:
            error = "you must log in before editing"
            self.render("error.html", error=error)

    def post(self, post_id):
        if self.user:
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() == post.user.key().id():
                subject = self.request.get("subject")
                content = self.request.get("content")
                post = Post.get_by_id(int(post_id))
                if subject and content:
                    post.content = content
                    post.subject = subject
                    post.put()
                    self.redirect("/blog/%s" % post_id)
                else:
                    error = "we need both a subject and some content!"
                    self.render("post-form.html", subject=subject,
                                content=content, error=error)
            else:
                error = "You can only edit your own post"
                self.redirect("/blog/%s" % post_id, error=error)
        else:
            error = "you must log in before editing"
            self.render("error.html", error=error)


class DeletePost(Handler):
    """Handles deletion of blog post"""

    def get(self, post_id):
        if self.user:
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() == post.user.key().id():
                self.render("delete.html")
            else:
                error = "You cannot delete other user's post"
                self.redirect("/blog/%s" % post_id, error=error)
        else:
            error = "you must log in before deleting"
            self.render("error.html", error=error)

    def post(self, post_id):
        if self.user:
            post = Post.get_by_id(int(post_id))
            if self.user.key().id() == post.user.key().id():
                post.delete()
                self.redirect("/blog")
            else:
                error = "You cannot delete other user's post"
                self.redirect("/blog/%s" % post_id, error)
        else:
            error = "you must log in before deleting"
            self.render("error.html", error=error)


class NewComment(Handler):
    """Handles creation of new comment"""

    def get(self, post_id):
        if self.user:
            self.render("comment-form.html")
        else:
            error = "you must log in before leaving a comment"
            self.render("error.html", error=error)

    def post(self, post_id):
        if self.user:
            content = self.request.get("content")
            if content:
                post = Post.get_by_id(int(post_id))
                comment = Comment(user=self.user, content=content, post=post)
                comment.put()
                self.redirect("/blog/%s" % post_id)
            else:
                error = "You didn't leave any comment."
                self.render("comment-form.html", error=error)
        else:
            error = "you must log in before leaving a comment"
            self.render("error.html", error=error)


class EditComment(Handler):
    """Handles editing of comments"""

    def get(self, comment_id):
        if self.user:
            comment = Comment.get_by_id(int(comment_id))
            if self.user.key().id() == comment.user.key().id():
                self.render("comment-form.html", content=comment.content)
            else:
                error = "you can only edit your own comment"
                self.redirect("/blog/%s" %
                              comment.post.key().id(), error=error)
        else:
            error = "you must log in before editing"
            self.render("error.html", error=error)

    def post(self, comment_id):
        if self.user:
            comment = Comment.get_by_id(int(comment_id))
            if self.user.key().id() == comment.user.key().id():
                content = self.request.get("content")
                if content:
                    comment.content = content
                    comment.put()
                    self.redirect("/blog/%s" % comment.post.key().id())
                else:
                    error = "Uhmmm, did you forget to put some content back?"
                    self.render("comment-form.html", error=error)
            else:
                error = "you can only edit your own comment"
                self.redirect("/blog/%s" %
                              comment.post.key().id(), error=error)
        else:
            error = "you must log in before editing"
            self.render("error.html", error=error)


class DeleteComment(Handler):
    """Handles deletion of comments"""

    def get(self, comment_id):
        if self.user:
            comment = Comment.get_by_id(int(comment_id))
            if self.user.key().id() == comment.user.key().id():
                self.render("delete.html")
            else:
                error = "You can only delete your own comment"
                self.redirect("/blog/%s" %
                              comment.post.key().id(), error=error)
        else:
            error = "you must log in before deleting"
            self.render("error.html", error=error)

    def post(self, comment_id):
        if self.user:
            comment = Comment.get_by_id(int(comment_id))
            if self.user.key().id() == comment.user.key().id():
                post_id = comment.post.key().id()
                comment.delete()
                self.redirect("/blog/%s" % post_id)
            else:
                error = "You can only delete your own comment"
                self.redirect("/blog/%s" %
                              comment.post.key().id(), error=error)
        else:
            error = "you must log in before deleting"
            self.render("error.html", error=error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignUp),
    ('/login', Login),
    ('/logout', Logout),
    ('/blog/?', BlogHandler),
    ('/blog/new', NewPost),
    ('/blog/([0-9]+)', PostHandler),
    ('/blog/like', LikePost),
    ('/blog/dislike', DislikePost),
    ('/blog/edit/([0-9]+)', EditPost),
    ('/blog/delete/([0-9]+)', DeletePost),
    ('/comment/new/([0-9]+)', NewComment),
    ('/comment/edit/([0-9]+)', EditComment),
    ('/comment/delete/([0-9]+)', DeleteComment),
], debug=True)
