from __future__ import annotations

from spokenforms.utils.text import digits_only
from spokenforms.validators.luhn import is_luhn_valid

PAYMENT_TEST_NUMBERS: tuple[str, ...] = (
    "4242424242424242",
    "4000056655665556",
    "5555555555554444",
    "378282246310005",
    "6011111111111117",
)


def is_payment_test_number(value: str) -> bool:
    return digits_only(value) in PAYMENT_TEST_NUMBERS


def is_safe_synthetic_card(value: str) -> bool:
    digits = digits_only(value)
    return is_payment_test_number(digits) and is_luhn_valid(digits)
