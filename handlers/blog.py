from models import Post
from handler import Handler

class Blog(Handler):
    """Display all blog entries"""

    def get(self):
        posts = Post.all().order('-created')
        self.render("blog.html", posts=posts)