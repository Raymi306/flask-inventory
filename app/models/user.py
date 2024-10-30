from datetime import datetime

import click
from flask.cli import AppGroup
from pydantic import BaseModel
from werkzeug.security import gen_salt

from app.db import get_db
from app.utils import PASSWORD_HASHER

user_cli = AppGroup("user")


class User(BaseModel):
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime | None


def get_user_by_name(name):
    script = f"SELECT {', '.join(User.model_fields)} FROM user WHERE username=%s;"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (name,))
        return cursor.fetchone()


def get_user_by_id(id_):
    script = f"SELECT {', '.join(User.model_fields)} FROM user WHERE id=%s;"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (id_,))
        return cursor.fetchone()


def update_user_password_hash(id_, password_hash):
    script = "UPDATE user SET password_hash = %s WHERE id = %s;"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (password_hash, id_))
    db.commit()


def update_user_last_login(id_):
    script = "UPDATE user SET last_login = CURRENT_TIMESTAMP() WHERE id = %s;"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (id_,))
    db.commit()


def new_user(name, password):
    password_hash = PASSWORD_HASHER.hash(password)
    script = "INSERT INTO user " "(username, password_hash) " "VALUES (%s, %s);"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (name, password_hash))
    db.commit()


def delete_user(name):
    script = "DELETE FROM user WHERE username = %s;"
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(script, (name,))
    db.commit()


@user_cli.command("delete")
@click.argument("name")
def delete_user_command(name):
    delete_user(name)
    click.echo("Done.")


@user_cli.command("create")
@click.argument("name")
@click.argument("password", default=lambda: gen_salt(24))
def new_user_command(name, password):
    new_user(name, password)
    click.echo("Done.")
    click.echo(f"User {name}'s {password=}")


def setup_app(app):
    app.cli.add_command(user_cli)
