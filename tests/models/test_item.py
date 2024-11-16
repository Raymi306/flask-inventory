import json
from contextlib import nullcontext

import pytest
from flask import session

from app.db import get_db
from app.models.item import (
    create_item,
    create_item_comment,
    create_item_tag,
    create_item_tag_association,
    update_item,
)


@pytest.mark.parametrize(
    "name, description, quantity, unit, error_context",
    (
        ("item1", None, 0, None, nullcontext()),
        ("item2", "description", 0, "gallons", nullcontext()),
        ("item3", None, 0, "gallons", nullcontext()),
        ("item4", "description", 0, None, nullcontext()),
        ("item1", None, -1, None, pytest.raises(ValueError)),
    ),
)
def test_create_item(
    app,
    client,
    new_authenticated_user,
    name,
    description,
    quantity,
    unit,
    error_context,
):
    expected_obj = {
        "name": name,
        "description": description,
        "quantity": quantity,
        "unit": unit,
    }
    user_name = "user"
    with app.app_context(), error_context, client:
        new_authenticated_user(client, user_name)
        create_item(session["user"]["id"], **expected_obj)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM item WHERE name = %s", (name,))
            created_obj = cursor.fetchone()
            created_obj.pop("id")
            created_obj.pop("revisions")
            assert created_obj == expected_obj
            cursor.execute("DELETE FROM item WHERE name = %s", (name,))
        db.commit()


def test_create_item_comment(app, client, new_item, new_authenticated_user):
    item_name = "item"
    user_name = "user"
    text = "a fancy comment"
    with app.app_context(), client:
        new_authenticated_user(client, user_name)
        new_item(session["user"]["id"], item_name)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM item WHERE name = %s", (item_name,))
            item_id = cursor.fetchone()["id"]
            create_item_comment(session["user"]["id"], item_id, text)
            cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
            created_obj = cursor.fetchone()
            created_obj.pop("id")
            created_obj.pop("revisions")
            assert created_obj == {
                "user_id": session["user"]["id"],
                "item_id": item_id,
                "text": text,
            }
            cursor.execute("DELETE FROM item_comment WHERE item_id = %s", (item_id,))
        db.commit()


def test_create_item_tag(app, client):
    tag_name = "tag"
    with app.app_context(), client:
        create_item_tag(tag_name)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM item_tag WHERE name = %s", (tag_name,))
            assert cursor.fetchone()
            cursor.execute("DELETE FROM item_tag WHERE name = %s", (tag_name,))
        db.commit()


def test_create_item_tag_association(app, client, new_item, new_authenticated_user):
    item_name = "item"
    user_name = "user"
    tag_name = "tag"
    with app.app_context(), client:
        new_authenticated_user(client, user_name)
        new_item(session["user"]["id"], item_name)
        create_item_tag(tag_name)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM item WHERE name = %s", (item_name,))
            item_id = cursor.fetchone()["id"]
            cursor.execute("SELECT id FROM item_tag WHERE name = %s", (tag_name,))
            tag_id = cursor.fetchone()["id"]
            create_item_tag_association(item_id, tag_id)
            cursor.execute("DELETE FROM item_tag_junction WHERE item_tag_id = %s", (tag_id,))
            cursor.execute("DELETE FROM item_tag WHERE name = %s", (tag_name,))
        db.commit()


def test_update_item(app, client, new_item, new_authenticated_user):
    expected_obj = {
        "name": "item",
        "description": "description",
        "quantity": 1,
        "unit": None,
    }
    expected_changed_obj = {
        "name": "item2",
        "description": "description2",
        "quantity": 2,
        "unit": "gallons",
    }
    user_name = "user"
    with app.app_context(), client:
        new_authenticated_user(client, user_name)
        new_item(session["user"]["id"], **expected_obj)
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM item WHERE name = %s", (expected_obj["name"],))
            created_obj = cursor.fetchone()
            update_item(created_obj["id"], session["user"]["id"], **expected_changed_obj)
            cursor.execute("SELECT * FROM item WHERE name = %s", (expected_changed_obj["name"],))
            updated_obj = cursor.fetchone()
            updated_obj.pop("id")
            revisions = json.loads(updated_obj.pop("revisions"))
            assert len(revisions) == 2  # noqa PLR2004
            assert updated_obj == expected_changed_obj
            cursor.execute("DELETE FROM item WHERE name = %s", (expected_changed_obj["name"],))
        db.commit()
