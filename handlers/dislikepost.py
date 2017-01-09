import json

from models import Post
from handler import Handler

class DislikePost(Handler):
    """Toggles whether user is in the dislikes list"""

    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if self.user.key().id() != post.user.key().id():
            if self.user.key() in post.likes:
                post.likes.remove(self.user.key())
            if self.user.key() not in post.dislikes:
                post.dislikes.append(self.user.key())
            else:
                post.dislikes.remove(self.user.key())
            post.put()
            likes = post.get_likes()
            dislikes = post.get_dislikes()
            self.write(json.dumps(
                ({'like_count': likes, 'dislike_count': dislikes})))
        else:
            self.error(404)
            return