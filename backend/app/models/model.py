import inspect
from dataclasses import dataclass
from datetime import datetime
from functools import partial, wraps
from pathlib import Path

from app.db import get_db_connection

VALID_PREFIXES = ("get_all", "get", "create", "update", "delete")


@dataclass
class RevisionMixin:
    _id: int
    _user_id: int
    _datetime: datetime
    is_deleted: bool


def query(func):
    # order sensitive!
    name = func.__name__
    if name.startswith("get_all"):
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
    query_path = wrapped_file_path.parent / f"{name}.sql"
    with open(query_path) as fileobj:
        query_str = fileobj.read().rstrip("\n")

    @wraps(func)
    def inner(*args, **kwargs):
        partial_kwargs = {}
        if "autocommit" in kwargs:
            partial_kwargs["autocommit"] = kwargs.pop("autocommit")
        return func(partial(call_func, query_str, **partial_kwargs), *args, **kwargs)

    return inner


def _call_commit(query, *args, autocommit=True):
    conn = get_db_connection()
    context = {}
    with conn.cursor() as cursor:
        cursor.execute(query, args)
        context["lastrowid"] = cursor.lastrowid
    if autocommit:
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
