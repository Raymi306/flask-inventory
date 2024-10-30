import click
import pymysql
from flask import current_app, g
from flask.cli import AppGroup
from pymysql.constants import CLIENT

db_cli = AppGroup("db")


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host="localhost",
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            database=current_app.config["DATABASE"],
            cursorclass=pymysql.cursors.DictCursor,
            client_flag=CLIENT.MULTI_STATEMENTS,
        )
    return g.db


def close_db(*_args, **_kwargs):
    if db := g.pop("db", None):
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("models/schema.sql") as file_obj:
        with db.cursor() as cursor:
            script = file_obj.read().decode("utf8")
            cursor.execute(script)
    db.commit()


@db_cli.command("init")
def init_db_command():
    init_db()
    click.echo("Done.")


def setup_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(db_cli)
