from solution import slugify


def test_normalizes_case_and_punctuation():
    assert slugify("Hello, World!") == "hello-world"


def test_collapses_whitespace_and_trims():
    assert slugify("  A   B  ") == "a-b"


def test_ignores_non_ascii_characters():
    assert slugify("café 東京") == "caf"


def test_empty_input():
    assert slugify("!!!") == ""
