from __future__ import annotations

from spokenforms.models import VerbalizationPattern


def _general(pattern_id: str, instruction: str) -> VerbalizationPattern:
    return VerbalizationPattern(pattern_id=pattern_id, scope="general", instruction=instruction)


def _entity(
    pattern_id: str, entity_id: str, instruction: str, example: str
) -> VerbalizationPattern:
    return VerbalizationPattern(
        pattern_id=pattern_id,
        scope="entity_specific",
        entity_ids=[entity_id],
        category=entity_id,
        instruction=instruction,
        example=example,
    )


def built_in_patterns() -> list[VerbalizationPattern]:
    general = [
        _general("direct_and_simple", "Answer directly with the value."),
        _general("filler_words", "Add light filler words while preserving the value."),
        _general("hesitation", "Add a short hesitation while preserving the value."),
        _general("correction", "Include a correction and end with the correct value."),
        _general("repetition", "Repeat the value for confirmation."),
        _general("formal", "Use formal phrasing."),
        _general("casual", "Use casual phrasing."),
        _general("polite", "Use polite phrasing."),
        _general("confident", "Use confident phrasing."),
        _general("uncertain", "Use uncertain phrasing while still giving the value."),
        _general("confirmation", "Give the value and confirm it."),
        _general("digit_by_digit", "Read each digit separately."),
        _general("grouped_two", "Read digits in groups of two."),
        _general("grouped_four", "Read digits in groups of four."),
        _general("nato_letters", "Spell letters with NATO words when letters are present."),
    ]
    return [
        *general,
        _entity(
            "ssn_grouped_3_2_4",
            "ssn",
            "Say the SSN in 3-2-4 grouping.",
            "nine zero zero, one two, three four five six",
        ),
        _entity(
            "ssn_digit_by_digit",
            "ssn",
            "Say every SSN digit separately.",
            "nine zero zero one two three four five six",
        ),
        _entity(
            "ssn_with_dashes",
            "ssn",
            "Include spoken dash separators.",
            "nine zero zero dash one two dash three four five six",
        ),
        _entity(
            "ssn_correction",
            "ssn",
            "Include a self-correction.",
            "nine zero one, sorry, nine zero zero, one two, three four five six",
        ),
        _entity(
            "ssn_repetition_for_confirmation",
            "ssn",
            "Repeat one group for confirmation.",
            "nine zero zero, one two, one two, three four five six",
        ),
        _entity(
            "card_grouped_4_4_4_4",
            "credit_card_number",
            "Say the card number in groups of four.",
            "four two four two, four two four two, four two four two, four two four two",
        ),
        _entity(
            "card_digit_by_digit",
            "credit_card_number",
            "Say every card digit separately.",
            "four two four two four two four two",
        ),
        _entity(
            "card_with_spaces",
            "credit_card_number",
            "Use spoken spaces between groups.",
            "four two four two space four two four two",
        ),
        _entity(
            "card_last_four_repetition",
            "credit_card_number",
            "Repeat the last four digits.",
            "last four are four two four two",
        ),
        _entity(
            "card_correction",
            "credit_card_number",
            "Include a correction.",
            "four two four three, sorry, four two four two",
        ),
        _entity(
            "card_issuer_style_grouping",
            "credit_card_number",
            "Use card-length appropriate grouping.",
            "three seven eight two, eight two two four six three, one zero zero zero five",
        ),
    ]
