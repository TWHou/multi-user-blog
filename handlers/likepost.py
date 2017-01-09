import json

from models import Post
from handler import Handler

class LikePost(Handler):
    """Toggles whether user is in the likes list"""

    @Handler.user_owns_post(False, "You cannot like your own post")
    @Handler.post_exist
    @Handler.user_logged_in
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if self.user.key() in post.dislikes:
            post.dislikes.remove(self.user.key())
        if self.user.key() not in post.likes:
            post.likes.append(self.user.key())
        else:
            post.likes.remove(self.user.key())
        post.put()
        likes = post.get_likes()
        dislikes = post.get_dislikes()
        self.write(json.dumps(
            ({'like_count': likes, 'dislike_count': dislikes})))