from __future__ import annotations

from spokenforms.normalizers.numbers import normalize_number_sequence


def normalize_ssn(value: str) -> str:
    digits = normalize_number_sequence(value)
    if len(digits) == 9:
        return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
    return digits
