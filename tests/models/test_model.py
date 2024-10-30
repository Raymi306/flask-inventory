import pytest

from app.models.model import DatabaseQuery


def test_no_query_attr():
    class OneFoo(DatabaseQuery):
        pass

    with pytest.raises(TypeError):
        OneFoo()


def test_mismatched_params():
    class OneFoo(DatabaseQuery):
        query = "%s"

    with pytest.raises(TypeError):
        OneFoo(1, 2)
    with pytest.raises(TypeError):
        OneFoo()


def test_invalid_name_scheme():
    class Foo(DatabaseQuery):
        pass

    with pytest.raises(TypeError):
        Foo()
