import pytest

from app.db import get_db_connection
from app.models.item import (
    create_item,
    create_item_comment,
    create_item_tag,
    create_item_tag_association,
)
from app.models.user import create_user


@pytest.fixture
def new_user(app):
    created_users = []

    def _inner(username="user", password="niceandlonggoodpassword", password_reset_required=False):
        with app.app_context():
            user_id = create_user(username, password, password_reset_required)
            created_users.append(str(user_id))
            return user_id

    yield _inner

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM user WHERE id IN ({', '.join(created_users)});")
        conn.commit()


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
    created_items = []

    def _inner(user_id, name="item", description=None, quantity=0, unit=None):
        created_items.append(f"'{name}'")
        with app.app_context():
            return create_item(user_id, name, description, quantity, unit)

    yield _inner

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM item WHERE name IN ({', '.join(created_items)});")
        conn.commit()


@pytest.fixture
def new_item_comment(app):
    created_item_comments = []

    def _inner(user_id, item_id, text="test comment"):
        with app.app_context():
            item_comment_id = create_item_comment(user_id, item_id, text)
            created_item_comments.append(str(item_comment_id))
            return item_comment_id

    yield _inner

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM item_comment WHERE id IN ({', '.join(created_item_comments)});"
            )
        conn.commit()


@pytest.fixture
def new_item_tag(app):
    created_item_tags = []

    def _inner(user_id, name="test tag"):
        with app.app_context():
            tag_id = create_item_tag(name)
            created_item_tags.append(str(tag_id))
            return tag_id

    yield _inner

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM item_tag WHERE id IN ({', '.join(created_item_tags)});")
        conn.commit()


@pytest.fixture
def new_item_tag_association(app):
    item_ids = []
    tag_ids = []

    def _inner(item_id, tag_id):
        with app.app_context():
            create_item_tag_association(item_id, tag_id)
            item_ids.append(str(item_id))
            tag_ids.append(str(tag_id))

    yield _inner

    with app.app_context():
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM item_tag_junction WHERE item_id IN ({', '.join(item_ids)}) AND item_tag_id in ({', '.join(tag_ids)});"
            )
        conn.commit()
