from models import Post
from handler import Handler

class NewPost(Handler):
    """Handle new blog post creation"""

    @Handler.user_logged_in
    def get(self):
        self.render("post-form.html")

    @Handler.user_logged_in
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            p = Post(user=self.user, subject=subject, content=content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "we need both a subject and some content!"
            self.render("post-form.html", subject=subject,
                        content=content, error=error)