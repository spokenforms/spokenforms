from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from spokenforms.models import DatasetRecord


def flattened_records(records: list[DatasetRecord]) -> list[dict[str, Any]]:
    return [
        {
            "id": record.id,
            "run_id": record.run_id,
            "entity_id": record.entity_id,
            "field_name": record.field_name,
            "question": record.question,
            "output_type": record.output_type,
            "ground_truth": record.ground_truth,
            "normalized_ground_truth": record.normalized_ground_truth,
            "transcript": record.transcript,
            "requested_pattern": record.requested_pattern,
            "consistency_passed": record.consistency.passed,
            "sensitive_type": record.sensitive_policy.sensitive_type,
            "synthetic_sensitive_value": record.sensitive_policy.synthetic_sensitive_value,
            "real_world_safe": record.sensitive_policy.real_world_safe,
        }
        for record in records
    ]


def export_csv(path: Path, records: list[DatasetRecord]) -> None:
    pd.DataFrame(flattened_records(records)).to_csv(path, index=False)


def export_parquet(path: Path, records: list[DatasetRecord]) -> None:
    pd.DataFrame(flattened_records(records)).to_parquet(path, index=False)
