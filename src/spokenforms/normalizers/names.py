from __future__ import annotations

from spokenforms.utils.text import compact_spaces


def normalize_name(value: str) -> str:
    return compact_spaces(value).title()
