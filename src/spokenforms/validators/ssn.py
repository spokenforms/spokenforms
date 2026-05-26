from __future__ import annotations

from spokenforms.utils.text import digits_only


def is_safe_synthetic_ssn(value: str) -> bool:
    digits = digits_only(value)
    if len(digits) != 9:
        return False
    area = digits[:3]
    group = digits[3:5]
    serial = digits[5:]
    return area in {"000", "666", "900", "999"} or group == "00" or serial == "0000"
