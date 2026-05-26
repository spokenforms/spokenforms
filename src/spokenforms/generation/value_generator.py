from __future__ import annotations

from spokenforms.models import EntitySpec, GeneratedValue
from spokenforms.normalizers import normalizer_for
from spokenforms.providers.base import LLMProvider


def generate_values(
    run_id: str,
    entity: EntitySpec,
    provider: LLMProvider,
    count: int,
) -> list[GeneratedValue]:
    normalize = normalizer_for(entity.entity_id, entity.output_type)
    return [
        GeneratedValue(
            run_id=run_id,
            entity_id=entity.entity_id,
            value=value,
            normalized_value=normalize(value),
            valid=True,
            provider=provider.name,
            model=provider.model,
            sensitive_policy=entity.sensitive_policy,
        )
        for value in provider.generate_values(entity, count)
    ]
