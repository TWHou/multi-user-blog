from models import Comment
from handler import Handler

class EditComment(Handler):
    """Handles editing of comments"""

    @Handler.user_owns_comment("you can only edit your own comment")
    @Handler.comment_exist
    @Handler.user_logged_in
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        self.render("comment-form.html", content=comment.content)

    @Handler.user_owns_comment("you can only edit your own comment")
    @Handler.comment_exist
    @Handler.user_logged_in
    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        content = self.request.get("content")
        if content:
            comment.content = content
            comment.put()
            self.redirect("/blog/%s" % comment.post.key().id())
        else:
            error = "Uhmmm, did you forget to put some content back?"
            self.render("comment-form.html", error=error)
