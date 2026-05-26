from __future__ import annotations

from collections import Counter

from spokenforms.models import DatasetRecord, DatasetStats, PairStatus, SensitiveType


def compute_stats(records: list[DatasetRecord], pair_statuses: list[PairStatus]) -> DatasetStats:
    lengths = [len(record.transcript) for record in records]
    by_entity = Counter(record.entity_id for record in records)
    by_pattern = Counter(record.requested_pattern for record in records)
    sensitive_count = sum(
        1
        for record in records
        if record.sensitive_policy.sensitive_type is not SensitiveType.NONE
        and record.sensitive_policy.synthetic_sensitive_value
    )
    passed = sum(1 for record in records if record.consistency.passed)
    return DatasetStats(
        total_records=len(records),
        total_entities=len(by_entity),
        total_values=len({record.ground_truth for record in records}),
        total_patterns=len(by_pattern),
        records_by_entity=dict(by_entity),
        records_by_pattern=dict(by_pattern),
        average_transcript_length=sum(lengths) / len(lengths) if lengths else 0.0,
        min_transcript_length=min(lengths) if lengths else 0,
        max_transcript_length=max(lengths) if lengths else 0,
        validation_pass_rate=passed / len(records) if records else 0.0,
        sensitive_record_count=sensitive_count,
        pair_statuses=pair_statuses,
    )


def render_stats_markdown(stats: DatasetStats) -> str:
    lines = [
        "# SpokenForms stats",
        "",
        f"- Total records: {stats.total_records}",
        f"- Total entities: {stats.total_entities}",
        f"- Total values: {stats.total_values}",
        f"- Total patterns: {stats.total_patterns}",
        f"- Validation pass rate: {stats.validation_pass_rate:.2%}",
        f"- Sensitive synthetic records: {stats.sensitive_record_count}",
        "",
        "## Records by pattern",
    ]
    for pattern, count in sorted(stats.records_by_pattern.items()):
        lines.append(f"- {pattern}: {count}")
    return "\n".join(lines) + "\n"
