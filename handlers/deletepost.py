from models import Post
from handler import Handler

class DeletePost(Handler):
    """Handles deletion of blog post"""

    @Handler.user_owns_post(True, "You cannot delete other user's post")
    @Handler.post_exist
    @Handler.user_logged_in
    def get(self, post_id):
        self.render("delete.html")

    @Handler.user_owns_post(True, "You cannot delete other user's post")
    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        post.delete()
        self.redirect("/blog")