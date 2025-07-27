from dataclasses import astuple, dataclass
from datetime import datetime, timezone
from itertools import groupby

from app.db import transaction
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
def create_item_revision(fire, user_id, item_id, name, description, quantity, unit, is_deleted):
    now = datetime.now(timezone.utc)
    return fire(user_id, now, item_id, name, description, quantity, unit)["lastrowid"]


@query
def get_item_by_id(fire, item_id):
    result = fire(item_id)
    if result is not None:
        return Item(*result.values())
    return result


def get_joined_item_by_id(item_id):
    # discuss compromises
    item = get_item_by_id(item_id)
    comments = get_all_item_comments_by_item_id(item_id)
    tags = get_all_item_tags_by_item_id(item_id)
    revisions = get_all_item_revisions_by_item_id(item_id)
    final = ItemFull(*astuple(item), comments, tags, len(revisions) > 1)
    return final


@query
def get_all_joined_items(fire):
    # discuss compromises, cartesian product

    grouped = groupby(fire(), lambda row: row["id"])

    items = []
    for item_id, group in grouped:
        tags = {}
        comments = {}
        for row in group:
            tags[row["tag_id"]] = ItemTag(
                row["tag_id"],
                row["tag_name"],
            )
            comments[row["comment_id"]] = ItemCommentFull(
                row["comment_id"],
                row["comment_user_id"],
                item_id,
                row["comment_text"],
                bool(row["item_comment_has_revisions"]),
            )
        items.append(
            ItemFull(
                item_id,
                row["name"],
                row["description"],
                row["quantity"],
                row["unit"],
                list(comments.values()),
                list(tags.values()),
                bool(row["item_has_revisions"]),
            )
        )
    return items


@query
def get_all_items(fire):
    results = fire()
    return [Item(*result.values()) for result in results]


@query
def get_all_item_revisions_by_item_id(fire, item_id):
    results = fire(item_id)
    return [ItemRevision(*result.values()) for result in results]


@query
def update_item_by_id(fire, user_id, item_id, name, description, quantity, unit):
    with transaction():
        fire(name, description, quantity, unit, item_id, autocommit=False)
        create_item_revision(user_id, item_id, name, description, quantity, unit, False, autocommit=False)


@query
def delete_item_by_id(fire, item_id):
    # danger
    fire(item_id)


@query
def update_item_deletion_flag_by_id(fire, item_id):
    # TODO manage the revisions
    fire(item_id)


@query
def create_item_comment(fire, user_id, item_id, text):
    with transaction():
        comment_id = fire(user_id, item_id, text, autocommit=False)["lastrowid"]
        create_item_comment_revision(user_id, comment_id, text, False, autocommit=False)
        return comment_id


@query
def update_item_comment_deletion_flag_by_id(fire, item_id):
    # TODO manage the revisions
    fire(item_id)


@query
def get_all_item_comments_by_item_id(fire, item_id):
    results = fire(item_id)
    return [ItemComment(**result, item_id=item_id) for result in results]


@query
def create_item_comment_revision(fire, editing_user_id, item_comment_id, text, is_deleted):
    now = datetime.now(timezone.utc)
    return fire(editing_user_id, now, item_comment_id, text, is_deleted)["lastrowid"]


# TODO rename, by_origin_id
@query
def get_all_item_comment_revisions_by_item_comment_id(fire, item_comment_id):
    results = fire(item_comment_id)
    return [ItemCommentRevision(*result.values()) for result in results]


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


@query
def get_all_item_tags(fire):
    results = fire()
    return [ItemTag(*result.values()) for result in results]


@query
def get_all_item_tags_by_item_id(fire, item_id):
    results = fire(item_id)
    return [ItemTag(*result.values()) for result in results]


@query
def delete_item_tag_by_id(fire, tag_id):
    fire(tag_id)


@query
def delete_item_tag_association(fire, item_id, tag_id):
    fire(item_id, tag_id)
