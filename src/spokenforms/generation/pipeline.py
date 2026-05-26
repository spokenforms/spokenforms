from __future__ import annotations

from spokenforms.generation.balancer import fill_pairs
from spokenforms.generation.sensitive_values import validate_sensitive_entity
from spokenforms.generation.value_generator import generate_values
from spokenforms.models import AppConfig, BaseStrictModel, DatasetRecord, GeneratedValue, PairStatus
from spokenforms.patterns import PatternRegistry
from spokenforms.providers.base import LLMProvider


class PipelineResult(BaseStrictModel):
    values: list[GeneratedValue]
    records: list[DatasetRecord]
    pair_statuses: list[PairStatus]


def run_pipeline(
    run_id: str,
    entity_id: str,
    config: AppConfig,
    provider: LLMProvider,
) -> PipelineResult:
    from spokenforms.entities import EntityRegistry

    entity = EntityRegistry().get(entity_id)
    validate_sensitive_entity(entity)
    values = generate_values(run_id, entity, provider, config.generation.num_values)
    patterns = PatternRegistry().for_entity(entity_id)
    records, pair_statuses = fill_pairs(
        run_id=run_id,
        entity=entity,
        values=values,
        patterns=patterns,
        provider=provider,
        target_per_pattern=config.generation.target_per_pattern,
        max_attempts_per_pair=config.generation.max_attempts_per_pair,
    )
    return PipelineResult(values=values, records=records, pair_statuses=pair_statuses)
