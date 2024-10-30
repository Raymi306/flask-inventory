import re
from functools import wraps

from flask import abort, g


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401)
        return view(**kwargs)

    return wrapped_view


def camel_case_split(string):
    """https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python"""
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", string)
