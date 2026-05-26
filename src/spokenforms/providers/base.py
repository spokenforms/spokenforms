from __future__ import annotations

from abc import ABC, abstractmethod

from spokenforms.models import EntitySpec, ProviderName, VerbalizationPattern


class LLMProvider(ABC):
    name: ProviderName
    model: str

    @abstractmethod
    def generate_values(self, entity: EntitySpec, count: int) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def generate_transcript(
        self,
        entity: EntitySpec,
        value: str,
        pattern: VerbalizationPattern,
        attempt: int,
    ) -> str:
        raise NotImplementedError
