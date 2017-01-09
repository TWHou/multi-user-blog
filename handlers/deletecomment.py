from models import Comment
from handler import Handler

class DeleteComment(Handler):
    """Handles deletion of comments"""

    @Handler.user_owns_comment("You can only delete your own comment")
    @Handler.comment_exist
    @Handler.user_logged_in
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        self.render("delete.html")

    @Handler.user_owns_comment("You can only delete your own comment")
    @Handler.comment_exist
    @Handler.user_logged_in
    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        post_id = comment.post.key().id()
        comment.delete()
        self.redirect("/blog/%s" % post_id)
