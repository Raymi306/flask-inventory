from dataclasses import asdict
from http import HTTPStatus

import pytest

from app.models.item import delete_item_by_id, get_all_items, get_item_by_id


class TestCreateItem:
    @staticmethod
    @pytest.mark.parametrize(
        "form_data, expected",
        (
            (
                {"name": "item", "description": None, "quantity": 0, "unit": None},
                {"name": "item", "description": None, "quantity": 0, "unit": None},
            ),
            (
                {"name": "item", "description": "description", "quantity": 1, "unit": "gallons"},
                {"name": "item", "description": "description", "quantity": 1, "unit": "gallons"},
            ),
            (
                {"name": "item"},
                {"name": "item", "description": None, "quantity": 0, "unit": None},
            ),
        ),
    )
    def test_success(client, new_authenticated_user, form_data, expected):
        with client:
            new_authenticated_user(client)
            response = client.post("/item/", data=form_data)
            assert response.status_code == HTTPStatus.OK
            item_id = response.json["id"]
            item = asdict(get_item_by_id(item_id))
            assert item.pop("id") == item_id
            assert item == expected
            delete_item_by_id(item_id)

    @staticmethod
    @pytest.mark.parametrize(
        "form_data",
        (
            {},
            {"description": "description", "quantity": 1, "unit": "gallons"},
            {"name": "item", "description": None, "quantity": -1, "unit": None},
        ),
    )
    def test_validation_failure(client, new_authenticated_user, form_data):
        with client:
            new_authenticated_user(client)
            response = client.post("/item/", data=form_data)
            assert response.status_code == HTTPStatus.BAD_REQUEST
            assert len(get_all_items()) == 0

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.post("/item/", data={"name": "item"})
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert len(get_all_items()) == 0
