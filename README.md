<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://dummyimage.com/1200x280/111827/f9fafb&text=SpokenForms">
    <img alt="SpokenForms" src="https://dummyimage.com/1200x280/f8fafc/111827&text=SpokenForms">
  </picture>
</p>

<p align="center">
  <strong>Synthetic spoken transcript variants for structured entity extraction.</strong>
</p>

<p align="center">
  <a href="https://github.com/aashsach/spokenforms/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/badge/ci-ruff%20%7C%20mypy%20%7C%20pytest-2563eb"></a>
  <a href="https://pypi.org/project/spokenforms/"><img alt="PyPI" src="https://img.shields.io/badge/pypi-spokenforms-0f766e"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.12%2B-111827">
  <img alt="Typed" src="https://img.shields.io/badge/typed-py.typed-7c3aed">
  <img alt="Coverage" src="https://img.shields.io/badge/coverage-94.92%25-16a34a">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-0f172a">
</p>

---

## The Problem

Voice AI systems do not fail only because they miss words. They fail because structured
values are spoken in messy, inconsistent, human ways.

```text
ZIP code:
  94101
  nine four one zero one
  nine four one oh one
  ninety four one oh one

SSN:
  900-12-3456
  nine zero zero, one two, three four five six
  nine zero zero dash one two dash three four five six

Credit card:
  4242 4242 4242 4242
  four two four two, four two four two, four two four two, four two four two
```

Real phone transcripts are private, expensive, sparse, and slow to annotate. SpokenForms
lets teams generate synthetic direct-answer data before production transcripts exist,
then validate every transcript back to the intended canonical value.

## What It Builds

```text
canonical structured value
  -> verbalization patterns
  -> phone-call-style transcript candidates
  -> deterministic consistency validation
  -> JSONL / CSV / Parquet dataset
```

SpokenForms is built around the LingVarBench-style three-stage pipeline:

| Stage | Job |
| --- | --- |
| Value Generator | Creates canonical values for an entity schema. |
| Transcript Generator | Applies reusable and entity-specific spoken patterns. |
| Consistency Checker | Keeps only transcripts recoverable to the intended value. |

## Install

```bash
uv add spokenforms
```

For local development:

```bash
uv sync --all-extras --dev
```

If you use OpenAI later, put credentials in `.env`. The mock provider works offline and
does not need network access.

## Quick Start

```bash
uv run spokenforms init --output demo
cd demo

uv run spokenforms build \
  --config config.yaml \
  --entity ssn \
  --provider mock \
  --num-values 3 \
  --target-per-pattern 2 \
  --output-dir runs/demo_ssn
```

Expected output:

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

## Generated Examples

These examples were generated from this package with:

```bash
uv run spokenforms build --entity ssn --provider mock --num-values 1 --target-per-pattern 1
uv run spokenforms build --entity credit_card_number --provider mock --num-values 1 --target-per-pattern 1
```

### Synthetic SSN

| Ground truth | Pattern | Generated transcript |
| --- | --- | --- |
| `900-12-3456` | `direct_and_simple` | `nine zero zero, one two, three four five six` |
| `900-12-3456` | `filler_words` | `Um, it is nine zero zero, one two, three four five six.` |
| `900-12-3456` | `formal` | `The Social Security number is nine zero zero, one two, three four five six.` |

All records are tagged:

```json
{
  "synthetic_sensitive_value": true,
  "sensitive_type": "ssn",
  "real_world_safe": true,
  "generation_mode": "reserved_or_invalid"
}
```

### Payment-Test Card Number

| Ground truth | Pattern | Generated transcript |
| --- | --- | --- |
| `4242424242424242` | `direct_and_simple` | `four two four two, four two four two, four two four two, four two four two` |
| `4242424242424242` | `filler_words` | `Um, it is four two four two, four two four two, four two four two, four two four two.` |
| `4242424242424242` | `card_correction` | `one two four, sorry, four two four two, four two four two, four two four two, four two four two.` |

All card records are tagged:

```json
{
  "synthetic_sensitive_value": true,
  "sensitive_type": "credit_card_number",
  "real_world_safe": true,
  "generation_mode": "payment_test_numbers"
}
```

### Generated Stats

```text
SSN run:
  total records: 16
  total patterns: 16
  validation pass rate: 100.00%
  sensitive synthetic records: 16

Credit-card run:
  total records: 21
  total patterns: 21
  validation pass rate: 100.00%
  sensitive synthetic records: 21
```

## Built-In Entities

```text
confirmation_code       account_number          member_id
claim_id                policy_number           zip_code
date_of_birth           full_name               phone_number
ssn                     credit_card_number      boolean_answer
enum_answer             multi_select_answer     pain_rating
respiratory_issues      hearing_issues
```

## Pattern Inventory

General patterns:

```text
direct_and_simple  filler_words  hesitation  correction  repetition
formal             casual        polite      confident   uncertain
confirmation       digit_by_digit grouped_two grouped_four nato_letters
```

Sensitive entity patterns:

```text
ssn_grouped_3_2_4
ssn_digit_by_digit
ssn_with_dashes
ssn_correction
ssn_repetition_for_confirmation

card_grouped_4_4_4_4
card_digit_by_digit
card_with_spaces
card_last_four_repetition
card_correction
card_issuer_style_grouping
```

## Safety Model

SpokenForms is synthetic-first.

| Entity | Default mode | Real-world data? |
| --- | --- | --- |
| `ssn` | `reserved_or_invalid` | No |
| `credit_card_number` | `payment_test_numbers` | No |

Unsafe generation flags are reserved in the CLI but intentionally rejected in v0.1:

```bash
spokenforms build --entity ssn --allow-potentially-real-sensitive-values
# exits with an error
```

## CLI

```bash
spokenforms init --output demo

spokenforms build \
  --config config.yaml \
  --entity credit_card_number \
  --provider mock \
  --num-values 3 \
  --target-per-pattern 2 \
  --output-dir runs/cards

spokenforms stats runs/cards/dataset.jsonl
```

## Python API

```python
from spokenforms.config import apply_cli_overrides, default_config
from spokenforms.generation import run_pipeline
from spokenforms.models import ProviderName
from spokenforms.providers import create_provider

config = apply_cli_overrides(
    default_config(),
    provider=ProviderName.MOCK,
    num_values=2,
    target_per_pattern=2,
    output_dir=None,
)
provider = create_provider(ProviderName.MOCK, "mock")
result = run_pipeline("readme-demo", "ssn", config, provider)

print(result.records[0].transcript)
```

## Test Cases

The repository ships with checks for:

| Area | Covered behavior |
| --- | --- |
| CLI | `init`, `build`, `stats`, unsafe flag rejection |
| Generation | mock value generation, pattern application, balancing |
| Validation | deterministic consistency checks |
| Normalization | numbers, alphanumeric values, SSN, card numbers, dates, names, enums, booleans |
| Safety | synthetic-only sensitive policy enforcement |
| Storage | JSONL, CSV, Parquet, manifest, stats |
| Packaging | Ruff, mypy strict mode, coverage, wheel/sdist build |

Run the full suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv build
```

Current local verification:

```text
ruff:   passing
format: passing
mypy:   passing
pytest: 5 passed, 94.92% coverage
build:  wheel and sdist generated
```

## Release Slugs

| Release | Slug | Theme |
| --- | --- | --- |
| `0.1.0` | `safe-synthetic-seed` | Offline mock generation, typed package, synthetic SSN/card guardrails |
| `0.2.0` | `provider-lift` | OpenAI provider, richer prompt contracts, retry/cache hardening |
| `0.3.0` | `bench-runner` | Evaluation harnesses, train/validation/test workflows, extraction prompt baselines |
| `1.0.0` | `voice-data-foundry` | Stable API for production synthetic transcript generation |

## Roadmap

- OpenAI provider implementation.
- User-defined entity and pattern YAML loading.
- Richer consistency checking for correction-style transcripts.
- DSPy/SIMBA prompt optimization hooks.
- More locale-specific readout styles.
- Larger generated example gallery.

## Project Layout

```text
src/spokenforms/
  cli.py
  config.py
  models.py
  providers/
  generation/
  patterns/
  entities/
  normalizers/
  validators/
  storage/
  stats/
tests/
examples/
```

## License

MIT. See [LICENSE](LICENSE).
