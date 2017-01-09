from models import Post
from handler import Handler

class DeletePost(Handler):
    """Handles deletion of blog post"""

    @Handler.post_exist
    @Handler.user_logged_in
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if self.user.key().id() == post.user.key().id():
            self.render("delete.html")
        else:
            error = "You cannot delete other user's post"
            self.redirect("/blog/%s" % post_id, error=error)

    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if self.user.key().id() == post.user.key().id():
            post.delete()
            self.redirect("/blog")
        else:
            error = "You cannot delete other user's post"
            self.redirect("/blog/%s" % post_id, error)