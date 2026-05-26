Below is a consolidated updated **PRD + Engineering Build Specification** for **SpokenForms**, explicitly aligned to the paper’s methods and extended to include **SSN** and **credit-card-number** synthetic spoken transcript generation.

---

# SpokenForms PRD and Engineering Build Specification

## Part 1: Product Requirements Document

## 1. Product

**Product name:** SpokenForms
**PyPI package:** `spokenforms`
**Python import:** `spokenforms`
**CLI command:** `spokenforms`

**One-line description:**

```text
Generate synthetic spoken transcript variants for structured values, alphanumeric sequences, and voice-AI entity extraction tasks.
```

**Core concept:**

```text
canonical structured value
  -> spoken transcript variants
  -> consistency validation
  -> balanced synthetic dataset
```

SpokenForms should implement the synthetic data-generation method described in the uploaded LingVarBench paper: generate canonical values, combine those values with curated linguistic/verbalization patterns, generate phone-call-style transcripts, and retain only value/transcript pairs that pass consistency validation. The paper describes this as a three-stage pipeline: **Value Generator**, **Transcript Generator**, and **Consistency Checker**. 

---

## 2. Problem

Voice AI systems often need to extract structured values from noisy, spontaneous speech. The challenge is not merely recognizing text; it is recognizing how humans verbalize structured values in many different ways.

Examples:

```text
ZIP code:
  94101
  nine four one zero one
  nine four one oh one
  ninety four one oh one

DOB:
  01-02-1985
  January second nineteen eighty five
  zero one zero two one nine eight five

Confirmation code:
  AB123
  A B one two three
  A as in Alpha, B as in Bravo, one two three

SSN:
  900-12-3456
  nine zero zero, one two, three four five six
  nine hundred, twelve, thirty four fifty six

Credit card:
  4242 4242 4242 4242
  four two four two, four two four two, four two four two, four two four two
```

Real phone transcripts are often private, expensive to annotate, hard to share, and limited in coverage. The paper identifies this exact bottleneck: teams often wait for real transcripts, then manually tune prompts on sensitive data, which slows iteration and limits robustness. 

---

## 3. Product intent

SpokenForms should be a reusable Python package and CLI for generating synthetic direct-answer phone-call transcript data for structured extraction tasks.

The product should let users define:

```text
entity schemas
canonical value formats
verbalization patterns
entity-specific spoken formats
validation rules
normalization rules
output dataset format
provider configuration
```

The goal is to create realistic synthetic data before real transcripts are available, while preserving controllability, reproducibility, and consistency.

---

## 4. Method from the paper

SpokenForms must explicitly implement the following method from LingVarBench.

### 4.1 Schema-driven value generation

Given a field description:

```text
field name
field type
natural-language constraints
question
number of values
```

Use an LLM or deterministic generator to produce canonical values.

Example:

```yaml
field_name: ZIP code
output_type: string
field_description: A five-digit US ZIP code.
question: What is your ZIP code?
num_values: 10
```

The paper’s value-generation module uses an LLM prompted with a field description to produce plausible values, and the number of values is configurable. 

---

### 4.2 Value × verbalization-pattern pairing

For each generated value, combine it with each enabled verbalization pattern:

```text
value × pattern
```

Example:

```text
94101 × digit_by_digit
94101 × grouped_two
94101 × correction
94101 × filler_words
```

The paper’s transcript generation module creates all possible pairs of generated values and LVPs, then prompts the LLM for each pair. 

---

### 4.3 Controlled transcript generation

For every `value × pattern` pair, generate phone-call-style direct-answer utterances that express the target value.

Example:

```json
{
  "ground_truth": "AB123",
  "requested_pattern": "nato_letters",
  "transcript": "A as in Alpha, B as in Bravo, one two three."
}
```

The paper conditions the LLM on the target value and the linguistic verbalization pattern so the transcript reflects a controlled variation while preserving the underlying value. 

---

### 4.4 Consistency checking

Each generated transcript must be validated against the intended value.

Example pass:

```json
{
  "ground_truth": "94101",
  "transcript": "nine four one zero one",
  "passed": true
}
```

Example fail:

```json
{
  "ground_truth": "94101",
  "transcript": "nineteen forty one zero one",
  "passed": false
}
```

The paper uses a consistency-checking module to verify whether a generated transcript correctly contains the intended value and retains only valid examples. 

---

### 4.5 Recursive balancing

SpokenForms must avoid overrepresenting easy value/pattern pairs. It must recursively regenerate underfilled pairs until each pair reaches the configured target or exhausts attempts.

Example:

```text
target_per_pattern = 5

AB123 × digit_by_digit      5 accepted
AB123 × nato_letters        5 accepted
AB123 × correction          3 accepted -> regenerate
AB123 × grouped             5 accepted
```

The paper explicitly uses recursive generation for underrepresented pairs to achieve uniform coverage across value–variation pairs. 

---

### 4.6 Modular pattern inventory

SpokenForms must model verbalization patterns as a modular, extensible inventory.

Patterns fall into two categories:

```text
general patterns
entity-specific patterns
```

General patterns include reusable speech phenomena:

```text
filler words
hesitation
correction
repetition
pause
formal
casual
polite
confident
uncertain
confirmation
clarification
```

Entity-specific patterns encode format-specific readout styles:

```text
ZIP digit grouping
DOB digit formats
name variants
SSN grouping
credit-card grouping
NATO spelling for alphanumeric IDs
```

The paper’s LVP design is intentionally lightweight and extensible: keep general LVPs reusable, add entity-specific templates for local conventions, and validate new patterns through the same consistency checker. 

---

### 4.7 Direct-answer scope

SpokenForms v0.1 must focus on direct-answer turns:

```text
Agent: What is your confirmation code?
Caller: It is A B one two three.
```

Out of scope for v0.1:

```text
multi-turn clarification
refusals
topic shifts
implicit answers
ambiguous dialogue-state resolution
```

The paper explicitly scopes the method to direct-answer utterances that state the target value, leaving refusals, topic shifts, clarification questions, and pragmatic answers for future work. 

---

### 4.8 Optional DSPy/SIMBA prompt optimization

SpokenForms should optionally support prompt optimization later. The paper uses generated synthetic data to optimize extraction prompts with DSPy and SIMBA, then evaluates those prompts on synthetic and real transcripts. This should be a v0.2+ optional feature, not required for v0.1. 

---

## 5. Target users

Primary users:

```text
voice AI engineers
LLM application engineers
ML engineers
NLP researchers
QA engineers for voice systems
prompt engineers
data engineers
evaluation engineers
```

Use-case teams:

```text
contact-center automation
healthcare intake automation
insurance automation
banking voice automation
payments and fintech voice systems
identity verification flows
customer support bots
```

---

## 6. In-scope entities for v0.1

SpokenForms must support these built-in entities:

```text
confirmation_code
account_number
member_id
claim_id
policy_number
zip_code
date_of_birth
full_name
phone_number
ssn
credit_card_number
boolean_answer
enum_answer
multi_select_answer
```

Healthcare-oriented examples from the paper remain supported:

```text
pain_rating
respiratory_issues
hearing_issues
```

---

## 7. Sensitive synthetic-data policy

Because SpokenForms includes SSNs and credit-card numbers, it must enforce a strict synthetic-only policy.

### 7.1 SSN policy

SpokenForms must never intentionally generate real SSNs.

For built-in `ssn`, use synthetic-only generation modes:

```text
reserved_or_invalid
fixed_test_values
user_supplied_synthetic_values
```

Default mode:

```yaml
synthetic_policy:
  real_world_safe: true
  generation_mode: reserved_or_invalid
  allow_potentially_real_values: false
```

Default generated SSNs should use reserved or invalid ranges/patterns that are useful for extraction testing but should not be treated as real identity data.

Examples:

```text
900-12-3456
999-45-6789
000-12-3456
666-22-3333
123-00-4567
123-45-0000
```

The default normalizer may accept these as syntactically extractable values, but metadata must mark them as:

```json
{
  "synthetic_sensitive_value": true,
  "sensitive_type": "ssn",
  "real_world_safe": true
}
```

### 7.2 Credit-card policy

SpokenForms must never generate active payment-card data.

For built-in `credit_card_number`, use synthetic-only modes:

```text
payment_test_numbers
luhn_valid_synthetic
luhn_invalid_synthetic
user_supplied_synthetic_values
```

Default mode:

```yaml
synthetic_policy:
  real_world_safe: true
  generation_mode: payment_test_numbers
  allow_potentially_real_values: false
```

Credit-card values must be tagged as synthetic and must never be presented as usable financial credentials.

Metadata:

```json
{
  "synthetic_sensitive_value": true,
  "sensitive_type": "credit_card_number",
  "real_world_safe": true,
  "luhn_valid": true,
  "issuer_network": "test"
}
```

### 7.3 Guardrails

The CLI must reject unsafe generation unless explicitly overridden with a dangerous flag.

Default behavior:

```bash
spokenforms build --entity ssn
# allowed only with synthetic-safe generation mode
```

Unsafe behavior:

```bash
spokenforms build --entity ssn --allow-potentially-real-sensitive-values
```

This flag must:

```text
print a warning
require --i-understand-sensitive-data-risk
write warning to manifest
mark all records as potentially_sensitive
```

For v0.1, the recommended implementation is to **not implement unsafe generation at all**. Reserve the flags in the schema, but fail with a clear error if users try to enable them.

---

## 8. Product scope

## 8.1 In scope for v0.1

```text
Python 3.12+ package
Typer CLI
uv project management
Pydantic-only structured models
pydantic-settings-only environment loading
OpenAI provider
mock provider
YAML config
.env.example
schema-driven entity definitions
general verbalization patterns
entity-specific verbalization patterns
value generation
transcript generation
consistency checking
deterministic normalizers
recursive balancing
sensitive synthetic-value guardrails
SSN built-in support
credit-card-number built-in support
JSONL export
CSV export
Parquet export
stats
train/validation/test split
resume support
full tests
GitHub Actions
PyPI publishing workflow
```

---

## 8.2 Out of scope for v0.1

```text
real SSN generation
real credit-card generation
payment processing
identity verification
multi-turn dialogue simulation
audio generation
ASR simulation
PHI ingestion
PCI data ingestion
real transcript ingestion
annotation UI
web app
database job queue
distributed generation
fine-tuning jobs
```

---

## 9. Success criteria

### 9.1 Functional success

This must work without network calls:

```bash
uv run spokenforms init --output demo
cd demo

uv run spokenforms build \
  --config config.yaml \
  --entity credit_card_number \
  --num-values 3 \
  --target-per-pattern 2 \
  --provider mock \
  --output-dir runs/demo_credit_card

uv run spokenforms build \
  --config config.yaml \
  --entity ssn \
  --num-values 3 \
  --target-per-pattern 2 \
  --provider mock \
  --output-dir runs/demo_ssn
```

Expected files:

```text
manifest.json
config.resolved.yaml
values.jsonl
candidates.jsonl
validated.jsonl
dataset.jsonl
dataset.csv
dataset.parquet
stats.json
stats.md
logs.jsonl
```

---

### 9.2 Quality success

All checks pass:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv build
test -f .env.example
```

Minimum coverage:

```text
90%
```

---

# Part 2: Engineering Build Specification

## 1. Hard engineering requirements

```text
Python 3.12+
uv for all Python management
Typer CLI
Pydantic BaseModel for all structured data
pydantic-settings for all environment variables
No dataclasses
No attrs
No direct os.getenv
No direct os.environ in application code
Every function must have fully typed arguments
Every function must have explicit return type
Strict mypy
Ruff linting and formatting
pytest
Full test suite
GitHub Actions
PyPI-ready package
```

---

## 2. Repository layout

```text
spokenforms/
  .github/
    workflows/
      ci.yml
      publish.yml
      codeql.yml
      release-check.yml
    dependabot.yml

  src/
    spokenforms/
      __init__.py
      __main__.py
      py.typed

      cli.py
      config.py
      settings.py
      exceptions.py
      models.py
      constants.py

      providers/
        __init__.py
        base.py
        factory.py
        openai_provider.py
        mock_provider.py

      prompts/
        __init__.py
        models.py
        value_generation.py
        transcript_generation.py
        consistency_check.py
        extraction.py

      generation/
        __init__.py
        pipeline.py
        value_generator.py
        transcript_generator.py
        consistency_checker.py
        balancer.py
        sensitive_values.py

      patterns/
        __init__.py
        registry.py
        builtins.py

      entities/
        __init__.py
        registry.py
        builtins.py

      normalizers/
        __init__.py
        base.py
        numbers.py
        alphanumeric.py
        dates.py
        names.py
        enums.py
        booleans.py
        ssn.py
        credit_card.py
        factory.py

      validators/
        __init__.py
        ssn.py
        credit_card.py
        luhn.py
        sensitive_policy.py

      storage/
        __init__.py
        jsonl.py
        exporters.py
        manifest.py
        cache.py

      stats/
        __init__.py
        dataset_stats.py

      utils/
        __init__.py
        hashing.py
        json_parser.py
        retry.py
        time.py
        text.py
        paths.py

  tests/
    unit/
      test_settings.py
      test_config.py
      test_models.py
      test_no_dataclasses.py
      test_no_direct_env_reads.py
      test_pattern_registry.py
      test_entity_registry.py
      test_json_parser.py
      test_hashing.py
      test_normalize_numbers.py
      test_normalize_alphanumeric.py
      test_normalize_dates.py
      test_normalize_names.py
      test_normalize_enums.py
      test_normalize_booleans.py
      test_normalize_ssn.py
      test_normalize_credit_card.py
      test_luhn.py
      test_sensitive_policy.py
      test_balancer.py
      test_exporters.py
      test_stats.py

    integration/
      test_cli_init.py
      test_cli_build_mock.py
      test_cli_build_ssn_mock.py
      test_cli_build_credit_card_mock.py
      test_cli_stats.py
      test_pipeline_mock_provider.py
      test_config_precedence.py

  examples/
    config.yaml
    entities.yaml
    patterns.yaml

  .env.example
  .gitignore
  .python-version
  pyproject.toml
  uv.lock
  README.md
  LICENSE
  CHANGELOG.md
  CONTRIBUTING.md
  SECURITY.md
```

---

## 3. `pyproject.toml`

```toml
[project]
name = "spokenforms"
version = "0.1.0"
description = "Generate synthetic spoken transcript variants for structured values and alphanumeric sequences."
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [
  { name = "Aashraya", email = "aashraya@observe.ai" }
]
keywords = [
  "synthetic-data",
  "voice-ai",
  "transcripts",
  "entity-extraction",
  "llm",
  "cli",
  "typer",
  "pydantic",
  "alphanumeric",
  "spoken-forms"
]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Typing :: Typed"
]

dependencies = [
  "typer>=0.12.0",
  "rich>=13.7.0",
  "pydantic>=2.8.0",
  "pydantic-settings>=2.4.0",
  "pyyaml>=6.0.2",
  "orjson>=3.10.0",
  "tenacity>=8.5.0",
  "openai>=1.40.0",
  "pandas>=2.2.0",
  "pyarrow>=16.0.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "pytest-cov>=5.0.0",
  "pytest-asyncio>=0.23.0",
  "pytest-mock>=3.14.0",
  "hypothesis>=6.100.0",
  "ruff>=0.6.0",
  "mypy>=1.11.0",
  "types-PyYAML>=6.0.12"
]

dspy = [
  "dspy-ai>=2.4.0"
]

[project.scripts]
spokenforms = "spokenforms.cli:app"

[build-system]
requires = ["hatchling>=1.25.0"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/spokenforms"]

[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
  "E",
  "F",
  "I",
  "UP",
  "B",
  "C4",
  "SIM",
  "TCH",
  "ANN",
  "ARG",
  "PTH",
  "RUF"
]
ignore = ["ANN401"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_any_generics = true
no_implicit_optional = true
show_error_codes = true
pretty = true
mypy_path = "src"

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
  "--strict-markers",
  "--strict-config",
  "--cov=spokenforms",
  "--cov-report=term-missing",
  "--cov-report=xml",
  "--cov-fail-under=90"
]
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["spokenforms"]

[tool.coverage.report]
show_missing = true
skip_covered = true
```

---

## 4. `.env.example`

```bash
# SpokenForms environment configuration
# Copy this file to .env for local development.
# Never commit your real .env file.

# ---------------------------------------------------------------------
# LLM provider
# ---------------------------------------------------------------------

# Supported: openai, mock
SPOKENFORMS_LLM_PROVIDER=openai

# Default OpenAI model used unless overridden by config.yaml or CLI flags.
SPOKENFORMS_OPENAI_MODEL=gpt-4.1-mini

# Required only when SPOKENFORMS_LLM_PROVIDER=openai.
OPENAI_API_KEY=sk-your-key-here

# ---------------------------------------------------------------------
# Generation defaults
# ---------------------------------------------------------------------

SPOKENFORMS_TEMPERATURE=0
SPOKENFORMS_TOP_P=1.0
SPOKENFORMS_MAX_OUTPUT_TOKENS=1500
SPOKENFORMS_TIMEOUT_SECONDS=60
SPOKENFORMS_MAX_RETRIES=4
SPOKENFORMS_CONCURRENCY=4

# ---------------------------------------------------------------------
# Project defaults
# ---------------------------------------------------------------------

SPOKENFORMS_PROJECT_NAME=spokenforms_project
SPOKENFORMS_OUTPUT_DIR=runs
SPOKENFORMS_RANDOM_SEED=42

# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------

SPOKENFORMS_CACHE_ENABLED=true
SPOKENFORMS_CACHE_DIR=.cache/spokenforms

# ---------------------------------------------------------------------
# Sensitive synthetic data safety
# ---------------------------------------------------------------------

SPOKENFORMS_ALLOW_POTENTIALLY_REAL_SENSITIVE_VALUES=false
SPOKENFORMS_REQUIRE_SYNTHETIC_SENSITIVE_VALUES=true

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

SPOKENFORMS_LOG_LEVEL=INFO
SPOKENFORMS_DEBUG=false
```

---

## 5. Settings model

Create `src/spokenforms/settings.py`.

```python
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from spokenforms.models import ProviderName


class SpokenFormsSettings(BaseSettings):
    """Environment-backed settings for SpokenForms.

    All environment variable reads must go through this class.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="SPOKENFORMS_",
        case_sensitive=False,
        extra="ignore",
    )

    project_name: str = "spokenforms_project"
    output_dir: Path = Path("runs")
    random_seed: int = 42

    llm_provider: ProviderName = ProviderName.OPENAI
    openai_model: str = "gpt-4.1-mini"
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )

    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 1500
    timeout_seconds: int = 60
    max_retries: int = 4
    concurrency: int = 4

    cache_enabled: bool = True
    cache_dir: Path = Path(".cache/spokenforms")

    allow_potentially_real_sensitive_values: bool = False
    require_synthetic_sensitive_values: bool = True

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    debug: bool = False


def load_settings() -> SpokenFormsSettings:
    """Load and validate environment-backed settings."""
    return SpokenFormsSettings()
```

---

## 6. Config precedence

```text
CLI flags
  > config.yaml
  > environment variables / .env via pydantic-settings
  > package defaults
```

Application code must not use:

```python
os.getenv(...)
os.environ.get(...)
os.environ[...]
load_dotenv(...)
dotenv_values(...)
```

---

## 7. Core Pydantic models

Create `src/spokenforms/models.py`.

```python
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


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
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class LLMConfig(BaseStrictModel):
    provider: ProviderName = ProviderName.OPENAI
    model: str
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
    formats: list[Literal["jsonl", "csv", "parquet"]] = Field(
        default_factory=lambda: ["jsonl", "csv", "parquet"]
    )


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
    llm: LLMConfig
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
```

---

## 8. Built-in entities

Create `src/spokenforms/entities/builtins.py`.

Required built-ins:

```text
confirmation_code
account_number
member_id
claim_id
policy_number
zip_code
date_of_birth
full_name
phone_number
ssn
credit_card_number
boolean_answer
enum_answer
multi_select_answer
pain_rating
respiratory_issues
hearing_issues
```

Example YAML entries:

```yaml
- entity_id: ssn
  enabled: true
  field_name: Social Security number
  output_type: sensitive_numeric_sequence
  question: What is your Social Security number?
  field_description: >
    A synthetic US Social Security number for extraction testing only.
    The value must not represent a real person.
  canonicalization:
    type: ssn
    output_format: "AAA-GG-SSSS"
    strip_separators: false
    normalize_separators: true
  sensitive_policy:
    sensitive_type: ssn
    synthetic_sensitive_value: true
    real_world_safe: true
    generation_mode: reserved_or_invalid
    allow_potentially_real_values: false
    require_synthetic_values: true
    warning: "Generate synthetic SSNs only. Do not generate real SSNs."

- entity_id: credit_card_number
  enabled: true
  field_name: Credit card number
  output_type: sensitive_numeric_sequence
  question: What is the credit card number?
  field_description: >
    A synthetic or payment-test credit card number for extraction testing only.
    The value must not be an active payment credential.
  canonicalization:
    type: credit_card
    output_format: "groups_of_4"
    strip_separators: true
    luhn_required: true
    allowed_lengths: [13, 15, 16, 19]
  sensitive_policy:
    sensitive_type: credit_card_number
    synthetic_sensitive_value: true
    real_world_safe: true
    generation_mode: payment_test_numbers
    allow_potentially_real_values: false
    require_synthetic_values: true
    warning: "Generate synthetic/test card numbers only. Do not generate active payment card data."
```

---

## 9. Built-in verbalization patterns

Create `src/spokenforms/patterns/builtins.py`.

### 9.1 General patterns from the paper

```text
filler_words
hesitation
correction
repetition
pause
formal
casual
polite
confident
uncertain
rushed
careful
confirmation
clarification
direct_and_simple
brief_confirmation
concise_confirmation
```

These map to the general LVP category in the paper’s appendix, including filler words, hesitation, self-correction, repetition, formal/casual phrasing, confidence/uncertainty, and confirmation. 

---

### 9.2 Sequence patterns

```text
digit_by_digit
character_by_character
letter_names
nato_letters
grouped_two
grouped_three
grouped_four
mixed_grouping
with_separators
spoken_separator_words
spelled_out_with_hyphens
double_triple_digits
read_as_large_number
```

---

### 9.3 SSN-specific patterns

```yaml
- pattern_id: ssn_grouped_3_2_4
  scope: entity_specific
  entity_ids: ["ssn"]
  category: ssn
  instruction: Say the SSN in the standard 3-2-4 grouping.
  example: nine zero zero, one two, three four five six

- pattern_id: ssn_digit_by_digit
  scope: entity_specific
  entity_ids: ["ssn"]
  category: ssn
  instruction: Say every SSN digit separately.
  example: nine zero zero one two three four five six

- pattern_id: ssn_with_dashes
  scope: entity_specific
  entity_ids: ["ssn"]
  category: ssn
  instruction: Include spoken dash separators between SSN groups.
  example: nine zero zero dash one two dash three four five six

- pattern_id: ssn_correction
  scope: entity_specific
  entity_ids: ["ssn"]
  category: ssn
  instruction: Include a self-correction while preserving the final SSN.
  example: nine zero one, sorry, nine zero zero, one two, three four five six

- pattern_id: ssn_repetition_for_confirmation
  scope: entity_specific
  entity_ids: ["ssn"]
  category: ssn
  instruction: Repeat one SSN group for confirmation.
  example: nine zero zero, one two, one two, three four five six
```

---

### 9.4 Credit-card-specific patterns

```yaml
- pattern_id: card_grouped_4_4_4_4
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Say the card number in four groups of four digits.
  example: four two four two, four two four two, four two four two, four two four two

- pattern_id: card_digit_by_digit
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Say every card digit separately.
  example: four two four two four two four two four two four two four two four two

- pattern_id: card_with_spaces
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Use spoken spaces between groups.
  example: four two four two space four two four two space four two four two space four two four two

- pattern_id: card_last_four_repetition
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Repeat the last four digits for confirmation while preserving the full number.
  example: four two four two, four two four two, four two four two, four two four two — last four are four two four two

- pattern_id: card_correction
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Include a correction while preserving the final card number.
  example: four two four three, sorry, four two four two, four two four two, four two four two, four two four two

- pattern_id: card_issuer_style_grouping
  scope: entity_specific
  entity_ids: ["credit_card_number"]
  category: credit_card
  instruction: Use grouping appropriate to the card length, such as 4-6-5 for fifteen-digit cards or 4-4-4-4 for sixteen-digit cards.
  example: three seven eight two, eight two two four six three, one zero zero zero five
```

---

## 10. Prompt contracts

Create `src/spokenforms/prompts/models.py`.

```python
from __future__ import annotations

from pydantic import Field

from spokenforms.models import BaseStrictModel


class ValueGenerationResponse(BaseStrictModel):
    values: list[str] = Field(min_length=1)


class TranscriptItem(BaseStrictModel):
    transcript: str
    variation_types: list[str]


class TranscriptGenerationResponse(BaseStrictModel):
    transcripts: list[TranscriptItem] = Field(min_length=1)


class ConsistencyCheckResponse(BaseStrictModel):
    passed: bool
    extracted_value: str | None = None
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
```

---

### 10.1 Value-generation prompt

The prompt must follow the paper’s value-generation method:

```text
Input:
- field name
- field description
- question
- expected output type
- number of values

Output:
{ "values": ["value_1", "value_2"] }
```

Additional sensitive-entity rules:

```text
For SSN:
- Generate synthetic/test SSNs only.
- Do not generate real-person SSNs.
- Prefer configured reserved_or_invalid generation mode.

For credit-card number:
- Generate synthetic/test card numbers only.
- Do not generate active payment credentials.
- Use configured payment_test_numbers or synthetic mode.
```

---

### 10.2 Transcript-generation prompt

The prompt must follow the paper’s transcript-generation method:

```text
Input:
- question
- output type
- target value
- existing transcripts
- variation types
- variation instructions

Task:
Generate additional natural spoken transcripts that verbalize the target value without changing its meaning.

Output:
{
  "transcripts": [
    {
      "transcript": "spoken response",
      "variation_types": ["type1"]
    }
  ]
}
```

Sensitive-entity additions:

```text
- Do not say or imply that synthetic SSNs or card numbers are real.
- Do not include extra unrelated sensitive values.
- Do not generate CVV, expiration date, PIN, password, or account login credentials unless a separate synthetic entity explicitly requests it.
```

---

### 10.3 Consistency-check prompt

The prompt must follow the paper’s validation method:

```text
Input:
- transcript
- ground truth
- action/entity name

Task:
Determine whether the ground truth value can be extracted from the transcript.

Output:
{
  "passed": true,
  "extracted_value": "normalized value",
  "reason": "brief reason",
  "confidence": 1.0
}
```

Rules:

```text
Pass only when the ground truth is recoverable.
Fail vague, contradictory, off-topic, or non-answer transcripts.
For corrections, use the final corrected value.
For SSN, normalize spoken digits and 3-2-4 grouping.
For credit cards, normalize spoken digits and grouping.
For alphanumeric sequences, normalize case, separators, NATO words, and digit words.
```

The paper’s appendix provides abstract prompts for value generation, transcript generation, validation, and extraction; SpokenForms should formalize those as typed prompt functions with typed response models. 

---

## 11. Normalizers and validators

All normalizers must be fully typed.

### 11.1 Base normalizer

```python
from __future__ import annotations

from typing import Protocol

from spokenforms.models import EntitySpec


class ValueNormalizer(Protocol):
    def normalize(self, value: str, entity: EntitySpec) -> str:
        """Normalize a value for comparison."""
        ...
```

---

### 11.2 Number normalizer

Must handle:

```text
one two three -> 123
one oh five -> 105
one zero five -> 105
double seven -> 77
triple nine -> 999
```

---

### 11.3 Alphanumeric normalizer

Must handle:

```text
A B C one two three -> ABC123
A as in Alpha B as in Bravo C as in Charlie one two three -> ABC123
ay bee see one two three -> ABC123
A dash B slash C one two three -> ABC123
A-B-C-123 -> ABC123
```

---

### 11.4 SSN normalizer

Create `src/spokenforms/normalizers/ssn.py`.

Must handle:

```text
900-12-3456 -> 900-12-3456
900123456 -> 900-12-3456
nine zero zero one two three four five six -> 900-12-3456
nine zero zero, one two, three four five six -> 900-12-3456
nine zero zero dash one two dash three four five six -> 900-12-3456
nine hundred, twelve, thirty four fifty six -> configurable; default may reject
```

Default behavior:

```text
strict_digit_recovery = true
```

That means the normalizer should prefer digit-by-digit recovery. Large-number interpretations such as “nine hundred” should be accepted only if the entity config enables `allow_group_as_number_words`.

SSN validator requirements:

```text
Validate shape AAA-GG-SSSS.
Validate synthetic policy.
Reject potentially real values by default.
Allow reserved_or_invalid synthetic patterns.
Mark all records sensitive.
```

---

### 11.5 Credit-card normalizer

Create `src/spokenforms/normalizers/credit_card.py`.

Must handle:

```text
4242424242424242 -> 4242424242424242
4242 4242 4242 4242 -> 4242424242424242
four two four two four two four two four two four two four two four two -> 4242424242424242
four two four two, four two four two, four two four two, four two four two -> 4242424242424242
four two four two space four two four two space four two four two space four two four two -> 4242424242424242
```

Credit-card validator requirements:

```text
Validate length from config.
Optionally validate Luhn checksum.
Validate synthetic policy.
Reject potentially real card generation by default.
Mark all records sensitive.
Never generate CVV, expiration date, PIN, or cardholder identity as part of this entity.
```

---

### 11.6 Luhn validator

Create `src/spokenforms/validators/luhn.py`.

```python
from __future__ import annotations


def luhn_checksum(number: str) -> int:
    """Return the Luhn checksum for a numeric string."""
    ...


def is_luhn_valid(number: str) -> bool:
    """Return whether a numeric string passes the Luhn check."""
    ...


def generate_luhn_check_digit(prefix: str) -> str:
    """Generate a Luhn check digit for a numeric prefix."""
    ...
```

All functions must be fully typed.

---

## 12. Sensitive value generators

Create `src/spokenforms/generation/sensitive_values.py`.

Required functions:

```python
from __future__ import annotations

from random import Random

from spokenforms.models import EntitySpec


def generate_synthetic_ssn_values(
    *,
    entity: EntitySpec,
    num_values: int,
    random: Random,
) -> list[str]:
    """Generate synthetic-only SSN-like values according to policy."""
    ...


def generate_synthetic_credit_card_values(
    *,
    entity: EntitySpec,
    num_values: int,
    random: Random,
) -> list[str]:
    """Generate synthetic-only credit-card-like values according to policy."""
    ...
```

Rules:

```text
Do not call LLM for sensitive value generation by default.
Use deterministic synthetic generators for SSN and credit-card numbers.
Allow LLM transcript generation after canonical synthetic values are generated.
Run deterministic validation before LLM consistency checking.
```

This is a product-level adaptation of the paper: keep the paper’s pipeline, but for sensitive identifiers, prefer deterministic canonical value generation and use the LLM for transcript variation only.

---

## 13. Generation pipeline

Create `src/spokenforms/generation/pipeline.py`.

Pipeline:

```text
load settings
load config
load entities
load patterns
create run manifest
generate canonical values
  - deterministic generator for sensitive built-ins by default
  - LLM generator for ordinary entities
normalize and validate values
create all value × pattern pairs
generate transcript candidates
validate candidates
accept valid records
retry underfilled pairs
export dataset
write stats
update manifest
```

Pseudo-code:

```text
for entity in selected_entities:
    values = generate_values(entity)

    for value in values:
        for pattern in enabled_patterns(entity):
            while accepted_count(value, pattern) < target_per_pattern:
                candidates = generate_transcripts(value, pattern)
                validation_results = validate(candidates)

                accept passed candidates
                retry if pair underfilled
                stop if max attempts reached
```

---

## 14. Balancing algorithm

Create `src/spokenforms/generation/balancer.py`.

```python
type PairKey = tuple[str, str, str]
# entity_id, value_id, pattern_id
```

Algorithm:

```text
1. Build all PairKeys from enabled values and enabled patterns.
2. Initialize counts from existing accepted records if resuming.
3. Select underfilled pairs.
4. Prioritize pairs by:
   a. lowest accepted_count / target_per_pattern
   b. lowest attempt count
   c. seeded random tie-breaker
5. Generate candidates for selected pair.
6. Validate candidates.
7. Add accepted records.
8. Requeue if pair is still underfilled and attempts remain.
9. Stop when all pairs are complete or exhausted.
```

Pair statuses:

```text
complete
underfilled
exhausted
skipped
error
```

---

## 15. Dataset record output

Every accepted record must include paper-style metadata: value, transcript, variation/pattern, consistency, LLM model, and timestamp.

Example SSN record:

```json
{
  "id": "uuid",
  "run_id": "2026-05-25T22-00-00Z_ssn_ab12",
  "entity_id": "ssn",
  "field_name": "Social Security number",
  "question": "What is your Social Security number?",
  "output_type": "sensitive_numeric_sequence",
  "field_description": "A synthetic US Social Security number for extraction testing only.",
  "ground_truth": "900-12-3456",
  "normalized_ground_truth": "900-12-3456",
  "transcript": "nine zero zero, one two, three four five six",
  "requested_pattern": "ssn_grouped_3_2_4",
  "assigned_pattern_tags": ["ssn_grouped_3_2_4"],
  "consistency": {
    "passed": true,
    "method": "hybrid",
    "reason": "The transcript verbalizes the SSN as 900-12-3456.",
    "extracted_value": "900-12-3456",
    "normalized_extracted_value": "900-12-3456",
    "confidence": 1.0,
    "checker_provider": "openai",
    "checker_model": "configured-model"
  },
  "sensitive_policy": {
    "sensitive_type": "ssn",
    "synthetic_sensitive_value": true,
    "real_world_safe": true,
    "generation_mode": "reserved_or_invalid",
    "allow_potentially_real_values": false,
    "require_synthetic_values": true,
    "warning": "Generate synthetic SSNs only. Do not generate real SSNs."
  },
  "generation": {
    "provider": "openai",
    "model": "configured-model",
    "temperature": 0,
    "top_p": 1.0,
    "attempt": 1,
    "prompt_template_version": "v1",
    "prompt_hash": "sha256..."
  },
  "metadata": {
    "created_at": "2026-05-25T22:00:00Z",
    "schema_version": "v1",
    "config_hash": "sha256..."
  }
}
```

---

## 16. CLI

Required commands:

```text
spokenforms init
spokenforms providers test
spokenforms entities list
spokenforms patterns list
spokenforms values generate
spokenforms transcripts generate
spokenforms validate
spokenforms build
spokenforms stats
spokenforms split
spokenforms export
```

Examples:

```bash
spokenforms build \
  --config config.yaml \
  --entities entities.yaml \
  --patterns patterns.yaml \
  --entity ssn \
  --num-values 10 \
  --target-per-pattern 5 \
  --provider openai \
  --output-dir runs/ssn_demo
```

```bash
spokenforms build \
  --config config.yaml \
  --entity credit_card_number \
  --num-values 10 \
  --target-per-pattern 5 \
  --provider mock \
  --output-dir runs/card_demo
```

Sensitive CLI behavior:

```text
If entity is ssn or credit_card_number:
  - enforce synthetic policy
  - print clear synthetic-data warning
  - write sensitive metadata to manifest
  - reject unsafe generation modes by default
```

---

## 17. Exporters

Required formats:

```text
JSONL
CSV
Parquet
```

CSV columns:

```text
id
run_id
entity_id
field_name
question
output_type
ground_truth
normalized_ground_truth
transcript
requested_pattern
assigned_pattern_tags
consistency_passed
consistency_method
consistency_reason
extracted_value
provider
model
temperature
top_p
created_at
synthetic_sensitive_value
sensitive_type
real_world_safe
generation_mode
```

---

## 18. Stats

Stats must include:

```text
total records
total entities
total values
total patterns
records by entity
records by pattern
records by value
average transcript length
min transcript length
max transcript length
validation pass rate
attempt count distribution
complete pair count
underfilled pair count
exhausted pair count
sensitive record count
records by sensitive type
```

---

## 19. Tests

Add these required tests on top of the previous suite.

### 19.1 SSN tests

```text
test_ssn_normalizer_digits_with_dashes
test_ssn_normalizer_spoken_digits
test_ssn_normalizer_grouped_3_2_4
test_ssn_rejects_non_synthetic_policy_violation
test_ssn_generator_uses_reserved_or_invalid_by_default
test_cli_build_ssn_mock
test_ssn_dataset_records_mark_sensitive
```

### 19.2 Credit-card tests

```text
test_credit_card_normalizer_plain_digits
test_credit_card_normalizer_grouped_digits
test_credit_card_normalizer_spoken_digits
test_luhn_valid_known_synthetic_number
test_luhn_invalid_number
test_credit_card_generator_uses_test_or_synthetic_values
test_credit_card_rejects_potentially_real_policy_violation
test_cli_build_credit_card_mock
test_credit_card_dataset_records_mark_sensitive
test_credit_card_generation_does_not_include_cvv_expiration_or_pin
```

### 19.3 Paper-method tests

```text
test_pipeline_builds_value_pattern_pairs
test_balancer_regenerates_underfilled_pairs
test_consistency_checker_filters_invalid_transcripts
test_pattern_registry_supports_general_and_entity_specific_patterns
test_direct_answer_scope_rejects_refusal_when_strict
```

### 19.4 Code policy tests

```text
test_no_dataclasses_imported
test_no_direct_environment_variable_reads
test_all_public_functions_are_typed
```

---

## 20. GitHub Actions

Keep the same workflows:

```text
.github/workflows/ci.yml
.github/workflows/publish.yml
.github/workflows/codeql.yml
.github/workflows/release-check.yml
.github/dependabot.yml
```

CI must run:

```bash
uv sync --all-extras --dev --frozen
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv build
```

---

## 21. Acceptance criteria

The implementation is complete when this passes:

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv build
test -f .env.example
```

And these smoke tests work without network calls:

```bash
uv run spokenforms init --output demo
cd demo

uv run spokenforms build \
  --config config.yaml \
  --entity ssn \
  --num-values 3 \
  --target-per-pattern 2 \
  --provider mock \
  --output-dir runs/demo_ssn

uv run spokenforms build \
  --config config.yaml \
  --entity credit_card_number \
  --num-values 3 \
  --target-per-pattern 2 \
  --provider mock \
  --output-dir runs/demo_credit_card

uv run spokenforms stats --dataset runs/demo_ssn/dataset.jsonl
uv run spokenforms stats --dataset runs/demo_credit_card/dataset.jsonl
```

Expected output for each run:

```text
manifest.json
config.resolved.yaml
values.jsonl
candidates.jsonl
validated.jsonl
dataset.jsonl
dataset.csv
dataset.parquet
stats.json
stats.md
logs.jsonl
```

---

## 22. Implementation order

```text
1. pyproject.toml, uv setup, src layout
2. Pydantic models
3. pydantic-settings environment model
4. Config loader and precedence handling
5. Typer CLI shell
6. Entity registry
7. Pattern registry
8. Sensitive data policy models
9. SSN normalizer and synthetic generator
10. Credit-card normalizer, Luhn validator, and synthetic generator
11. Mock provider
12. JSON parser
13. General normalizers
14. Value generator
15. Transcript generator
16. Consistency checker
17. Balancer
18. End-to-end build pipeline
19. Exporters
20. Stats
21. Split command
22. Resume support
23. OpenAI provider
24. Tests
25. GitHub Actions
26. README, SECURITY, CONTRIBUTING, CHANGELOG
27. PyPI release workflow
```

The key update is that SpokenForms should now implement the paper’s method as a first-class architecture: **schema-driven values, value × pattern generation, controlled spoken transcript synthesis, consistency filtering, recursive balancing, direct-answer scope, modular general/entity-specific patterns, and optional future prompt optimization**. SSN and credit-card support should be implemented with strict synthetic-only safeguards.
