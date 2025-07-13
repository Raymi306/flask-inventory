from pydantic_core import ValidationError
from pymysql.err import IntegrityError

from app.models.user import get_all_users, get_user_by_id, get_user_by_name


class TestUserCliCommands:
    @staticmethod
    def test_create_success(app, cli_runner):
        username = "foo1"
        result = cli_runner.invoke(args=f"user create {username}")
        with app.app_context():
            user = get_user_by_name(username)
            assert user.username == username
            assert "password" in result.output
        cli_runner.invoke(args=f"user delete {username}")

    @staticmethod
    def test_create_custom_password_success(cli_runner):
        username = "foo2"
        password = "sufficientlystrongpassword"
        result = cli_runner.invoke(args=f"user create {username} {password}")
        assert password not in result.output
        cli_runner.invoke(args=f"user delete {username}")

    @staticmethod
    def test_create_custom_password_failure(cli_runner):
        username = "foo3"
        password = "2short"
        result = cli_runner.invoke(args=f"user create {username} {password}")
        assert isinstance(result.exception, ValidationError)

    @staticmethod
    def test_create_duplicate_usernames(cli_runner):
        result = cli_runner.invoke(args="user create dupe")
        assert result.exception is None
        result = cli_runner.invoke(args="user create dupe")
        assert isinstance(result.exception, IntegrityError)
        cli_runner.invoke(args="user delete dupe")

    @staticmethod
    def test_delete(cli_runner):
        username = "foo4"
        result = cli_runner.invoke(args=f"user create {username}")
        assert result.exception is None
        result = cli_runner.invoke(args=f"user delete {username}")
        assert result.exception is None
        # if it wasn't deleted, we'd get a duplicate key error
        result = cli_runner.invoke(args=f"user create {username}")
        assert result.exception is None
        result = cli_runner.invoke(args=f"user delete {username}")
        assert result.exception is None


class TestGetUserById:
    @staticmethod
    def test_success(app, new_user):
        username = "foo5"
        user_id = new_user(username)
        with app.app_context():
            result = get_user_by_id(user_id)
            assert result.id
            assert result.username == username
            assert result.password_hash
            assert result.created_at
            assert result.last_login is None
            assert not result.password_reset_required

    @staticmethod
    def test_not_found(app):
        with app.app_context():
            assert get_user_by_id(1) is None


class TestGetUserByName:
    @staticmethod
    def test_success(app, new_user):
        username = "foo6"
        new_user(username)
        with app.app_context():
            result = get_user_by_name(username)
            assert result.id
            assert result.username == username
            assert result.password_hash
            assert result.created_at
            assert result.last_login is None
            assert not result.password_reset_required

    @staticmethod
    def test_not_found(app):
        with app.app_context():
            assert get_user_by_id("foo") is None


def test_get_all_users(app, new_user):
    with app.app_context():
        assert len(get_all_users()) == 0

    num_users = 2
    for i in range(num_users):
        new_user(str(i))

    with app.app_context():
        assert len(get_all_users()) == num_users
