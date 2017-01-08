import hashlib
import random
import string
import jinja2
import os

from google.appengine.ext import db

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

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
