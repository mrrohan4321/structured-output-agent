import sys
from pathlib import Path

# tests folder theke project root er file gulo import korar jonno
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validator import parse_and_validate

from agent import extract


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

def fake_llm(*replies):
    """Fake LLM: replies gulo ek ek kore dey, kotobar call hoyeche gune."""
    calls = {"n": 0}

    def llm(messages):
        reply = replies[min(calls["n"], len(replies) - 1)]
        calls["n"] += 1
        return reply

    llm.calls = calls
    return llm


def test_extract_success():
    res = extract("some text", llm=fake_llm(VALID))
    assert res.ok and res.attempts == 1
    assert res.data["name"] == "Rahul Das"


def test_retry_recovers():
    res = extract("some text", llm=fake_llm("{bad json", VALID))
    assert res.ok and res.attempts == 2


def test_retry_exhaustion():
    llm = fake_llm("{bad json")
    res = extract("some text", llm=llm, max_attempts=3)
    assert not res.ok
    assert res.attempts == 3
    assert llm.calls["n"] == 3


def test_empty_input():
    res = extract("   ", llm=fake_llm(VALID))
    assert not res.ok


def test_api_failure_handled():
    def boom(messages):
        raise RuntimeError("rate limited")

    res = extract("x", llm=boom)
    assert not res.ok and "rate limited" in res.errors[0]