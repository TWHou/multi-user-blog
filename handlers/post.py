from models import Post as PostModel
from handler import Handler

class Post(Handler):
    """Display single blog entry with votes and comments"""

    def get(self, post_id):
        post = PostModel.get_by_id(int(post_id))
        if not post:
            self.error(404)
            return
        comments = post.comments.run(batch_size=1000)
        self.render("permalink.html", post=post, comments=comments)