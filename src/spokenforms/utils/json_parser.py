from __future__ import annotations

from typing import Any

import orjson


def parse_json_object(text: str) -> dict[str, Any]:
    parsed = orjson.loads(text)
    if not isinstance(parsed, dict):
        msg = "Expected a JSON object."
        raise ValueError(msg)
    return parsed


def dump_json_line(value: object) -> str:
    return orjson.dumps(value, option=orjson.OPT_APPEND_NEWLINE).decode("utf-8")
