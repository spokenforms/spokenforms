from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from spokenforms.models import ProviderName


class SpokenFormsSettings(BaseSettings):
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
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
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
    return SpokenFormsSettings()
