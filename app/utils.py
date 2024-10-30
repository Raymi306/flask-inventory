from functools import wraps

from flask import abort, g


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401)
        return view(**kwargs)

    return wrapped_view


def snake_to_camel(string):
    return string.title().replace("_", "")
