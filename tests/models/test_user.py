from pymysql.err import IntegrityError

from app.constants import MIN_PASSWORD_LENGTH
from app.db import get_db
from app.models.user import get_user_by_id, get_user_by_name, get_users


class TestNewUserCommand:
    @staticmethod
    def test_success(app, cli_runner):
        username = "foo"
        cli_runner.invoke(args=f"user create {username}")
        with app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
                assert cursor.fetchone()["username"] == username
        cli_runner.invoke(args=f"user delete {username}")

    @staticmethod
    def test_create_custom_password_success(cli_runner):
        username = "foo"
        password = "sufficientlystrongpassword"
        result = cli_runner.invoke(args=f"user create {username} {password}")
        assert f"User {username}'s {password=}" in result.output
        cli_runner.invoke(args=f"user delete {username}")

    @staticmethod
    def test_create_custom_password_failure(cli_runner):
        username = "foo"
        password = "2short"
        result = cli_runner.invoke(args=f"user create {username} {password}")
        assert isinstance(result.exception, ValueError)
        assert f"Password must be at least {MIN_PASSWORD_LENGTH} characters long." == str(
            result.exception
        )

    @staticmethod
    def test_delete(cli_runner):
        username = "foo"
        cli_runner.invoke(args=f"user create {username}")
        cli_runner.invoke(args=f"user delete {username}")
        # if it wasn't deleted, we'd get a duplicate key error
        cli_runner.invoke(args=f"user create {username}")
        result = cli_runner.invoke(args=f"user create {username}")
        assert isinstance(result.exception, IntegrityError)
        cli_runner.invoke(args=f"user delete {username}")


def test_get_user_by_id(app, new_user):
    username = "user"
    new_user(username)
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            expected_user = cursor.fetchone()
        result = get_user_by_id(expected_user["id"])
        assert expected_user == result


def test_get_user_by_name(app, new_user):
    username = "user"
    new_user(username)
    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            expected_user = cursor.fetchone()
        result = get_user_by_name(username)
        assert expected_user == result


def test_get_users(app, new_user):
    with app.app_context():
        assert not get_users()

    num_users = 2
    for i in range(num_users):
        new_user(str(i))

    with app.app_context():
        assert len(get_users()) == num_users
