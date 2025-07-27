from dataclasses import asdict
from http import HTTPStatus

import pytest

from app.models.item import delete_item_by_id, get_all_items, get_item_by_id


@pytest.fixture(autouse=True)
def clean(truncate_all):
    pass


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


class TestGetItems:
    @staticmethod
    def test_success_with_content(
        client,
        new_authenticated_user,
        new_item,
        new_item_comment,
        new_item_tag,
        new_item_tag_association,
    ):
        with client:
            user_id = new_authenticated_user(client)
            tag_1_id = new_item_tag(user_id, "tag1")
            tag_2_id = new_item_tag(user_id, "tag2")
            tag_3_id = new_item_tag(user_id, "tag3")

            item_1_id = new_item(user_id, "item1")
            new_item_comment(user_id, item_1_id, "comment1")
            new_item_comment(user_id, item_1_id, "comment2")
            new_item_tag_association(item_1_id, tag_1_id)
            new_item_tag_association(item_1_id, tag_2_id)

            item_2_id = new_item(user_id, "item2")
            new_item_comment(user_id, item_2_id, "comment3")
            new_item_tag_association(item_2_id, tag_2_id)
            new_item_tag_association(item_2_id, tag_3_id)
            response = client.get("/item/")
            assert response.status_code == HTTPStatus.OK

            result = response.json
            assert result[0]["id"] == item_1_id
            assert len(result[0]["tags"]) == 2
            assert len(result[0]["comments"]) == 2

            assert result[1]["id"] == item_2_id
            assert len(result[1]["tags"]) == 2
            assert len(result[1]["comments"]) == 1

    @staticmethod
    def test_success_without_content(
        client,
        new_authenticated_user,
    ):
        with client:
            new_authenticated_user(client)
            response = client.get("/item/")
            assert response.status_code == HTTPStatus.OK
            assert len(response.json) == 0

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.get("/item/")
            assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestGetItemTags:
    @staticmethod
    def test_success_with_content(
        client,
        new_authenticated_user,
        new_item_tag,
    ):
        with client:
            user_id = new_authenticated_user(client)
            new_item_tag(user_id, "tag1")
            new_item_tag(user_id, "tag2")
            new_item_tag(user_id, "tag3")

            response = client.get("/item/tags/")
            assert response.status_code == HTTPStatus.OK

            result = response.json
            assert len(result) == 3

    @staticmethod
    def test_success_without_content(
        client,
        new_authenticated_user,
    ):
        with client:
            new_authenticated_user(client)
            response = client.get("/item/tags/")
            assert response.status_code == HTTPStatus.OK
            assert len(response.json) == 0

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.get("/item/tags/")
            assert response.status_code == HTTPStatus.UNAUTHORIZED
