from __future__ import annotations

from spokenforms.models import (
    EntitySpec,
    OutputType,
    SensitiveDataPolicy,
    SensitiveType,
    SyntheticSensitiveGenerationMode,
)


def _basic(entity_id: str, field_name: str, output_type: OutputType, question: str) -> EntitySpec:
    return EntitySpec(
        entity_id=entity_id,
        field_name=field_name,
        output_type=output_type,
        question=question,
        field_description=f"A synthetic {field_name} value for extraction testing.",
    )


def built_in_entities() -> list[EntitySpec]:
    return [
        _basic(
            "confirmation_code",
            "Confirmation code",
            OutputType.ALPHANUMERIC,
            "What is your confirmation code?",
        ),
        _basic(
            "account_number",
            "Account number",
            OutputType.NUMERIC_SEQUENCE,
            "What is your account number?",
        ),
        _basic("member_id", "Member ID", OutputType.ALPHANUMERIC, "What is your member ID?"),
        _basic("claim_id", "Claim ID", OutputType.ALPHANUMERIC, "What is your claim ID?"),
        _basic(
            "policy_number", "Policy number", OutputType.ALPHANUMERIC, "What is your policy number?"
        ),
        _basic("zip_code", "ZIP code", OutputType.NUMERIC_SEQUENCE, "What is your ZIP code?"),
        _basic("date_of_birth", "Date of birth", OutputType.DATE, "What is your date of birth?"),
        _basic("full_name", "Full name", OutputType.STRING, "What is your full name?"),
        _basic(
            "phone_number",
            "Phone number",
            OutputType.NUMERIC_SEQUENCE,
            "What is your phone number?",
        ),
        EntitySpec(
            entity_id="ssn",
            field_name="Social Security number",
            output_type=OutputType.SENSITIVE_NUMERIC_SEQUENCE,
            question="What is your Social Security number?",
            field_description="A synthetic US Social Security number for extraction testing only.",
            canonicalization={"type": "ssn", "output_format": "AAA-GG-SSSS"},
            sensitive_policy=SensitiveDataPolicy(
                sensitive_type=SensitiveType.SSN,
                synthetic_sensitive_value=True,
                real_world_safe=True,
                generation_mode=SyntheticSensitiveGenerationMode.RESERVED_OR_INVALID,
                allow_potentially_real_values=False,
                require_synthetic_values=True,
                warning="Generate synthetic SSNs only. Do not generate real SSNs.",
            ),
        ),
        EntitySpec(
            entity_id="credit_card_number",
            field_name="Credit card number",
            output_type=OutputType.SENSITIVE_NUMERIC_SEQUENCE,
            question="What is the credit card number?",
            field_description=(
                "A synthetic or payment-test credit card number for extraction testing only."
            ),
            canonicalization={"type": "credit_card", "output_format": "groups_of_4"},
            sensitive_policy=SensitiveDataPolicy(
                sensitive_type=SensitiveType.CREDIT_CARD_NUMBER,
                synthetic_sensitive_value=True,
                real_world_safe=True,
                generation_mode=SyntheticSensitiveGenerationMode.PAYMENT_TEST_NUMBERS,
                allow_potentially_real_values=False,
                require_synthetic_values=True,
                warning="Generate synthetic/test card numbers only.",
            ),
        ),
        _basic("boolean_answer", "Boolean answer", OutputType.BOOLEAN, "Is that correct?"),
        _basic("enum_answer", "Enum answer", OutputType.ENUM, "Which option do you choose?"),
        _basic(
            "multi_select_answer",
            "Multi-select answer",
            OutputType.MULTI_SELECT_ENUM,
            "Which options apply?",
        ),
        _basic("pain_rating", "Pain rating", OutputType.INTEGER, "How would you rate your pain?"),
        _basic(
            "respiratory_issues",
            "Respiratory issues",
            OutputType.BOOLEAN,
            "Are you having respiratory issues?",
        ),
        _basic(
            "hearing_issues", "Hearing issues", OutputType.BOOLEAN, "Are you having hearing issues?"
        ),
    ]
