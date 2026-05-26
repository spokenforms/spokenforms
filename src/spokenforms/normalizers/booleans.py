from __future__ import annotations


def normalize_boolean(value: str) -> str:
    lower = value.strip().lower()
    if lower in {"yes", "yeah", "y", "true", "correct"}:
        return "true"
    if lower in {"no", "nope", "n", "false", "incorrect"}:
        return "false"
    return lower
