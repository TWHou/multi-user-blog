from handler import Handler

class Logout(Handler):
    """Handles Logout"""

    def get(self):
        self.logout()
        self.redirect('/login')