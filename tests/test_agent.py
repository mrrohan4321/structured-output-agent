import sys
from pathlib import Path

# tests folder theke project root er file gulo import korar jonno
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validator import parse_and_validate

VALID = '{"name": "Rahul Das", "age": 21, "skills": ["Python", "SQL"], "email": "rahul@example.com"}'


def test_valid_input():
    profile, errors = parse_and_validate(VALID)
    assert errors == []
    assert profile.name == "Rahul Das"
    assert profile.age == 21


def test_fenced_json_is_accepted():
    profile, errors = parse_and_validate("```json\n" + VALID + "\n```")
    assert errors == []


def test_missing_optional_fields():
    profile, errors = parse_and_validate('{"name": "Rahul"}')
    assert errors == []
    assert profile.age is None
    assert profile.email is None
    assert profile.skills == []


def test_invalid_email():
    _, errors = parse_and_validate('{"name": "Rahul", "email": "not-an-email"}')
    assert errors


def test_wrong_type_age():
    _, errors = parse_and_validate('{"name": "Rahul", "age": "twenty-one"}')
    assert errors


def test_extra_field_rejected():
    _, errors = parse_and_validate('{"name": "Rahul", "phone": "123"}')
    assert errors


def test_malformed_json():
    _, errors = parse_and_validate("{bad json")
    assert errors and "Malformed" in errors[0]


def test_non_object_json():
    _, errors = parse_and_validate("[1, 2]")
    assert errors