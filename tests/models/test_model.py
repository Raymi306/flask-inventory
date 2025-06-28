import pytest

from app.models.model import _call_commit, _call_fetchall, _call_fetchone, query


class TestQueryDecorator:
    @pytest.mark.parametrize(
        "function_name, expected_func",
        (
            ("get_testfunc", _call_fetchone),
            ("get_all_testfunc", _call_fetchall),
            ("create_testfunc", _call_commit),
            ("update_testfunc", _call_commit),
            ("delete_testfunc", _call_commit),
        ),
    )
    @staticmethod
    def test_all_good(app, function_name, expected_func):
        def standin(fire):
            assert fire.func is expected_func
            assert fire.args[0] == "TESTING"

        standin.__name__ = function_name

        with app.app_context():
            query(standin)()

    @staticmethod
    def test_missing_sql_file(app):
        with pytest.raises(FileNotFoundError):

            @query
            def get_nosuchfile(fire):
                pass

    @staticmethod
    def test_bad_function_name(app):
        with pytest.raises(ValueError):

            @query
            def testfunc(fire):
                pass
