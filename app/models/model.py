from abc import ABC

from app.db import get_db
from app.utils import camel_case_split


def _call_commit(self):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, self.query_params)
    db.commit()


def _call_fetchone(self):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, self.query_params)
        return cursor.fetchone()


def _call_fetchmany(self):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(self.query, self.query_params)
        return cursor.fetchmany()


class DatabaseQuery(ABC):
    query: str

    def __init__(self, *args):
        self.query_params = tuple(args)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "query"):
            raise TypeError("Must define class attribute `query`")
        num_params = cls.query.count("%s")
        num_args = len(args)
        if num_params != num_args:
            raise TypeError(
                f"Number of arguments, {num_args} is not equal to number of params, {num_params}"
            )
        name_parts = camel_case_split(cls.__name__)
        match name_parts[0]:
            case "One":
                cls.__call__ = _call_fetchone
            case "Many":
                cls.__call__ = _call_fetchmany
            case "Create" | "Update" | "Delete":
                cls.__call__ = _call_commit
            case _:
                raise TypeError(
                    "Class name must start with `One`, `Many`, `Create`, `Update`, or `Delete`"
                )
        return super().__new__(cls)
