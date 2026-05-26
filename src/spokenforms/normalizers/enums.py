from __future__ import annotations

from spokenforms.utils.text import compact_spaces


def normalize_enum(value: str) -> str:
    return compact_spaces(value).lower()
