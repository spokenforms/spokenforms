from __future__ import annotations


def build_consistency_check_prompt(value: str, transcript: str) -> str:
    return f"Does this transcript express {value}? {transcript}"
