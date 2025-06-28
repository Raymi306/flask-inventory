from http import HTTPStatus

from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, abort, g, request, session
from pydantic import BaseModel

from app.constants import PASSWORD_HASHER
from app.models.user import (
    get_user_by_id,
    get_user_by_name,
    update_user_last_login,
    update_user_password,
)

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(BaseModel):
    username: str
    password: str


@blueprint.post("/login")
def login():
    form = LoginForm(**request.form)
    username = form.username
    password = form.password
    user = get_user_by_name(username)
    if not user:
        abort(HTTPStatus.UNAUTHORIZED)

    password_hash = user.password_hash
    try:
        PASSWORD_HASHER.verify(password_hash, password)
    except VerifyMismatchError:
        abort(HTTPStatus.UNAUTHORIZED)
    if PASSWORD_HASHER.check_needs_rehash(password_hash):
        update_user_password(user.id, password)
    session["user"] = {
        "id": user.id,
        "last_login": user.last_login,
        "username": user.username,
        "password_reset_required": user.password_reset_required,
    }
    update_user_last_login(user.id)
    return ("", HTTPStatus.NO_CONTENT)


@blueprint.route("/logout", methods=("POST", "DELETE"))
def logout():
    session.clear()
    return ("", HTTPStatus.NO_CONTENT)


class ChangePasswordForm(BaseModel):
    old_password: str
    new_password: str


@blueprint.post("/password")
def change_password():
    # login is still required but with a loosening on the password reset requirement
    if g.user is None:
        abort(HTTPStatus.UNAUTHORIZED)
    form = ChangePasswordForm(**request.form)
    old_password = form.old_password
    new_password = form.new_password
    if old_password == new_password:
        return ("Old and new password can not be the same.", HTTPStatus.BAD_REQUEST)
    user_id = g.user["id"]
    user = get_user_by_id(user_id)
    try:
        PASSWORD_HASHER.verify(user.password_hash, old_password)
    except VerifyMismatchError:
        abort(HTTPStatus.UNAUTHORIZED)
    try:
        update_user_password(user_id, new_password)
    except ValueError as err:
        return (
            str(err),
            HTTPStatus.BAD_REQUEST,
        )
    return ("", HTTPStatus.NO_CONTENT)


# TODO shouldn't this be a little broader than this blueprint
@blueprint.before_app_request
def load_current_user():
    if user := session.get("user"):
        g.user = user
    else:
        g.user = None
