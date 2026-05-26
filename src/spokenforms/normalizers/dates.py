from __future__ import annotations

from spokenforms.utils.text import compact_spaces


def normalize_date(value: str) -> str:
    return compact_spaces(value)
