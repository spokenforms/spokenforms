from __future__ import annotations

from spokenforms.generation.consistency_checker import check_consistency
from spokenforms.generation.transcript_generator import generate_candidate
from spokenforms.models import (
    DatasetRecord,
    EntitySpec,
    GeneratedValue,
    PairStatus,
    VerbalizationPattern,
)
from spokenforms.providers.base import LLMProvider


def fill_pairs(
    run_id: str,
    entity: EntitySpec,
    values: list[GeneratedValue],
    patterns: list[VerbalizationPattern],
    provider: LLMProvider,
    target_per_pattern: int,
    max_attempts_per_pair: int,
) -> tuple[list[DatasetRecord], list[PairStatus]]:
    records: list[DatasetRecord] = []
    statuses: list[PairStatus] = []
    for generated_value in values:
        for pattern in patterns:
            valid = 0
            failed = 0
            attempts = 0
            seen: set[str] = set()
            while valid < target_per_pattern and attempts < max_attempts_per_pair:
                attempts += 1
                candidate = generate_candidate(
                    run_id, entity, generated_value, pattern, provider, attempts
                )
                consistency = check_consistency(entity, candidate)
                if consistency.passed and candidate.transcript not in seen:
                    seen.add(candidate.transcript)
                    valid += 1
                    records.append(
                        DatasetRecord(
                            run_id=run_id,
                            entity_id=entity.entity_id,
                            field_name=entity.field_name,
                            question=entity.question,
                            output_type=entity.output_type,
                            field_description=entity.field_description,
                            ground_truth=generated_value.value,
                            normalized_ground_truth=generated_value.normalized_value,
                            transcript=candidate.transcript,
                            requested_pattern=pattern.pattern_id,
                            assigned_pattern_tags=candidate.assigned_pattern_tags,
                            consistency=consistency,
                            generation={
                                "provider": provider.name,
                                "model": provider.model,
                                "attempt": attempts,
                            },
                            metadata=_record_metadata(entity, generated_value),
                            sensitive_policy=entity.sensitive_policy,
                        )
                    )
                else:
                    failed += 1
            statuses.append(
                PairStatus(
                    entity_id=entity.entity_id,
                    value_id=generated_value.id,
                    pattern_id=pattern.pattern_id,
                    target=target_per_pattern,
                    valid=valid,
                    failed=failed,
                    attempts=attempts,
                    status="complete" if valid == target_per_pattern else "underfilled",
                )
            )
    return records, statuses


def _record_metadata(entity: EntitySpec, generated_value: GeneratedValue) -> dict[str, object]:
    return {
        "value_id": generated_value.id,
        "synthetic_sensitive_value": entity.sensitive_policy.synthetic_sensitive_value,
        "sensitive_type": entity.sensitive_policy.sensitive_type,
        "real_world_safe": entity.sensitive_policy.real_world_safe,
    }
