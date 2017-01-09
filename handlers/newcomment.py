from models import Post, Comment
from handler import Handler

class NewComment(Handler):
    """Handles creation of new comment"""

    @Handler.post_exist
    @Handler.user_logged_in
    def get(self, post_id):
        self.render("comment-form.html")

    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        content = self.request.get("content")
        if content:
            post = Post.get_by_id(int(post_id))
            comment = Comment(user=self.user, content=content, post=post)
            comment.put()
            self.redirect("/blog/%s" % post_id)
        else:
            error = "You didn't leave any comment."
            self.render("comment-form.html", error=error)