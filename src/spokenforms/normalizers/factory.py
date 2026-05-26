from __future__ import annotations

from collections.abc import Callable

from spokenforms.models import OutputType
from spokenforms.normalizers.alphanumeric import normalize_alphanumeric
from spokenforms.normalizers.booleans import normalize_boolean
from spokenforms.normalizers.credit_card import normalize_credit_card
from spokenforms.normalizers.dates import normalize_date
from spokenforms.normalizers.enums import normalize_enum
from spokenforms.normalizers.names import normalize_name
from spokenforms.normalizers.numbers import normalize_number_sequence
from spokenforms.normalizers.ssn import normalize_ssn


def normalizer_for(entity_id: str, output_type: OutputType) -> Callable[[str], str]:
    if entity_id == "ssn":
        return normalize_ssn
    if entity_id == "credit_card_number":
        return normalize_credit_card
    if output_type is OutputType.ALPHANUMERIC:
        return normalize_alphanumeric
    if output_type is OutputType.BOOLEAN:
        return normalize_boolean
    if output_type in {OutputType.ENUM, OutputType.MULTI_SELECT_ENUM}:
        return normalize_enum
    if output_type is OutputType.DATE:
        return normalize_date
    if entity_id == "full_name":
        return normalize_name
    return normalize_number_sequence
