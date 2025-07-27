from typing import Annotated

from flask import Blueprint, g, request
from pydantic import BaseModel, Field

from app.blueprints.utils import login_required
from app.models.item import (
    create_item,
    create_item_tag,
    get_all_item_tags,
    get_all_item_comment_revisions_by_item_comment_id,
    get_all_item_revisions_by_item_id,
    get_all_joined_items,
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


@blueprint.put("/<item_id>")
@login_required
def update_item(item_id):
    form = ItemForm(**request.form)
    update_item_by_id(g.user["id"], item_id, *form.model_dump().values())
    # returns 204?


@blueprint.delete("/<item_id>")
@login_required
def delete_item(item_id):
    # TODO should flag items rather than actually delete
    update_item_deletion_flag_by_id(item_id)
    return {"id": item_id}


class ItemTagForm(BaseModel):
    name: str


@blueprint.post("/tags/")
@login_required
def create_item_tag_():
    form = ItemTagForm(**request.form)
    item_tag_id = create_item_tag(g.user["id"], *form.model_dump().values())
    return {"id": item_tag_id}


@blueprint.get("/tags/")
@login_required
def get_item_tags():
    return get_all_item_tags()


@blueprint.get("/<item_id>/revision/")
@login_required
def get_item_revisions(item_id):
    return get_all_item_revisions_by_item_id(item_id)


@blueprint.get("/comments/<comment_id>/revision/")
@login_required
def get_item_comment_revisions(comment_id):
    return get_all_item_comment_revisions_by_item_comment_id(comment_id)
