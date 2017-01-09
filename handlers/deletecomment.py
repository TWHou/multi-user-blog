from models import Comment
from handler import Handler

class DeleteComment(Handler):
    """Handles deletion of comments"""

    @Handler.comment_exist
    @Handler.user_logged_in
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        if self.user.key().id() == comment.user.key().id():
            self.render("delete.html")
        else:
            error = "You can only delete your own comment"
            self.redirect("/blog/%s" %
                          comment.post.key().id(), error=error)

    @Handler.comment_exist
    @Handler.user_logged_in
    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        if self.user.key().id() == comment.user.key().id():
            post_id = comment.post.key().id()
            comment.delete()
            self.redirect("/blog/%s" % post_id)
        else:
            error = "You can only delete your own comment"
            self.redirect("/blog/%s" %
                          comment.post.key().id(), error=error)