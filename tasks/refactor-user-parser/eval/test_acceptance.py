import pytest
from solution import parse_user


def test_parses_and_normalizes_fields():
    assert parse_user("42,  Ada Lovelace  , ADA@EXAMPLE.COM ") == {
        "id": 42, "name": "Ada Lovelace", "email": "ada@example.com"
    }


@pytest.mark.parametrize("record", ["1,Ada", "1,Ada,a@b,c", "x,Ada,a@b", "1, ,a@b", "1,Ada, "])
def test_rejects_invalid_records(record):
    with pytest.raises(ValueError):
        parse_user(record)
