from __future__ import annotations


def build_extraction_prompt(entity_id: str, transcript: str) -> str:
    return f"Extract {entity_id} from: {transcript}"
