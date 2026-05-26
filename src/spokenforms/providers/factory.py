from __future__ import annotations

from spokenforms.models import ProviderName
from spokenforms.providers.base import LLMProvider
from spokenforms.providers.mock_provider import MockProvider
from spokenforms.providers.openai_provider import OpenAIProvider


def create_provider(provider: ProviderName, model: str) -> LLMProvider:
    if provider is ProviderName.MOCK:
        return MockProvider()
    return OpenAIProvider(model=model)
