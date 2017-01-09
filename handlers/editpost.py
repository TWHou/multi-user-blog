from models import Post
from handler import Handler

class EditPost(Handler):
    """Handles blog post edits"""

    @Handler.user_owns_post(True, "You can only edit your own post")
    @Handler.post_exist
    @Handler.user_logged_in
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render("post-form.html", subject=post.subject, content=post.content)

    @Handler.user_owns_post(True, "You can only edit your own post")
    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            post = Post.get_by_id(int(post_id))
            post.content = content
            post.subject = subject
            post.put()
            self.redirect("/blog/%s" % post_id)
        else:
            error = "we need both a subject and some content!"
            self.render("post-form.html", subject=subject, content=content, error=error)