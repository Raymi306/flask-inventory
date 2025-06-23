from datetime import datetime

import click
from flask.cli import AppGroup
from pydantic import BaseModel
from werkzeug.security import gen_salt

from app.constants import MIN_PASSWORD_LENGTH, PASSWORD_HASHER
from app.models.model import DatabaseQueryManager

user_cli = AppGroup("user")


class User(BaseModel):
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime | None
    password_reset_required: bool


class UserQueryManager(DatabaseQueryManager):
    get_all_users = f"SELECT {', '.join(User.model_fields)} FROM user;"
    get_user_by_name = f"SELECT {', '.join(User.model_fields)} FROM user WHERE username = %s;"
    get_user_by_id = f"SELECT {', '.join(User.model_fields)} FROM user WHERE id = %s;"
    update_user_password = "UPDATE user SET password_hash = %s WHERE id = %s;"
    update_user_last_login = "UPDATE user SET last_login = CURRENT_TIMESTAMP() WHERE id = %s;"
    create_user = (
        "INSERT INTO user (username, password_hash, password_reset_required) VALUES (%s, %s, %s);"
    )
    delete_user_by_name = "DELETE FROM user WHERE username = %s;"


#QUERY_MANAGER = UserQueryManager()


def get_users():
    return QUERY_MANAGER.get_all_users()


def get_user_by_name(name):
    return QUERY_MANAGER.get_user_by_name(name)


def get_user_by_id(id_):
    return QUERY_MANAGER.get_user_by_id(id_)


def update_user_password(id_, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    QUERY_MANAGER.update_user_password(password_hash, id_)


def update_user_last_login(id_):
    QUERY_MANAGER.update_user_last_login(id_)


def new_user(name, password, password_reset_required=True):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    QUERY_MANAGER.create_user(name, password_hash, password_reset_required)


def delete_user(name):
    QUERY_MANAGER.delete_user_by_name(name)


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
