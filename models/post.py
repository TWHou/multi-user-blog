import jinja2
import os

from os.path import join, dirname, abspath
from user import User
from google.appengine.ext import db

TEMPLATE_DIR = join(dirname(dirname(abspath(__file__))), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


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