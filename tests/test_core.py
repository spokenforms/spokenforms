from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from spokenforms.cli import app
from spokenforms.config import apply_cli_overrides, default_config, load_config
from spokenforms.entities import EntityRegistry
from spokenforms.exceptions import SensitivePolicyError
from spokenforms.models import OutputType, ProviderName, SensitiveDataPolicy, SensitiveType
from spokenforms.normalizers.alphanumeric import normalize_alphanumeric
from spokenforms.normalizers.booleans import normalize_boolean
from spokenforms.normalizers.credit_card import normalize_credit_card
from spokenforms.normalizers.dates import normalize_date
from spokenforms.normalizers.enums import normalize_enum
from spokenforms.normalizers.factory import normalizer_for
from spokenforms.normalizers.names import normalize_name
from spokenforms.normalizers.numbers import normalize_number_sequence
from spokenforms.normalizers.ssn import normalize_ssn
from spokenforms.patterns import PatternRegistry
from spokenforms.prompts.consistency_check import build_consistency_check_prompt
from spokenforms.prompts.extraction import build_extraction_prompt
from spokenforms.prompts.models import (
    ConsistencyCheckResponse,
    TranscriptGenerationResponse,
    TranscriptItem,
    ValueGenerationResponse,
)
from spokenforms.prompts.transcript_generation import build_transcript_generation_prompt
from spokenforms.prompts.value_generation import build_value_generation_prompt
from spokenforms.providers import create_provider
from spokenforms.providers.openai_provider import OpenAIProvider
from spokenforms.storage.cache import cache_path
from spokenforms.storage.jsonl import read_jsonl
from spokenforms.utils.hashing import stable_hash
from spokenforms.utils.json_parser import dump_json_line, parse_json_object
from spokenforms.utils.paths import ensure_dir
from spokenforms.utils.retry import call_once
from spokenforms.utils.text import compact_spaces, digits_only
from spokenforms.utils.time import utc_now
from spokenforms.validators.credit_card import is_payment_test_number, is_safe_synthetic_card
from spokenforms.validators.luhn import is_luhn_valid
from spokenforms.validators.sensitive_policy import enforce_sensitive_policy
from spokenforms.validators.ssn import is_safe_synthetic_ssn


def test_cli_init_and_build_mock(tmp_path: Path) -> None:
    runner = CliRunner()
    init_result = runner.invoke(app, ["init", "--output", str(tmp_path)])
    assert init_result.exit_code == 0

    output = tmp_path / "runs" / "ssn"
    build_result = runner.invoke(
        app,
        [
            "build",
            "--config",
            str(tmp_path / "config.yaml"),
            "--entity",
            "ssn",
            "--provider",
            "mock",
            "--num-values",
            "2",
            "--target-per-pattern",
            "2",
            "--output-dir",
            str(output),
        ],
    )
    assert build_result.exit_code == 0
    expected = {
        "manifest.json",
        "config.resolved.yaml",
        "values.jsonl",
        "candidates.jsonl",
        "validated.jsonl",
        "dataset.jsonl",
        "dataset.csv",
        "dataset.parquet",
        "stats.json",
        "stats.md",
        "logs.jsonl",
    }
    assert expected == {path.name for path in output.iterdir()}
    rows = read_jsonl(output / "dataset.jsonl")
    assert rows
    assert {row["entity_id"] for row in rows} == {"ssn"}

    stats_result = runner.invoke(app, ["stats", str(output / "dataset.jsonl")])
    assert stats_result.exit_code == 0
    assert "records:" in stats_result.stdout


def test_normalizers_and_validators() -> None:
    assert normalize_number_sequence("nine four one oh one") == "94101"
    assert normalize_alphanumeric("AB-123") == "AB123"
    assert normalize_ssn("nine zero zero one two three four five six") == "900-12-3456"
    assert normalize_credit_card("four two four two") == "4242"
    assert normalize_boolean("yeah") == "true"
    assert normalize_enum("  Option   A ") == "option a"
    assert normalize_date(" 01-02-1985 ") == "01-02-1985"
    assert normalize_name("jane smith") == "Jane Smith"
    assert is_luhn_valid("4242424242424242")
    assert is_payment_test_number("4242 4242 4242 4242")
    assert is_safe_synthetic_card("4242 4242 4242 4242")
    assert is_safe_synthetic_ssn("900-12-3456")


def test_registries_config_prompts_and_utils(tmp_path: Path) -> None:
    entities = EntityRegistry()
    ssn = entities.get("ssn")
    assert "ssn" in entities.ids()
    assert ssn in entities.all()
    patterns = PatternRegistry().for_entity("ssn")
    assert any(pattern.pattern_id == "ssn_grouped_3_2_4" for pattern in patterns)

    config = default_config()
    overridden = apply_cli_overrides(config, ProviderName.MOCK, 3, 2, tmp_path)
    assert overridden.llm.provider is ProviderName.MOCK
    assert load_config(None).project.name
    assert "Generate 2 values" in build_value_generation_prompt(ssn, 2)
    assert "Pattern:" in build_transcript_generation_prompt(ssn, "900-12-3456", patterns[0])
    assert "Does this transcript" in build_consistency_check_prompt("x", "x")
    assert "Extract ssn" in build_extraction_prompt("ssn", "nine zero zero")

    assert ValueGenerationResponse(values=["x"]).values == ["x"]
    transcript_response = TranscriptGenerationResponse(
        transcripts=[TranscriptItem(transcript="x", variation_types=["direct"])]
    )
    assert transcript_response.transcripts[0].transcript == "x"
    assert ConsistencyCheckResponse(passed=True, reason="ok", confidence=1.0).confidence == 1.0

    assert digits_only("a1-b2") == "12"
    assert compact_spaces("a   b") == "a b"
    assert parse_json_object('{"a":1}') == {"a": 1}
    with pytest.raises(ValueError):
        parse_json_object("[1]")
    assert dump_json_line({"a": 1}).endswith("\n")
    assert len(stable_hash("x")) == 64
    assert ensure_dir(tmp_path / "nested").exists()
    assert cache_path(tmp_path, "abc").name == "abc.json"
    assert call_once(lambda: "ok") == "ok"
    assert utc_now().tzinfo is not None

    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        "generation:\n  num_values: 4\nproject:\n  name: configured\n",
        encoding="utf-8",
    )
    loaded = load_config(cfg_path)
    assert loaded.generation.num_values == 4
    assert loaded.project.name == "configured"

    invalid_cfg = tmp_path / "bad.yaml"
    invalid_cfg.write_text("- not-a-map\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(invalid_cfg)


def test_provider_and_policy_edges() -> None:
    mock = create_provider(ProviderName.MOCK, "mock")
    ssn = EntityRegistry().get("ssn")
    pattern = PatternRegistry().for_entity("ssn")[0]
    value = mock.generate_values(ssn, 1)[0]
    assert value
    assert mock.generate_transcript(ssn, value, pattern, 2) != mock.generate_transcript(
        ssn,
        value,
        pattern,
        1,
    )
    assert create_provider(ProviderName.OPENAI, "gpt-test").model == "gpt-test"

    entities = EntityRegistry()
    for entity_id in [
        "credit_card_number",
        "zip_code",
        "boolean_answer",
        "date_of_birth",
        "full_name",
        "confirmation_code",
    ]:
        entity = entities.get(entity_id)
        assert mock.generate_values(entity, 1)[0]

    card = entities.get("credit_card_number")
    card_patterns = {item.pattern_id: item for item in PatternRegistry().for_entity(card.entity_id)}
    for pattern_id in [
        "card_digit_by_digit",
        "card_with_spaces",
        "card_last_four_repetition",
        "card_correction",
        "formal",
        "casual",
        "polite",
        "uncertain",
        "confirmation",
    ]:
        transcript = mock.generate_transcript(
            card, "4242424242424242", card_patterns[pattern_id], 1
        )
        assert transcript

    assert normalizer_for("ssn", OutputType.SENSITIVE_NUMERIC_SEQUENCE)("900123456")
    assert normalizer_for("credit_card_number", OutputType.SENSITIVE_NUMERIC_SEQUENCE)("4242")
    assert normalizer_for("confirmation_code", OutputType.ALPHANUMERIC)("AB123") == "AB123"
    assert normalizer_for("boolean_answer", OutputType.BOOLEAN)("no") == "false"
    assert normalizer_for("enum_answer", OutputType.ENUM)("A") == "a"
    assert normalizer_for("date_of_birth", OutputType.DATE)("x") == "x"
    assert normalizer_for("full_name", OutputType.STRING)("jane smith") == "Jane Smith"
    assert normalizer_for("zip_code", OutputType.NUMERIC_SEQUENCE)("one two") == "12"

    openai_provider = OpenAIProvider("gpt-test")
    with pytest.raises(NotImplementedError):
        openai_provider.generate_values(ssn, 1)
    with pytest.raises(NotImplementedError):
        openai_provider.generate_transcript(ssn, "900-12-3456", pattern, 1)

    unsafe = SensitiveDataPolicy(
        sensitive_type=SensitiveType.SSN,
        synthetic_sensitive_value=True,
        allow_potentially_real_values=True,
    )
    with pytest.raises(SensitivePolicyError):
        enforce_sensitive_policy(unsafe)
    enforce_sensitive_policy(SensitiveDataPolicy())
    with pytest.raises(SensitivePolicyError):
        enforce_sensitive_policy(
            SensitiveDataPolicy(sensitive_type=SensitiveType.SSN, synthetic_sensitive_value=False)
        )


def test_cli_unsafe_flag_rejected() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "build",
            "--entity",
            "ssn",
            "--allow-potentially-real-sensitive-values",
        ],
    )
    assert result.exit_code == 2
