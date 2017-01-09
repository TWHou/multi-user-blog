import re

from models import User
from handler import Handler

# validations for signup form
def verify_username(name):
    return name and re.compile(r"^[a-zA-Z0-9_-]{3,20}$").match(name)


def verify_password(pw):
    return pw and re.compile(r"^.{3,20}$").match(pw)


def verify_email(email):
    return not email or re.compile(r"^[\S]+@[\S]+.[\S]+$").match(email)


class SignUp(Handler):
    """Handles sign up form for new user"""

    def get(self):
        self.render("signup.html")

    def post(self):
        input_username = self.request.get('username')
        input_password = self.request.get('password')
        input_verify = self.request.get('verify')
        input_email = self.request.get('email')

        username = verify_username(input_username)
        password = verify_password(input_password)
        verify = input_password == input_verify
        email = verify_email(input_email)

        if not username or not password or not verify or not email:
            user_error = "" if username else "Please enter a valid username."
            pass_error = "" if password else "Please enter a valid password."
            verify_error = "" if verify else "The passwords must match."
            email_error = "" if email else "Please enter a valid email."
            self.render("signup.html",
                        username=input_username,
                        email=input_email,
                        user_error=user_error,
                        pass_error=pass_error,
                        verify_error=verify_error,
                        email_error=email_error)
        else:
            user = User.by_name(input_username)
            if user:
                # user already exist
                self.render("signup.html",
                            username=input_username,
                            email=input_email,
                            user_error="This username is taken.")
            else:
                user = User.register(
                    input_username, input_password, input_email)
                user.put()
                self.login(user)
                self.redirect('/blog')