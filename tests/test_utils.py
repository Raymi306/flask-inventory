import pytest

from app.utils import camel_case_split


@pytest.mark.parametrize(
    "input_string, expected",
    (
        ("XYZCamelCase", ["XYZ", "Camel", "Case"]),
        ("CamelCaseXYZ", ["Camel", "Case", "XYZ"]),
        ("CamelCaseXYZa", ["Camel", "Case", "XY", "Za"]),
        ("XYZCamelCaseXYZ", ["XYZ", "Camel", "Case", "XYZ"]),
        ("CamelCaseWordT", ["Camel", "Case", "Word", "T"]),
        ("CamelCaseWordTa", ["Camel", "Case", "Word", "Ta"]),
        ("Ta", ["Ta"]),
        ("T", ["T"]),
        ("", []),
    ),
)
def test_camel_case_splitter(input_string, expected):
    assert camel_case_split(input_string) == expected
