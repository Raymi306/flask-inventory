from contextlib import contextmanager
from enum import StrEnum

import click

import pymysql
from flask import current_app, g
from flask.cli import AppGroup

db_cli = AppGroup("db")


class DatabaseError(Exception):
    pass


class NotFoundError(DatabaseError):
    pass


class DuplicateError(DatabaseError):
    pass


def get_db_connection():
    if "db_connection" not in g:
        g.db_connection = pymysql.connect(
            host="localhost",
            port=current_app.config["DATABASE_PORT"],
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            database=current_app.config["DATABASE"],
            cursorclass=pymysql.cursors.DictCursor,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
        )
        g.in_transaction = False
    return g.db_connection


@contextmanager
def transaction():
    conn = get_db_connection()
    try:
        g.in_transaction = True
        conn.begin()
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        g.in_transaction = False


class LockType(StrEnum):
    READ = "READ"
    WRITE = "WRITE"


@contextmanager
def locked_tables(table_lock_type_pair: tuple["table name string", LockType], *additional_pairs):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        pairs = [" ".join(pair) for pair in (table_lock_type_pair, *additional_pairs)]
        cursor.execute(f"LOCK TABLES {', '.join(pairs)};")
        yield
        cursor.execute("UNLOCK TABLES;")


def close_db_connection(*_args, **_kwargs):
    if conn := g.pop("db_connection", None):
        conn.close()


def init_db():
    db = get_db_connection()
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
    app.teardown_appcontext(close_db_connection)
    app.cli.add_command(db_cli)
