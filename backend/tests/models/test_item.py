from dataclasses import asdict
from unittest.mock import patch

import pytest
from pymysql.err import IntegrityError

from app.db import get_db_connection
from app.models.item import (
    create_item,
    create_item_comment,
    create_item_tag,
    create_item_tag_association,
    delete_item_by_id,
    delete_item_comment_by_id,
    delete_item_tag_association,
    delete_item_tag_by_id,
    get_all_item_comment_revisions_by_item_comment_id,
    get_all_item_revisions_by_item_id,
    get_all_item_tags,
    get_all_items,
    get_all_joined_items,
    get_item_by_id,
    get_joined_item_by_id,
    update_item_by_id,
    update_item_comment_by_id,
)


@pytest.fixture(autouse=True)
def clean(truncate_all):
    pass


class TestCreateItem:
    @staticmethod
    @pytest.mark.parametrize(
        "function_args, expected",
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
    def test_success(
        app,
        new_user,
        function_args,
        expected,
    ):
        with app.app_context():
            user_id = new_user()
            item_id = create_item(user_id, **function_args)

            item = asdict(get_item_by_id(item_id))
            assert item.pop("id") == item_id
            assert item == expected

            revisions = get_all_item_revisions_by_item_id(item_id)
            assert len(revisions) == 1
            revision = asdict(revisions[0])
            assert revision["_user_id"] == user_id
            assert revision["id"] == item_id

            delete_item_by_id(item_id)

    @staticmethod
    def test_unique_constraints(app, new_user, new_item):
        with app.app_context():
            user_id = new_user()
            new_item(user_id, "duplicate")
            with pytest.raises(IntegrityError):
                create_item(user_id, "duplicate")

    @staticmethod
    def test_transaction_integrity(app, new_user):
        with app.app_context():
            user_id = new_user()

            with (
                pytest.raises(RuntimeError),
                patch("app.models.item.item.create_item_revision") as mock_func,
            ):
                mock_func.side_effect = RuntimeError("Induced failure.")
                create_item(user_id, "name")

            assert len(get_all_items()) == 0


class TestUpdateItemById:
    @staticmethod
    def test_success(
        app,
        new_user,
        new_item,
    ):
        initial_item = {
            "name": "initial_name",
            "description": "initial_description",
            "quantity": 0,
            "unit": "initial_unit",
        }
        with app.app_context():
            user_id = new_user()
            item_id = new_item(user_id, **initial_item)
            expected_item = {
                "name": "updated_name",
                "description": "updated_description",
                "quantity": 1,
                "unit": "updated_unit",
            }
            update_item_by_id(user_id, item_id, **expected_item)
            item = asdict(get_item_by_id(item_id))
            id_ = item.pop("id")
            assert id_
            assert item == expected_item

            revisions = get_all_item_revisions_by_item_id(item_id)
            assert len(revisions) == 2

            previous = asdict(revisions[0])
            assert previous.pop("_user_id") == user_id
            assert previous.pop("id") == item_id
            assert previous.pop("_id")
            assert previous.pop("_datetime")
            assert previous == initial_item

            current = asdict(revisions[1])
            assert current.pop("_user_id") == user_id
            assert current.pop("id") == item_id
            assert current.pop("_id")
            assert current.pop("_datetime")
            assert current == expected_item

            delete_item_by_id(item_id)

    @staticmethod
    def test_transaction_integrity(
        app,
        new_user,
        new_item,
    ):
        with app.app_context():
            # with broken transactions, the error:
            # Record has changed since last read in table 'item'
            # was reproducible here by adding a "get" retrieval as below:
            assert not get_all_items()
            expected_item = {
                "name": "initial_name",
                "description": "description",
                "quantity": 1,
                "unit": "unit",
            }
            user_id = new_user()
            item_id = new_item(user_id, **expected_item)

            with (
                pytest.raises(RuntimeError),
                patch("app.models.item.item.create_item_revision") as mock_func,
            ):
                mock_func.side_effect = RuntimeError("Induced failure.")
                expected_item["name"] = "updated_name"
                update_item_by_id(user_id, item_id, **expected_item)

            assert asdict(get_item_by_id(item_id))["name"] == "initial_name"


def test_delete_item_by_id(
    app,
    new_user,
    new_item,
):
    with app.app_context():
        user_id = new_user()
        item_id = new_item(user_id)
        assert get_item_by_id(item_id) is not None
        delete_item_by_id(item_id)
        assert get_item_by_id(item_id) is None


def test_get_joined_item_by_id(
    app,
    new_user,
    new_item,
    new_item_comment,
    new_item_tag,
    new_item_tag_association,
):
    with app.app_context():
        user_id = new_user()
        item_id = new_item(user_id)
        comment_1_id = new_item_comment(user_id, item_id, "comment1")
        comment_2_id = new_item_comment(user_id, item_id, "comment2")
        tag_1_id = new_item_tag(user_id, "tag1")
        tag_2_id = new_item_tag(user_id, "tag2")
        new_item_tag_association(item_id, tag_1_id)
        new_item_tag_association(item_id, tag_2_id)
        result = get_joined_item_by_id(item_id)
        assert result.id == item_id
        assert len(result.comments) == 2
        assert result.comments[0].id == comment_1_id
        assert result.comments[1].id == comment_2_id
        assert len(result.tags) == 2
        assert result.tags[0].id == tag_1_id
        assert result.tags[1].id == tag_2_id
        assert not result.has_revisions


def test_get_all_joined_items(
    app,
    new_user,
    new_item,
    new_item_comment,
    new_item_tag,
    new_item_tag_association,
):
    with app.app_context():
        user_id = new_user()

        tag_1_id = new_item_tag(user_id, "tag1")
        tag_2_id = new_item_tag(user_id, "tag2")
        tag_3_id = new_item_tag(user_id, "tag3")

        item_1_id = new_item(user_id, "item1")

        expected_item = {
            "name": "updated_name",
            "description": "updated_description",
            "quantity": 1,
            "unit": "updated_unit",
        }

        # introduce a revision to item 1
        update_item_by_id(user_id, item_1_id, **expected_item)

        comment_1_id = new_item_comment(user_id, item_1_id, "comment1")

        # introduce a revision to comment 1
        update_item_comment_by_id(user_id, comment_1_id, "updated_text")

        new_item_comment(user_id, item_1_id, "comment2")
        new_item_tag_association(item_1_id, tag_1_id)
        new_item_tag_association(item_1_id, tag_2_id)

        item_2_id = new_item(user_id, "item2")
        new_item_comment(user_id, item_2_id, "comment3")
        new_item_tag_association(item_2_id, tag_2_id)
        new_item_tag_association(item_2_id, tag_3_id)

        result = get_all_joined_items()

        assert result[0].id == item_1_id
        assert len(result[0].tags) == 2
        assert len(result[0].comments) == 2
        assert result[0].has_revisions
        assert result[0].comments[0].has_revisions

        assert result[1].id == item_2_id
        assert len(result[1].tags) == 2
        assert len(result[1].comments) == 1


class TestCreateItemComment:
    @staticmethod
    def test_success(app, new_item, new_user):
        text = "a fancy comment"
        with app.app_context():
            user_id = new_user()
            item_id = new_item(user_id)
            expected_item_comment = {
                "user_id": user_id,
                "item_id": item_id,
                "text": text,
            }
            create_item_comment(**expected_item_comment)

            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
                item_comment = cursor.fetchone()
                item_comment_id = item_comment.pop("id")
                assert item_comment.pop("is_deleted") == 0
                assert item_comment == expected_item_comment

                revisions = get_all_item_comment_revisions_by_item_comment_id(item_comment_id)
                assert len(revisions) == 1
                revision = asdict(revisions[0])
                assert revision["_user_id"] == user_id
                assert revision["id"] == item_comment_id

            delete_item_comment_by_id(item_comment_id)

    @staticmethod
    def test_transaction_integrity(app, new_item, new_user):
        text = "a fancy comment"
        with app.app_context():
            user_id = new_user()
            item_id = new_item(user_id)

            with (
                pytest.raises(RuntimeError),
                patch("app.models.item.item.create_item_comment_revision") as mock_func,
            ):
                mock_func.side_effect = RuntimeError("Induced failure.")
                create_item_comment(user_id, item_id, text)

            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
                item_comment = cursor.fetchone()
                assert item_comment is None


class TestUpdateItemCommentById:
    @staticmethod
    def test_success(
        app,
        new_user,
        new_item,
        new_item_comment,
    ):
        with app.app_context():
            user_id = new_user()
            item_id = new_item(user_id)
            item_comment_id = new_item_comment(user_id, item_id, "initial")
            update_item_comment_by_id(user_id, item_comment_id, "updated")

            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
                item_comment = cursor.fetchone()
                assert item_comment["text"] == "updated"

            revisions = get_all_item_comment_revisions_by_item_comment_id(item_comment_id)
            assert len(revisions) == 2

            previous = asdict(revisions[0])
            assert previous.pop("_user_id") == user_id
            assert previous.pop("id") == item_comment_id
            assert previous.pop("_id")
            assert previous.pop("_datetime")
            assert previous["text"] == "initial"

            current = asdict(revisions[1])
            assert current.pop("_user_id") == user_id
            assert current.pop("id") == item_comment_id
            assert current.pop("_id")
            assert current.pop("_datetime")
            assert current["text"] == "updated"

    @staticmethod
    def test_transaction_integrity(
        app,
        new_user,
        new_item,
        new_item_comment,
    ):
        with app.app_context():
            user_id = new_user()
            item_id = new_item(user_id)
            item_comment_id = new_item_comment(user_id, item_id, "initial")

            with (
                pytest.raises(RuntimeError),
                patch("app.models.item.item.create_item_comment_revision") as mock_func,
            ):
                mock_func.side_effect = RuntimeError("Induced failure.")
                update_item_comment_by_id(user_id, item_comment_id, "updated")

            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
                item_comment = cursor.fetchone()
                assert item_comment["text"] == "initial"


def test_delete_item_comment_by_id(
    app,
    new_user,
    new_item,
    new_item_comment,
):
    with app.app_context():
        user_id = new_user()
        item_id = new_item(user_id)
        item_comment_id = new_item_comment(user_id, item_id, "initial")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
            assert cursor.fetchone() is not None
            delete_item_comment_by_id(item_comment_id)
            cursor.execute("SELECT * FROM item_comment WHERE item_id = %s", (item_id,))
            assert cursor.fetchone() is None


def test_create_item_tag(app):
    tag_name = "tag"
    with app.app_context():
        tag_id = create_item_tag(tag_name)
        tags = get_all_item_tags()
        assert len(tags) == 1
        assert tags[0].name == tag_name
        delete_item_tag_by_id(tag_id)


def test_create_item_tag_association(app, new_user, new_item, new_item_tag):
    tag_name = "tag"
    with app.app_context():
        user_id = new_user()
        item_id = new_item(user_id)
        tag_id = new_item_tag(tag_name)
        create_item_tag_association(item_id, tag_id)
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT item_id, item_tag_id FROM item_tag_junction")
            results = cursor.fetchall()
            assert len(results) == 1
            assert results[0]["item_id"] == item_id
            assert results[0]["item_tag_id"] == tag_id
        delete_item_tag_association(item_id, tag_id)
