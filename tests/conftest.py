import pytest

from app.app import create_app
from app.db import get_db, init_db
from app.models import item as item_model
from app.models import user as user_model


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    app.config["DATABASE"] = app.config["DATABASE"] + "_test"
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


@pytest.fixture
def new_user(app):
    created_users = []

    def _inner(username="user", password="niceandlonggoodpassword"):
        created_users.append(f"'{username}'")
        with app.app_context():
            user_model.new_user(username, password)

    yield _inner

    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(f"DELETE FROM user WHERE username IN ({', '.join(created_users)});")
        db.commit()


@pytest.fixture
def new_authenticated_user(app, new_user):
    def _inner(client, username="user", password="niceandlonggoodpassword"):
        username = "user"
        password = "niceandlonggoodpassword"
        new_user(username, password)

        client.post(
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
        )
    yield _inner

@pytest.fixture
def new_item(app):
    created_items = []

    def _inner(user_id, name="item", description=None, quantity=0, unit=None):
        created_items.append(f"'{name}'")
        with app.app_context():
            item_model.create_item(user_id, name, description, quantity, unit)

    yield _inner

    with app.app_context():
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(f"DELETE FROM item WHERE name IN ({', '.join(created_items)});")
        db.commit()
