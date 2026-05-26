from __future__ import annotations

from spokenforms.models import EntitySpec, ProviderName, VerbalizationPattern
from spokenforms.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = ProviderName.OPENAI

    def __init__(self, model: str) -> None:
        self.model = model

    def generate_values(self, entity: EntitySpec, count: int) -> list[str]:
        msg = (
            "OpenAI generation is not implemented in this offline v0.1 slice. Use --provider mock."
        )
        raise NotImplementedError(msg)

    def generate_transcript(
        self,
        entity: EntitySpec,
        value: str,
        pattern: VerbalizationPattern,
        attempt: int,
    ) -> str:
        msg = (
            "OpenAI generation is not implemented in this offline v0.1 slice. Use --provider mock."
        )
        raise NotImplementedError(msg)
