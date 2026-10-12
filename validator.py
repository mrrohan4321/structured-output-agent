import json
import re

from pydantic import ValidationError

from schemas import ContactProfile

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_json(raw: str):
    """Returns (data, error). Markdown ``` fence thakle remove kore."""
    cleaned = _FENCE.sub("", raw.strip())
    try:
        return json.loads(cleaned), None
    except json.JSONDecodeError as exc:
        return None, f"Malformed JSON: {exc}"


def validate(data):
    """Returns (profile, errors)."""
    if not isinstance(data, dict):
        return None, ["Top-level JSON value must be an object."]
    try:
        return ContactProfile.model_validate(data), []
    except ValidationError as exc:
        errors = [
            f"{'.'.join(str(p) for p in e['loc']) or 'root'}: {e['msg']}"
            for e in exc.errors()
        ]
        return None, errors


def parse_and_validate(raw: str):
    data, err = parse_json(raw)
    if err:
        return None, [err]
    return validate(data)