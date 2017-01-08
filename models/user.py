import string
import random
import hashlib

from google.appengine.ext import db

# functions for hashing password
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def hash_pw(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (salt, h)


def check_pw(name, pw, h):
    salt = h.split("|")[0]
    return h == hash_pw(name, pw, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    """Model for user database recording name, hashed password and email"""
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        return cls.all().filter('name =', name).get()

    @classmethod
    def register(cls, name, pw, email=None):
        """Saves new user into database"""
        pw_hash = hash_pw(name, pw)
        return cls(parent=users_key(),
                   name=name,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, name, pw):
        """Checks password to log in user"""
        user = cls.by_name(name)
        if user and check_pw(name, pw, user.pw_hash):
            return user