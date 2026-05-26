from __future__ import annotations

from spokenforms.models import EntitySpec, GeneratedValue, TranscriptCandidate, VerbalizationPattern
from spokenforms.providers.base import LLMProvider
from spokenforms.utils.hashing import stable_hash


def generate_candidate(
    run_id: str,
    entity: EntitySpec,
    generated_value: GeneratedValue,
    pattern: VerbalizationPattern,
    provider: LLMProvider,
    attempt: int,
) -> TranscriptCandidate:
    transcript = provider.generate_transcript(entity, generated_value.value, pattern, attempt)
    prompt_hash = stable_hash(
        f"{entity.entity_id}:{generated_value.value}:{pattern.pattern_id}:{attempt}"
    )
    return TranscriptCandidate(
        run_id=run_id,
        entity_id=entity.entity_id,
        value_id=generated_value.id,
        ground_truth=generated_value.value,
        normalized_ground_truth=generated_value.normalized_value,
        requested_pattern=pattern.pattern_id,
        transcript=transcript,
        assigned_pattern_tags=[pattern.pattern_id],
        provider=provider.name,
        model=provider.model,
        attempt=attempt,
        prompt_hash=prompt_hash,
        sensitive_policy=entity.sensitive_policy,
    )
