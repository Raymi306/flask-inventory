from typing import Annotated

from flask import Blueprint, g, request
from pydantic import BaseModel, Field

from app.blueprints.utils import login_required
from app.models.item import (
    create_item,
)

blueprint = Blueprint("item", __name__, url_prefix="/item")


class CreateItemForm(BaseModel):
    name: str
    description: str | None = None
    quantity: Annotated[int, Field(ge=0, default=0)]
    unit: str | None = None


@blueprint.post("/")
@login_required
def create_item_view():
    form = CreateItemForm(**request.form)
    item_id = create_item(g.user["id"], *form.model_dump().values())
    return {"id": item_id}


@blueprint.get("/")
@login_required
def get_items():
    pass
