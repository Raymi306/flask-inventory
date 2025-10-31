from dataclasses import asdict
from http import HTTPStatus

import pytest

from app.models.item import delete_item_by_id, get_all_items, get_item_by_id


@pytest.fixture(autouse=True)
def clean(truncate_all):
    pass


# TODO / NOTE:
# would be interesting to have mixins or inheritance to guarantee certain things get tests
# TODO maybe test CRUD operations in a suite together
# TODO move sql files away from py files, get rid of stupid init files in model packages
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


class TestUpdateItem:
    @staticmethod
    def test_success(
        client,
        new_authenticated_user,
        new_item,
    ):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            item = client.get(f"/item/{item_id}").json
            item["description"] = "updated description"
            assert item.pop("has_revisions") == False

            response = client.put(
                f"/item/{item_id}",
                data=item,
            )
            assert response.status_code == HTTPStatus.NO_CONTENT

            updated_item = client.get(f"/item/{item_id}").json
            assert updated_item.pop("has_revisions") == True
            assert updated_item == item

    @staticmethod
    def test_not_found(
        client,
        new_authenticated_user,
        new_item,
    ):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            item = client.get(f"/item/{item_id}").json

            response = client.put(
                f"/item/{item_id + 1}",
                data=item,
            )
            assert response.status_code == HTTPStatus.NOT_FOUND

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.put("/item/1")
            assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestDeleteItem:
    @staticmethod
    def test_success(client, new_authenticated_user, new_item):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            assert client.get(f"/item/{item_id}").json
            response = client.delete(
                f"/item/{item_id}",
            )
            assert response.status_code == HTTPStatus.NO_CONTENT
            assert client.get(f"/item/{item_id}").status_code == HTTPStatus.NOT_FOUND
            # idempotence
            response = client.delete(
                f"/item/{item_id}",
            )
            assert response.status_code == HTTPStatus.NO_CONTENT

    @staticmethod
    def test_not_found(client, new_authenticated_user, new_item):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            assert client.get(f"/item/{item_id}").json
            response = client.delete(
                f"/item/{item_id + 1}",
            )
            assert response.status_code == HTTPStatus.NOT_FOUND
            assert client.get(f"/item/{item_id}").json

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.delete("/item/1")
            assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestGetItemRevisions:
    @staticmethod
    def test_success(client, new_authenticated_user, new_item):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            assert len(client.get(f"/item/{item_id}/revision/").json) == 1
            response = client.delete(
                f"/item/{item_id}",
            )
            assert len(client.get(f"/item/{item_id}/revision/").json) == 2

    @staticmethod
    def test_not_found(client, new_authenticated_user):
        with client:
            user_id = new_authenticated_user(client)
            assert client.get(f"/item/1/revision/").status_code == HTTPStatus.NOT_FOUND

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.get("/item/1/revision/")
            assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestCreateItemTag:
    @staticmethod
    def test_success(client, new_authenticated_user, new_item):
        with client:
            user_id = new_authenticated_user(client)
            item_id = new_item(user_id)
            assert not client.get(f"/item/{item_id}").json["tags"]
            response = client.post(
                f"/item/{item_id}/tags/",
                data={"name": "foo"},
            )
            assert response.status_code == HTTPStatus.OK
            assert len(client.get(f"/item/{item_id}").json["tags"]) == 1
            response = client.post(
                f"/item/{item_id}/tags/",
                data={"name": "foo"},
            )
            assert response.status_code == HTTPStatus.OK
            assert len(client.get(f"/item/{item_id}").json["tags"]) == 1

    @staticmethod
    def test_not_found(client, new_authenticated_user):
        with client:
            user_id = new_authenticated_user(client)
            assert client.post(f"/item/1/tags/", data={"name": "foo"}).status_code == HTTPStatus.NOT_FOUND

    @staticmethod
    def test_unauthenticated(client):
        with client:
            response = client.post("/item/1/tags/")
            assert response.status_code == HTTPStatus.UNAUTHORIZED

