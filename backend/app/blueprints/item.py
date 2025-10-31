from http import HTTPStatus
from typing import Annotated

from flask import Blueprint, g, request
from pydantic import BaseModel, Field
from pymysql.err import IntegrityError

from app.blueprints.utils import login_required
from app.db import NotFoundError
from app.models.item import (
    create_item,
    create_item_tag,
    create_item_tag_association,
    get_all_item_tags,
    get_all_item_comment_revisions_by_origin_id,
    get_all_item_revisions_by_origin_id,
    get_all_joined_items,
    get_item_tag_by_name,
    get_joined_item_by_id,
    update_item_by_id,
    update_item_deletion_flag_by_id,
)

blueprint = Blueprint("item", __name__, url_prefix="/item")


class ItemForm(BaseModel):
    name: str
    description: str | None = None
    quantity: Annotated[int, Field(ge=0, default=0)]
    unit: str | None = None


@blueprint.post("/")
@login_required
def create_item_():
    form = ItemForm(**request.form)
    item_id = create_item(g.user["id"], *form.model_dump().values())
    return {"id": item_id}


@blueprint.get("/")
@login_required
def get_items():
    return get_all_joined_items()


@blueprint.get("/<item_id>")
@login_required
def get_item(item_id):
    return get_joined_item_by_id(item_id)


@blueprint.put("/<item_id>")
@login_required
def update_item(item_id):
    form = ItemForm(**request.form)
    update_item_by_id(g.user["id"], item_id, *form.model_dump().values())
    return ("", HTTPStatus.NO_CONTENT)


@blueprint.delete("/<item_id>")
@login_required
def delete_item(item_id):
    update_item_deletion_flag_by_id(g.user["id"], item_id)
    return ("", HTTPStatus.NO_CONTENT)


class ItemTagForm(BaseModel):
    name: str


@blueprint.post("/<item_id>/tags/")
@login_required
def create_item_tag_(item_id):
    form = ItemTagForm(**request.form)

    try:
        tag = get_item_tag_by_name(form.name)
    except NotFoundError:
        item_tag_id = create_item_tag(*form.model_dump().values())
    else:
        item_tag_id = tag.id

    try:
        create_item_tag_association(item_id, item_tag_id)
    except IntegrityError as err:
        if "FOREIGN KEY" in str(err):
            return ("", HTTPStatus.NOT_FOUND)

    return {"id": item_tag_id}


@blueprint.get("/tags/")
@login_required
def get_item_tags():
    return get_all_item_tags()


@blueprint.get("/<item_id>/revision/")
@login_required
def get_item_revisions(item_id):
    return get_all_item_revisions_by_origin_id(item_id)


@blueprint.get("/<item_id>/comments/<comment_id>/revision/")
@login_required
def get_item_comment_revisions(comment_id):
    return get_all_item_comment_revisions_by_origin_id(comment_id)
