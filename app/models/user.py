from datetime import datetime

import click
from flask.cli import AppGroup
from pydantic import BaseModel
from werkzeug.security import gen_salt

from app.constants import MIN_PASSWORD_LENGTH, PASSWORD_HASHER
from app.models.model import DatabaseQuery

user_cli = AppGroup("user")


class User(BaseModel):
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime | None
    password_reset_required: bool


class OneUserByName(DatabaseQuery):
    query = f"SELECT {', '.join(User.model_fields)} FROM user WHERE username=%s;"


def get_user_by_name(name):
    return OneUserByName(name)()


class OneUserById(DatabaseQuery):
    query = f"SELECT {', '.join(User.model_fields)} FROM user WHERE id=%s;"


def get_user_by_id(id_):
    return OneUserById(id_)()


class UpdateUserPassword(DatabaseQuery):
    query = "UPDATE user SET password_hash = %s WHERE id = %s;"


def update_user_password(id_, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    UpdateUserPassword(password_hash, id_)()


class UpdateUserLastLogin(DatabaseQuery):
    query = "UPDATE user SET last_login = CURRENT_TIMESTAMP() WHERE id = %s;"


def update_user_last_login(id_):
    UpdateUserLastLogin(id_)()


class CreateUser(DatabaseQuery):
    query = (
        "INSERT INTO user (username, password_hash, password_reset_required) VALUES (%s, %s, %s);"
    )


def new_user(name, password, password_reset_required=True):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    CreateUser(name, password_hash, password_reset_required)()


class DeleteUser(DatabaseQuery):
    query = "DELETE FROM user WHERE username = %s;"


def delete_user(name):
    DeleteUser(name)()


@user_cli.command("delete")
@click.argument("name")
def delete_user_command(name):
    delete_user(name)
    click.echo("Done.")


@user_cli.command("create")
@click.argument("name")
@click.argument("password", required=False)
def new_user_command(name, password):
    password_reset_required = False
    if password is None:
        password_reset_required = True
        password = gen_salt(24)
    new_user(name, password, password_reset_required)
    click.echo("Done.")
    click.echo(f"User {name}'s {password=}")


def setup_app(app):
    app.cli.add_command(user_cli)
