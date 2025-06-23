# TODO separate model and db stuff a bit?
from abc import ABC

from pydantic import create_model

from app.db import get_db
from app.utils import snake_to_camel


VALID_PREFIXES = ("get_all", "get", "create", "update", "delete")


class DatabaseError(Exception):
    pass


class NotFoundError(DatabaseError):
    pass


def revision_factory(cls):
    return create_model(
        user_id=int,
        time=datetime,
        __base__=cls,
    )

import inspect
from functools import wraps
from pathlib import Path

def query(func):
    # TODO break into testable pieces
    # NOTE is this cached..?
    db = get_db()

    wrapped_file_path = Path(inspect.getfile(func))
    query_path = wrapped_file_path.parent / f"{func.__name__}.sql"
    with open(query_path, "r") as fileobj:
        query_str = fileobj.read()

    # order sensitive!
    if name.startswith("get_all"):
        call_func = _call_fetchall
    elif name.startswith("get"):
        call_func = _call_fetchone
    elif name.startswith("create") or name.startswith("update") or name.startswith("delete"):
        call_func = _call_commit
    else:
        raise TypeError(
            # TODO improve me
            f"Name must start with {','.join(VALID_PREFIXES)}"
        )

    @wraps(func)
    def inner(*args, **kwargs):
        # TODO pass in a function preloaded with query?
        # would partial be useful here somehow?
        return func(query_str, *args, **kwargs)
    return inner


class DatabaseQuery:
    def __init__(self, _, query):
        self.query = query
        self.db = get_db()

    def __new__(cls, name, query):
        new_cls = type(f"{snake_to_camel(name)}{cls.__name__}", (cls,), {"__call__": call_func})
        return super().__new__(new_cls)

def _call_commit(db, *args):
    with self.db.cursor() as cursor:
        cursor.execute(self.query, args)
    self.db.commit()

def _call_fetchone(db, *args):
    with self.db.cursor() as cursor:
        cursor.execute(self.query, args)
        return cursor.fetchone()

def _call_fetchall(db, *args):
    with self.db.cursor() as cursor:
        cursor.execute(self.query, args)
        return cursor.fetchall()


class DatabaseQueryManager(ABC):
    def __new__(cls, *args, **kwargs):
        for key, value in cls.__dict__.items():
            if key.startswith("_"):
                pass
            for prefix in VALID_PREFIXES:
                if key.startswith(prefix):
                    setattr(cls, key, DatabaseQuery(key, value))
        return super().__new__(cls)
