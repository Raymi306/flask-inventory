import pytest

from app.utils import snake_to_camel


@pytest.mark.parametrize(
    "input_string, expected",
    (
        ("foo_bar_baz", "FooBarBaz"),
        ("foo", "Foo"),
    ),
)
def test_snake_to_camel(input_string, expected):
    assert snake_to_camel(input_string) == expected
