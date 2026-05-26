from __future__ import annotations

from spokenforms.normalizers.numbers import normalize_number_sequence


def normalize_credit_card(value: str) -> str:
    return normalize_number_sequence(value)
