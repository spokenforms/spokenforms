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
