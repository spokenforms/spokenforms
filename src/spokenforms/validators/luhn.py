from __future__ import annotations


def luhn_checksum(number: str) -> int:
    digits = [int(char) for char in number if char.isdigit()]
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        value = digit
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10


def is_luhn_valid(number: str) -> bool:
    return bool(number) and luhn_checksum(number) == 0
