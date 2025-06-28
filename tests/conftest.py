import pytest

from app.app import create_app
from app.db import get_db_connection, init_db

from .resource_helpers import (
    new_authenticated_user,
    new_item,
    new_item_comment,
    new_item_tag,
    new_item_tag_association,
    new_user,
)


@pytest.fixture(scope="session")
def app():
    config = {
        "DATABASE": "inventory_test",
        "DATABASE_USER": "inventory_test_user",
        "DATABASE_PASSWORD": "inventory_test_password",
        "SECRET_KEY": "myvoiceismypassport",
        "TESTING": True,
    }
    app = create_app(config)
    return app


@pytest.fixture(scope="session", autouse=True)
def reset_db(app):
    with app.app_context():
        init_db()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()
