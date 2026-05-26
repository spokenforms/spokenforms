from __future__ import annotations

from spokenforms.models import EntitySpec, VerbalizationPattern


def build_transcript_generation_prompt(
    entity: EntitySpec,
    value: str,
    pattern: VerbalizationPattern,
) -> str:
    return f"{entity.question}\nValue: {value}\nPattern: {pattern.instruction}"
