import pytest

from app.app import create_app
from app.models import user as user_model


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()


@pytest.fixture
def new_user(app):
    created_users = []

    def _inner(username="user", password="password"):
        created_users.append(username)
        with app.app_context():
            return user_model.new_user(username, password)

    yield _inner

    with app.app_context():
        for username in created_users:
            user_model.delete_user(username)
