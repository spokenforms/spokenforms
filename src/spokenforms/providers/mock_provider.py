from __future__ import annotations

from spokenforms.constants import DIGIT_WORDS
from spokenforms.models import EntitySpec, ProviderName, VerbalizationPattern
from spokenforms.providers.base import LLMProvider
from spokenforms.validators.credit_card import PAYMENT_TEST_NUMBERS

SSN_VALUES: tuple[str, ...] = (
    "900-12-3456",
    "999-45-6789",
    "000-12-3456",
    "666-22-3333",
    "123-00-4567",
    "123-45-0000",
)


class MockProvider(LLMProvider):
    name = ProviderName.MOCK
    model = "mock"

    def generate_values(self, entity: EntitySpec, count: int) -> list[str]:
        values = self._values_for(entity.entity_id)
        return [values[index % len(values)] for index in range(count)]

    def generate_transcript(
        self,
        entity: EntitySpec,
        value: str,
        pattern: VerbalizationPattern,
        attempt: int,
    ) -> str:
        spoken = _spoken_digits(value)
        grouped = _spoken_grouped(value, _groups_for(entity.entity_id, value))
        pattern_id = pattern.pattern_id
        if "correction" in pattern_id:
            return _vary(f"{_wrong_first_digit(value)}, sorry, {grouped}.", attempt)
        if "repetition" in pattern_id:
            return _vary(f"{grouped}, again that is {grouped}.", attempt)
        if pattern_id in {"filler_words", "hesitation"}:
            return _vary(f"Um, it is {grouped}.", attempt)
        if pattern_id == "formal":
            return _vary(f"The {entity.field_name} is {grouped}.", attempt)
        if pattern_id == "casual":
            return _vary(f"Yeah, {grouped}.", attempt)
        if pattern_id == "polite":
            return _vary(f"Sure, it is {grouped}.", attempt)
        if pattern_id == "uncertain":
            return _vary(f"I believe it is {grouped}.", attempt)
        if pattern_id in {"digit_by_digit", "ssn_digit_by_digit", "card_digit_by_digit"}:
            return _vary(spoken, attempt)
        if pattern_id in {"ssn_with_dashes", "card_with_spaces"}:
            separator = " dash " if entity.entity_id == "ssn" else " space "
            return _vary(
                separator.join(_spoken_groups(value, _groups_for(entity.entity_id, value))), attempt
            )
        if pattern_id == "card_last_four_repetition":
            return _vary(f"{grouped}, last four are {_spoken_digits(value[-4:])}.", attempt)
        if pattern_id == "confirmation":
            return _vary(f"{grouped}, that is correct.", attempt)
        return _vary(grouped, attempt)

    def _values_for(self, entity_id: str) -> tuple[str, ...]:
        if entity_id == "ssn":
            return SSN_VALUES
        if entity_id == "credit_card_number":
            return PAYMENT_TEST_NUMBERS
        if entity_id == "zip_code":
            return ("94101", "10001", "60601", "30301", "98101")
        if entity_id == "boolean_answer":
            return ("yes", "no")
        if entity_id == "date_of_birth":
            return ("01-02-1985", "12-31-1970", "07-04-1999")
        if entity_id == "full_name":
            return ("Jane Smith", "Alex Johnson", "Sam Rivera")
        return ("AB123", "ZX902", "MN456", "A1B2C3", "778899")


def _groups_for(entity_id: str, value: str) -> list[int]:
    digits = "".join(char for char in value if char.isdigit())
    if entity_id == "ssn":
        return [3, 2, 4]
    if entity_id == "credit_card_number" and len(digits) == 15:
        return [4, 6, 5]
    if entity_id == "credit_card_number":
        return [4, 4, 4, 4, 3]
    return [1] * len(digits)


def _spoken_digits(value: str) -> str:
    pieces = [DIGIT_WORDS[char] for char in value if char.isdigit()]
    return " ".join(pieces)


def _spoken_groups(value: str, groups: list[int]) -> list[str]:
    digits = "".join(char for char in value if char.isdigit())
    result: list[str] = []
    offset = 0
    for size in groups:
        chunk = digits[offset : offset + size]
        if chunk:
            result.append(_spoken_digits(chunk))
        offset += size
    if offset < len(digits):
        result.append(_spoken_digits(digits[offset:]))
    return result


def _spoken_grouped(value: str, groups: list[int]) -> str:
    return ", ".join(_spoken_groups(value, groups))


def _wrong_first_digit(value: str) -> str:
    digits = "".join(char for char in value if char.isdigit())
    if not digits:
        return "sorry"
    wrong = "1" if digits[0] != "1" else "2"
    return _spoken_digits(wrong + digits[1:3])


def _vary(transcript: str, attempt: int) -> str:
    if attempt == 1:
        return transcript
    return f"{transcript} That's it."
