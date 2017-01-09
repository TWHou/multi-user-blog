from models import User
from handler import Handler

class Login(Handler):
    """Handles login for users"""

    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect('/blog')
        else:
            self.render('login.html', error="Invalid login")