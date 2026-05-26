from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ExportFormat = Literal["jsonl", "csv", "parquet"]


class ProviderName(StrEnum):
    OPENAI = "openai"
    MOCK = "mock"


class OutputType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    ENUM = "enum"
    MULTI_SELECT_ENUM = "multi_select_enum"
    ALPHANUMERIC = "alphanumeric"
    NUMERIC_SEQUENCE = "numeric_sequence"
    SENSITIVE_NUMERIC_SEQUENCE = "sensitive_numeric_sequence"


class SensitiveType(StrEnum):
    NONE = "none"
    SSN = "ssn"
    CREDIT_CARD_NUMBER = "credit_card_number"


class SyntheticSensitiveGenerationMode(StrEnum):
    NONE = "none"
    RESERVED_OR_INVALID = "reserved_or_invalid"
    PAYMENT_TEST_NUMBERS = "payment_test_numbers"
    LUHN_VALID_SYNTHETIC = "luhn_valid_synthetic"
    LUHN_INVALID_SYNTHETIC = "luhn_invalid_synthetic"
    USER_SUPPLIED_SYNTHETIC_VALUES = "user_supplied_synthetic_values"


class BaseStrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, str_strip_whitespace=True)


class LLMConfig(BaseStrictModel):
    provider: ProviderName = ProviderName.OPENAI
    model: str = "gpt-4.1-mini"
    api_key_env: str | None = "OPENAI_API_KEY"
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 1500
    timeout_seconds: int = 60
    max_retries: int = 4
    concurrency: int = 4
    json_mode: bool = True


class ProjectConfig(BaseStrictModel):
    name: str = "spokenforms_project"
    output_dir: Path = Path("runs")
    random_seed: int = 42


class GenerationConfig(BaseStrictModel):
    num_values: int = 10
    target_per_pattern: int = 5
    batch_size: int = 5
    max_attempts_per_pair: int = 8
    max_total_attempts: int = 10_000
    deduplicate_transcripts: bool = True
    min_transcript_chars: int = 2
    max_transcript_chars: int = 500


class ValidationConfig(BaseStrictModel):
    deterministic_first: bool = True
    llm_check: Literal["never", "fallback", "always"] = "fallback"
    strict: bool = True
    keep_failed_candidates: bool = True
    require_exact_recoverability: bool = True


class ExportConfig(BaseStrictModel):
    formats: list[ExportFormat] = Field(default_factory=lambda: _default_export_formats())


def _default_export_formats() -> list[ExportFormat]:
    return ["jsonl", "csv", "parquet"]


class CacheConfig(BaseStrictModel):
    enabled: bool = True
    directory: Path = Path(".cache/spokenforms")


class SensitiveDataPolicy(BaseStrictModel):
    sensitive_type: SensitiveType = SensitiveType.NONE
    synthetic_sensitive_value: bool = False
    real_world_safe: bool = True
    generation_mode: SyntheticSensitiveGenerationMode = SyntheticSensitiveGenerationMode.NONE
    allow_potentially_real_values: bool = False
    require_synthetic_values: bool = True
    warning: str | None = None


class AppConfig(BaseStrictModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)


class EntitySpec(BaseStrictModel):
    entity_id: str
    enabled: bool = True
    field_name: str
    output_type: OutputType
    question: str
    field_description: str
    canonicalization: dict[str, Any] = Field(default_factory=dict)
    examples: list[str] = Field(default_factory=list)
    sensitive_policy: SensitiveDataPolicy = Field(default_factory=SensitiveDataPolicy)


class VerbalizationPattern(BaseStrictModel):
    pattern_id: str
    scope: Literal["general", "entity_specific"]
    entity_ids: list[str] = Field(default_factory=list)
    category: str | None = None
    instruction: str
    example: str | None = None
    enabled: bool = True


class GeneratedValue(BaseStrictModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    entity_id: str
    value: str
    normalized_value: str
    valid: bool
    validation_errors: list[str] = Field(default_factory=list)
    provider: ProviderName
    model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sensitive_policy: SensitiveDataPolicy = Field(default_factory=SensitiveDataPolicy)
    raw_response: dict[str, Any] | None = None


class TranscriptCandidate(BaseStrictModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    entity_id: str
    value_id: str
    ground_truth: str
    normalized_ground_truth: str
    requested_pattern: str
    transcript: str
    assigned_pattern_tags: list[str]
    provider: ProviderName
    model: str
    attempt: int
    prompt_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sensitive_policy: SensitiveDataPolicy = Field(default_factory=SensitiveDataPolicy)
    raw_response: dict[str, Any] | None = None


class ConsistencyResult(BaseStrictModel):
    passed: bool
    method: Literal["deterministic", "llm", "hybrid"]
    reason: str | None = None
    extracted_value: str | None = None
    normalized_extracted_value: str | None = None
    confidence: float | None = None
    checker_provider: ProviderName | None = None
    checker_model: str | None = None


class DatasetRecord(BaseStrictModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    entity_id: str
    field_name: str
    question: str
    output_type: OutputType
    field_description: str
    ground_truth: str
    normalized_ground_truth: str
    transcript: str
    requested_pattern: str
    assigned_pattern_tags: list[str]
    consistency: ConsistencyResult
    generation: dict[str, Any]
    metadata: dict[str, Any]
    sensitive_policy: SensitiveDataPolicy = Field(default_factory=SensitiveDataPolicy)


class PairStatus(BaseStrictModel):
    entity_id: str
    value_id: str
    pattern_id: str
    target: int
    valid: int
    failed: int
    attempts: int
    status: Literal["complete", "underfilled", "exhausted", "skipped", "error"]


class DatasetStats(BaseStrictModel):
    total_records: int
    total_entities: int
    total_values: int
    total_patterns: int
    records_by_entity: dict[str, int]
    records_by_pattern: dict[str, int]
    average_transcript_length: float
    min_transcript_length: int
    max_transcript_length: int
    validation_pass_rate: float
    sensitive_record_count: int
    pair_statuses: list[PairStatus]


class RunManifest(BaseStrictModel):
    run_id: str
    created_at: datetime
    updated_at: datetime
    package_version: str
    config_hash: str
    provider: ProviderName
    model: str
    entities: list[str]
    contains_sensitive_synthetic_values: bool
    sensitive_types: list[SensitiveType] = Field(default_factory=list)
    status: Literal[
        "running",
        "completed",
        "completed_with_underfilled_pairs",
        "failed",
        "interrupted",
    ]
