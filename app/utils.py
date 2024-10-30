from functools import wraps

from argon2 import PasswordHasher
from flask import abort, g

PASSWORD_HASHER = PasswordHasher()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401)
        return view(**kwargs)

    return wrapped_view
