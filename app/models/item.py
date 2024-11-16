import json
from datetime import datetime

from flask import g
from flask.cli import AppGroup
from pydantic import BaseModel

from app.models.model import DatabaseQueryManager, NotFoundError


class Item(BaseModel):
    id: int
    name: str
    description: str | None
    quantity: int
    unit: str | None
    revisions: dict


class Tag(BaseModel):
    id: int
    name: str


class TagComment(BaseModel):
    id: int
    user_id: int
    item_id: int
    text: int
    revisions: dict


class ItemQueryManager(DatabaseQueryManager):
    create_item = "INSERT INTO item (name, description, quantity, unit, revisions) VALUES (%s, %s, %s, %s, %s);"
    create_item_comment = (
        "INSERT INTO item_comment (user_id, item_id, text, revisions) VALUES (%s, %s, %s, %s);"
    )
    create_item_tag = "INSERT INTO item_tag (name) VALUES (%s);"
    create_item_tag_association = (
        "INSERT INTO item_tag_junction (item_id, item_tag_id) VALUES (%s, %s);"
    )
    get_all_item_comments = (
        "SELECT "
        "id, user_id, item_id, text, revisions "
        "FROM item_comment "
        "JOIN item ON item_comment.item_id = item.id;"
    )
    get_all_items_with_tags = (
        "SELECT "
        "item.id AS item_id, item.name AS item_name, item.description AS item_description, "
        "item.quantity AS item_quantity, item.unit AS item_unit, item.revisions AS item_revisions "
        "item_tag.id AS item_tag.id, item_tag.name AS tag_name "
        "FROM item "
        "LEFT JOIN item_tag_junction ON item.id = item_tag_junction.item_id "
        "LEFT JOIN item_tag ON item_tag.id = item_tag_junction.item_tag_id;"
        # "LEFT JOIN item_tag ON item_tag.id = item_tag_junction.item_tag_id "
        # "ORDER BY item_id ASC;"
    )
    update_item = "UPDATE item SET (name, description, quantity, unit, revisions) VALUES (%s, %s, %s, %s, %s) WHERE id = %s;"


QUERY_MANAGER = ItemQueryManager()


def _map_items(items, item_comments):
    # good lord
    result = {}
    tags = []
    if not items:
        return []
    last_id = items[0]["item_id"]
    for item in items:
        current_id = item["item_id"]
        if current_id == last_id:
            tags.append({"id": item["tag_id"], "name": item["tag_name"]})
        else:
            result[current_id] = {
                "id": item["item_id"],
                "name": item["item_name"],
                "description": item["item_description"],
                "quantity": item["item_quantity"],
                "unit": item["item_unit"],
                "revisions": item["item_revisions"],
                "tags": tags.copy(),
                "comments": [],
            }
            tags = []
    for comment in item_comments:
        result[comment["item_id"]]["comments"].append(
            {
                "id": comment["id"],
                "user_id": comment["user_id"],
                "item_id": comment["item_id"],
                "text": comment["text"],
                "revisions": comment["revisions"],
            }
        )
    return result.values()


def get_items():
    items = QUERY_MANAGER.get_items_with_tags()
    item_comments = QUERY_MANAGER.get_item_comments()
    result = _map_items(items, item_comments)
    return result


def create_item(user_id, name, description=None, quantity=0, unit=None):
    if quantity < 0:
        raise ValueError("`quantity` must be a positive integer.")
    revisions = (
        {
            "user_id": user_id,
            "time": datetime.now().isoformat(),
            "content": {
                "name": name,
                "description": description,
                "quantity": quantity,
                "unit": unit,
            }
        },
    )
    QUERY_MANAGER.create_item(name, description, quantity, unit, json.dumps(revisions))


def create_item_comment(user_id, item_id, text):
    revisions = (
        {
            "user_id": user_id,
            "time": datetime.now().isoformat(),
            "content": {
                "user_id": user_id,
                "item_id": item_id,
                "text": text,
            },
        },
    )
    QUERY_MANAGER.create_item_comment(user_id, item_id, text, json.dumps(revisions))


def create_item_tag(name):
    QUERY_MANAGER.create_item_tag(name)


def create_item_tag_association(item_id, item_tag_id):
    QUERY_MANAGER.create_item_tag_association(item_id, item_tag_id)


def update_item(id_, user_id, name, description, quantity, unit):
    existing_item = QUERY_MANAGER.get_item_by_id(id_)
    if existing_item is None:
        raise NotFoundError
    revisions = existing_item["revisions"]
    revisions.append(
        {
            "user_id": user_id,
            "time": datetime.now().isoformat(),
            "content": {
                "name": name,
                "description": description,
                "quantity": quantity,
                "unit": unit,
            }
        }
    )
    QUERY_MANAGER.update_item(name, description, quantity, unit, revisions, id_)
