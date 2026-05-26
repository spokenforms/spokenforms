from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

import orjson
from pydantic import BaseModel

from spokenforms import __version__
from spokenforms.models import AppConfig, ProviderName, RunManifest, SensitiveType
from spokenforms.utils.hashing import stable_hash


def build_manifest(
    run_id: str,
    created_at: datetime,
    updated_at: datetime,
    config: AppConfig,
    provider: ProviderName,
    model: str,
    entities: list[str],
    sensitive_types: list[SensitiveType],
    status: Literal[
        "running",
        "completed",
        "completed_with_underfilled_pairs",
        "failed",
        "interrupted",
    ],
) -> RunManifest:
    return RunManifest(
        run_id=run_id,
        created_at=created_at,
        updated_at=updated_at,
        package_version=__version__,
        config_hash=stable_hash(config.model_dump_json()),
        provider=provider,
        model=model,
        entities=entities,
        contains_sensitive_synthetic_values=bool(sensitive_types),
        sensitive_types=sensitive_types,
        status=status,
    )


def write_json(path: Path, value: object) -> None:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
