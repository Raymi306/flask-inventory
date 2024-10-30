from http import HTTPStatus

from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, abort, g, request, session

from app.models.user import (
    get_user_by_id,
    get_user_by_name,
    update_user_last_login,
    update_user_password_hash,
)
from app.utils import PASSWORD_HASHER

blueprint = Blueprint("auth", __name__, url_prefix="/auth")

MIN_PASSWORD_LENGTH = 12


@blueprint.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = get_user_by_name(username)
    if not user:
        abort(HTTPStatus.UNAUTHORIZED)

    password_hash = user["password_hash"]
    try:
        PASSWORD_HASHER.verify(password_hash, password)
    except VerifyMismatchError:
        abort(HTTPStatus.UNAUTHORIZED)
    if PASSWORD_HASHER.check_needs_rehash(password_hash):
        update_user_password_hash(user["id"], PASSWORD_HASHER.hash(password))
    session["user_id"] = user["id"]
    session["last_login"] = user["last_login"]
    update_user_last_login(user["id"])
    return ("", HTTPStatus.NO_CONTENT)


@blueprint.route("/logout", methods=("POST", "DELETE"))
def logout():
    session.clear()
    return ("", HTTPStatus.NO_CONTENT)


@blueprint.post("/password")
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        abort(HTTPStatus.UNAUTHORIZED)
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    if old_password == new_password:
        return ("Old and new password can not be the same.", HTTPStatus.BAD_REQUEST)
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return (
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.",
            HTTPStatus.BAD_REQUEST,
        )
    user = get_user_by_id(user_id)
    try:
        PASSWORD_HASHER.verify(user["password_hash"], old_password)
    except VerifyMismatchError:
        abort(HTTPStatus.UNAUTHORIZED)
    update_user_password_hash(user_id, PASSWORD_HASHER.hash(new_password))
    return ("", HTTPStatus.NO_CONTENT)


@blueprint.before_app_request
def load_current_user():
    if user_id := session.get("user_id"):
        g.user = user_id
    else:
        g.user = None
