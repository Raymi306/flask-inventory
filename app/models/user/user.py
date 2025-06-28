from dataclasses import dataclass
from datetime import datetime

import click
from flask.cli import AppGroup
from werkzeug.security import gen_salt

from app.constants import MIN_PASSWORD_LENGTH, PASSWORD_HASHER
from app.models.model import query

user_cli = AppGroup("user")


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime | None
    password_reset_required: bool


@query
def get_all_users(fire):
    results = fire()
    return [User(*result.values()) for result in results]


@query
def get_user_by_name(fire, name):
    result = fire(name)
    if result is not None:
        return User(*result.values())
    return result


@query
def get_user_by_id(fire, user_id):
    result = fire(user_id)
    if result is not None:
        return User(*result.values())
    return result


@query
def update_user_password(fire, user_id, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    fire(password_hash, user_id)


@query
def update_user_last_login(fire, user_id):
    fire(user_id)


@query
def create_user(fire, name, password, password_reset_required=True):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    password_hash = PASSWORD_HASHER.hash(password)
    return fire(name, password_hash, password_reset_required)["lastrowid"]


@query
def delete_user_by_name(fire, name):
    fire(name)


@user_cli.command("delete")
@click.argument("name")
def delete_user_by_name_command(name):
    delete_user_by_name(name)
    click.echo("Done.")


@user_cli.command("create")
@click.argument("name")
@click.argument("password", required=False)
def new_user_command(name, password):
    password_reset_required = False
    if password is None:
        password_reset_required = True
        password = gen_salt(24)
        click.echo(f"User {name}'s {password=}")
    create_user(name, password, password_reset_required)
    click.echo("Done.")


def setup_app(app):
    app.cli.add_command(user_cli)
