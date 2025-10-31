from dataclasses import astuple, dataclass
from datetime import datetime, timezone
from itertools import groupby

from app.db import transaction, NotFoundError
from app.models.model import RevisionMixin, query


@dataclass
class Item:
    id: int
    name: str
    description: str | None
    quantity: int
    unit: str | None


@dataclass
class ItemRevision(Item, RevisionMixin):
    pass


@dataclass
class ItemTag:
    id: int
    name: str


@dataclass
class ItemComment:
    id: int
    user_id: int
    item_id: int
    text: str


@dataclass
class ItemCommentRevision(RevisionMixin):
    id: int
    text: str


@dataclass
class ItemCommentFull(ItemComment):
    has_revisions: bool


@dataclass
class ItemFull(Item):
    comments: list[ItemComment]
    tags: list[ItemTag]
    has_revisions: bool


@query
def create_item(fire, user_id, name, description=None, quantity=0, unit=None):
    with transaction():
        item_id = fire(name, description, quantity, unit, autocommit=False)["lastrowid"]
        create_item_revision(user_id, item_id, name, description, quantity, unit, False, autocommit=False)
        return item_id


@query
def create_item_revision(fire, user_id, item_id, name, description, quantity, unit, is_deleted=False):
    now = datetime.now(timezone.utc)
    return fire(user_id, now, item_id, name, description, quantity, unit, is_deleted)["lastrowid"]


@query
def get_item_by_id(fire, item_id):
    result = fire(item_id)
    if not result:
        raise NotFoundError
    return Item(*result.values())


def make_joined_item(item_id, rows):
    tags = {}
    comments = {}
    for row in rows:
        # account for the nature of left joins producing nulls
        if row["tag_id"]:
            tags[row["tag_id"]] = ItemTag(
                row["tag_id"],
                row["tag_name"],
            )
        # account for the nature of left joins producing nulls
        if row["comment_id"]:
            comments[row["comment_id"]] = ItemCommentFull(
                row["comment_id"],
                row["comment_user_id"],
                item_id,
                row["comment_text"],
                bool(row["item_comment_has_revisions"]),
            )
    result = ItemFull(
        item_id,
        row["name"],
        row["description"],
        row["quantity"],
        row["unit"],
        list(comments.values()),
        list(tags.values()),
        bool(row["item_has_revisions"]),
    )
    return result


@query
def get_all_joined_items(fire):
    # TODO discuss compromises, cartesian product
    grouped = groupby(fire(), lambda row: row["id"])

    items = []
    for item_id, rows in grouped:
        items.append(
            make_joined_item(item_id, rows)
        )
    return items


@query
def get_joined_item_by_id(fire, item_id):
    rows = fire(item_id)
    if not rows:
        raise NotFoundError
    result = make_joined_item(item_id, rows)
    return result


@query
def get_all_items(fire):
    results = fire()
    return [Item(*result.values()) for result in results]


@query
def get_all_item_revisions_by_origin_id(fire, item_id):
    results = fire(item_id)
    if not results:
        raise NotFoundError
    return [ItemRevision(**result) for result in results]


@query
def update_item_by_id(fire, user_id, item_id, name, description, quantity, unit):
    with transaction():
        result = fire(name, description, quantity, unit, item_id, autocommit=False)
        if not result["rowcount"]:
            raise NotFoundError
        create_item_revision(user_id, item_id, name, description, quantity, unit, False, autocommit=False)


@query
def delete_item_by_id(fire, item_id):
    # danger
    fire(item_id)


@query
def update_item_deletion_flag_by_id(fire, user_id, item_id):
    with transaction():
        # TODO race condition
        original = get_item_by_id(item_id)
        fire(item_id, autocommit=False)
        create_item_revision(
            user_id,
            item_id,
            original.name,
            original.description,
            original.quantity,
            original.unit,
            is_deleted=True,
            autocommit=False,
        )


@query
def create_item_comment(fire, user_id, item_id, text):
    with transaction():
        comment_id = fire(user_id, item_id, text, autocommit=False)["lastrowid"]
        create_item_comment_revision(user_id, comment_id, text, False, autocommit=False)
        return comment_id


@query
def get_item_comment_by_id(fire, item_comment_id):
    result = fire(item_comment_id)
    if not result:
        raise NotFoundError
    return ItemComment(**result)


@query
def update_item_comment_deletion_flag_by_id(fire, item_comment_id, user_id):
    with transaction():
        # TODO race condition
        original = get_item_comment_by_id(item_comment_id)
        fire(item_comment_id, autocommit=False)
        create_item_comment_revision(
            user_id,
            item_comment_id,
            original.text,
            is_deleted=True,
            autocommit=False,
        )


# @query
# def get_all_item_comments_by_item_id(fire, item_id):
#     results = fire(item_id)
#     return [ItemComment(**result, item_id=item_id) for result in results]


@query
def create_item_comment_revision(fire, editing_user_id, item_comment_id, text, is_deleted=False):
    now = datetime.now(timezone.utc)
    return fire(editing_user_id, now, item_comment_id, text, is_deleted)["lastrowid"]


@query
def get_all_item_comment_revisions_by_origin_id(fire, item_comment_id):
    results = fire(item_comment_id)
    return [ItemCommentRevision(**result) for result in results]


@query
def update_item_comment_by_id(fire, user_id, item_comment_id, text):
    with transaction():
        fire(text, item_comment_id, autocommit=False)
        create_item_comment_revision(user_id, item_comment_id, text, False, autocommit=False)


@query
def delete_item_comment_by_id(fire, item_comment_id):
    fire(item_comment_id)


@query
def create_item_tag(fire, name):
    return fire(name)["lastrowid"]


@query
def create_item_tag_association(fire, item_id, tag_id):
    fire(item_id, tag_id)


# TODO create way to remove tag associations


@query
def get_item_tag_by_name(fire, tag_name):
    result = fire(tag_name)
    if not result:
        raise NotFoundError
    return ItemTag(**result)


@query
def get_all_item_tags(fire):
    results = fire()
    return [ItemTag(*result.values()) for result in results]


# @query
# def get_all_item_tags_by_item_id(fire, item_id):
#     results = fire(item_id)
#     return [ItemTag(*result.values()) for result in results]


@query
def delete_item_tag_by_id(fire, tag_id):
    fire(tag_id)


@query
def delete_item_tag_association(fire, item_id, tag_id):
    fire(item_id, tag_id)
