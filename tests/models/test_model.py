import pytest

from app.models.model import query

def test_query_decorator(app):

    with app.app_context():

        @query
        def get_testfunc(query_func):
            assert query_func == "TESTING\n"

    get_testfunc()
