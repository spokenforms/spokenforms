from __future__ import annotations

import re

from spokenforms.constants import WORD_DIGITS
from spokenforms.utils.text import digits_only


def normalize_number_sequence(value: str) -> str:
    lower = value.lower()
    tokens = re.findall(r"[a-z]+|\d", lower)
    result: list[str] = []
    for token in tokens:
        if token.isdigit():
            result.append(token)
        elif token in WORD_DIGITS:
            result.append(WORD_DIGITS[token])
    digits = "".join(result)
    return digits or digits_only(value)
