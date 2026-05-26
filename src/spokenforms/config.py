from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from spokenforms.models import (
    AppConfig,
    CacheConfig,
    ExportConfig,
    GenerationConfig,
    LLMConfig,
    ProjectConfig,
    ProviderName,
    ValidationConfig,
)
from spokenforms.settings import SpokenFormsSettings, load_settings


def default_config(settings: SpokenFormsSettings | None = None) -> AppConfig:
    loaded = settings or load_settings()
    return AppConfig(
        project=ProjectConfig(
            name=loaded.project_name,
            output_dir=loaded.output_dir,
            random_seed=loaded.random_seed,
        ),
        llm=LLMConfig(
            provider=loaded.llm_provider,
            model=loaded.openai_model,
            temperature=loaded.temperature,
            top_p=loaded.top_p,
            max_output_tokens=loaded.max_output_tokens,
            timeout_seconds=loaded.timeout_seconds,
            max_retries=loaded.max_retries,
            concurrency=loaded.concurrency,
        ),
        generation=GenerationConfig(),
        validation=ValidationConfig(),
        export=ExportConfig(),
        cache=CacheConfig(enabled=loaded.cache_enabled, directory=loaded.cache_dir),
    )


def load_config(path: Path | None) -> AppConfig:
    config = default_config()
    if path is None:
        return config
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        msg = f"Config at {path} must be a mapping."
        raise ValueError(msg)
    merged = _deep_merge(config.model_dump(mode="python"), data)
    return AppConfig.model_validate(merged)


def apply_cli_overrides(
    config: AppConfig,
    provider: ProviderName | None,
    num_values: int | None,
    target_per_pattern: int | None,
    output_dir: Path | None,
) -> AppConfig:
    data = config.model_dump(mode="python")
    if provider is not None:
        data["llm"]["provider"] = provider
        if provider is ProviderName.MOCK:
            data["llm"]["model"] = "mock"
    if num_values is not None:
        data["generation"]["num_values"] = num_values
    if target_per_pattern is not None:
        data["generation"]["target_per_pattern"] = target_per_pattern
    if output_dir is not None:
        data["project"]["output_dir"] = output_dir
    return AppConfig.model_validate(data)


def write_default_config(path: Path) -> None:
    config = default_config()
    payload = yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False)
    path.write_text(payload, encoding="utf-8")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
