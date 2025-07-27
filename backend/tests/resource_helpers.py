import pytest

from app.models.item import (
    create_item,
    create_item_comment,
    create_item_tag,
    create_item_tag_association,
)
from app.models.user import create_user


@pytest.fixture
def new_user(app):
    def _inner(username="user", password="niceandlonggoodpassword", password_reset_required=False):
        with app.app_context():
            return create_user(username, password, password_reset_required)

    yield _inner


@pytest.fixture
def new_authenticated_user(app, new_user):
    def _inner(
        client, username="user", password="niceandlonggoodpassword", password_reset_required=False
    ):
        username = "user"
        password = "niceandlonggoodpassword"
        user_id = new_user(username, password, password_reset_required)

        client.post(
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
        )
        return user_id

    yield _inner


@pytest.fixture
def new_item(app):
    def _inner(user_id, name="item", description=None, quantity=0, unit=None):
        with app.app_context():
            return create_item(user_id, name, description, quantity, unit)

    yield _inner


@pytest.fixture
def new_item_comment(app):
    def _inner(user_id, item_id, text="test comment"):
        with app.app_context():
            return create_item_comment(user_id, item_id, text)

    yield _inner


@pytest.fixture
def new_item_tag(app):
    def _inner(user_id, name="test tag"):
        with app.app_context():
            return create_item_tag(name)

    yield _inner


@pytest.fixture
def new_item_tag_association(app):
    def _inner(item_id, tag_id):
        with app.app_context():
            create_item_tag_association(item_id, tag_id)

    yield _inner
