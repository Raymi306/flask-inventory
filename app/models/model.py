from abc import ABC

from app.db import get_db
from app.utils import snake_to_camel


def _call_commit(self, *args):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, args)
    db.commit()


def _call_fetchone(self, *args):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, args)
        return cursor.fetchone()


def _call_fetchmany(self, *args):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, args)
        return cursor.fetchmany()


class DatabaseQuery:
    def __init__(self, _, query):
        self.query = query

    def __new__(cls, name, query):
        if name.startswith("get"):
            call_func = _call_fetchone
        elif name.startswith("get_many"):
            call_func = _call_fetchmany
        elif name.startswith("create") or name.startswith("update") or name.startswith("delete"):
            call_func = _call_commit
        else:
            raise TypeError(
                "Class name must start with `One`, `Many`, `Create`, `Update`, or `Delete`"
            )
        new_cls = type(f"{snake_to_camel(name)}{cls.__name__}", (cls,), {"__call__": call_func})
        return super().__new__(new_cls)


class DatabaseQueryManager(ABC):
    def __new__(cls, *args, **kwargs):
        for key, value in cls.__dict__.items():
            if key.startswith("_"):
                pass
            if (
                key.startswith("get")
                or key.startswith("get_many")
                or key.startswith("create")
                or key.startswith("update")
                or key.startswith("delete")
            ):
                setattr(cls, key, DatabaseQuery(key, value))
        return super().__new__(cls)
