import inspect
from dataclasses import dataclass
from datetime import datetime
from enum import auto, StrEnum
from functools import partial, wraps
from pathlib import Path

from flask import g

from app.db import get_db_connection

VALID_PREFIXES = ("get_all", "get_joined", "get", "create", "update", "delete")


@dataclass
class RevisionMixin:
    _id: int
    _user_id: int
    _datetime: datetime
    is_deleted: bool


def query(func):
    name = func.__name__
    module = func.__module__.split(".")[-1]
    # these branches are order sensitive!
    # make sure VALID_PREFIXES is up-to-date if editing
    # TODO overengineer a solution to couple these things and obviate the need for these comments?
    if name.startswith("get_all") or name.startswith("get_joined"):
        call_func = _call_fetchall
    elif name.startswith("get"):
        call_func = _call_fetchone
    elif name.startswith("create") or name.startswith("update") or name.startswith("delete"):
        call_func = _call_commit
    else:
        raise ValueError(
            f"Function name {name} is invalid, must start with {','.join(VALID_PREFIXES)}"
        )

    wrapped_file_path = Path(inspect.getfile(func))
    query_path = wrapped_file_path.parent / f"{module}_queries" / f"{name}.sql"
    with open(query_path) as fileobj:
        query_str = fileobj.read().rstrip("\n")

    @wraps(func)
    def inner(*args, **kwargs):
        return func(partial(call_func, query_str), *args, **kwargs)

    return inner


def _call_commit(query, *args):
    conn = get_db_connection()
    context = {}
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        context["lastrowid"] = cursor.lastrowid
        context["rowcount"] = cursor.rowcount
    if not g.in_transaction:
        conn.commit()
    return context


def _call_fetchone(query, *args):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        return cursor.fetchone()


def _call_fetchall(query, *args):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        return cursor.fetchall()
