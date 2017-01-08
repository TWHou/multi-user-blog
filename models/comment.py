from post import Post
from user import User
from google.appengine.ext import db


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