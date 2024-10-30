from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

from argon2 import PasswordHasher
from flask import session

from app.models.user import get_user_by_name


class TestLogin:
    @staticmethod
    def test_success(app, client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)

        with client:
            response = client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            assert response.status_code == HTTPStatus.NO_CONTENT
            assert b"" == response.data
            assert session["user_id"]
            assert session["last_login"] is None

            # idempotent
            response = client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            assert response.status_code == HTTPStatus.NO_CONTENT
            assert b"" == response.data
            assert session["user_id"]
            assert isinstance(session["last_login"], datetime)

    @staticmethod
    def test_hasher_changed(app, client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        with patch("app.models.user.PASSWORD_HASHER") as mock_hasher:
            hasher = PasswordHasher(memory_cost=100)
            mock_hasher.hash = hasher.hash
            new_user(username, password)
        with app.app_context():
            original_user = get_user_by_name(username)
            with client:
                response = client.post(
                    "/auth/login",
                    data={
                        "username": username,
                        "password": password,
                    },
                )
                assert response.status_code == HTTPStatus.NO_CONTENT
                assert b"" == response.data
                assert session["user_id"]
            new_user = get_user_by_name(username)
            assert original_user["password_hash"] != new_user["password_hash"]
            with client:
                response = client.post(
                    "/auth/login",
                    data={
                        "username": username,
                        "password": password,
                    },
                )
                assert response.status_code == HTTPStatus.NO_CONTENT
                assert b"" == response.data
                assert session["user_id"]
            stabilized_user = get_user_by_name(username)
            assert stabilized_user["password_hash"] == new_user["password_hash"]

    @staticmethod
    def test_failure(client, new_user):
        new_user()
        with client:
            response = client.post(
                "/auth/login",
                data={
                    "username": "",
                    "password": "",
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert "user_id" not in session


def test_logout(client):
    with client.session_transaction() as presession:
        presession["user_id"] = 1

    with client:
        response = client.delete("/auth/logout")
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert b"" == response.data
        assert "user_id" not in session

        # idempotent
        response = client.delete("/auth/logout")
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert b"" == response.data
        assert "user_id" not in session


class TestChangePassword:
    @staticmethod
    def test_success(client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)
        with client:
            client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": "anewsufficientlylongandstrongpassword",
                },
            )
            assert response.status_code == HTTPStatus.NO_CONTENT
            assert b"" == response.data

    @staticmethod
    def test_passwords_same(client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)
        with client:
            client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": password,
                },
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    def test_password_too_short(client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)
        with client:
            client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": "2short",
                },
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    def test_no_session_cookie(client, new_user):
        password = "niceandlonggoodpassword"
        new_user(password=password)
        with client:
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": "2short",
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    def test_bad_password(client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)
        with client:
            client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
            )
            response = client.post(
                "/auth/password",
                data={
                    "old_password": "invalid",
                    "new_password": "xxxxxxxxxxxxxxxxxxxxxxxx",
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED
