from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

import pytest
from argon2 import PasswordHasher
from flask import session

from app.models.user import get_user_by_name


@pytest.fixture(autouse=True)
def clean(truncate_all):
    pass


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
            assert session["user"]
            assert session["user"]["last_login"] is None

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
            assert session["user"]
            assert isinstance(session["user"]["last_login"], datetime)

    @staticmethod
    def test_failure_mismatched_password(app, client, new_user):
        username = "user"
        new_user(username)

        with client:
            response = client.post(
                "/auth/login",
                data={
                    "username": username,
                    "password": "wrongpassword",
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert "user" not in session

    @staticmethod
    def test_hasher_changed(app, client, new_user):
        username = "user"
        password = "niceandlonggoodpassword"
        with patch("app.models.user.user.PASSWORD_HASHER") as mock_hasher:
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
                assert session["user"]
            new_user = get_user_by_name(username)
            assert original_user.password_hash != new_user.password_hash
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
                assert session["user"]
            stabilized_user = get_user_by_name(username)
            assert stabilized_user.password_hash == new_user.password_hash

    @staticmethod
    def test_empty_form_fields(client, new_user):
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
            assert "user" not in session


def test_logout(client):
    with client.session_transaction() as presession:
        presession["user"] = {"id": 1}

    with client:
        response = client.delete("/auth/logout")
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert b"" == response.data
        assert "user" not in session

        # idempotent
        response = client.delete("/auth/logout")
        assert response.status_code == HTTPStatus.NO_CONTENT
        assert b"" == response.data
        assert "user" not in session


class TestChangePassword:
    @staticmethod
    @pytest.mark.parametrize(
        "reset_required",
        (
            True,
            False,
        ),
    )
    def test_success(client, new_authenticated_user, reset_required):
        username = "user"
        password = "niceandlonggoodpassword"
        with client:
            new_authenticated_user(client, username, password, reset_required)
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
    def test_passwords_same(client, new_authenticated_user):
        username = "user"
        password = "niceandlonggoodpassword"
        with client:
            new_authenticated_user(client, username, password)
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": password,
                },
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    def test_password_too_short(client, new_authenticated_user):
        username = "user"
        password = "niceandlonggoodpassword"
        with client:
            new_authenticated_user(client, username, password)
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": "2short",
                },
            )
            assert response.status_code == HTTPStatus.BAD_REQUEST

    @staticmethod
    def test_not_authenticated(client, new_user):
        password = "niceandlonggoodpassword"
        new_user(password=password)
        with client:
            response = client.post(
                "/auth/password",
                data={
                    "old_password": password,
                    "new_password": "niceandlonggoodreplacementpassword",
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED

    @staticmethod
    def test_bad_old_password(client, new_user):
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
