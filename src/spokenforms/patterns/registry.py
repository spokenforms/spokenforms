from __future__ import annotations

from spokenforms.models import VerbalizationPattern
from spokenforms.patterns.builtins import built_in_patterns


class PatternRegistry:
    def __init__(self, patterns: list[VerbalizationPattern] | None = None) -> None:
        self._patterns = {
            pattern.pattern_id: pattern for pattern in patterns or built_in_patterns()
        }

    def for_entity(self, entity_id: str) -> list[VerbalizationPattern]:
        return [
            pattern
            for pattern in self._patterns.values()
            if pattern.enabled and (pattern.scope == "general" or entity_id in pattern.entity_ids)
        ]

    def ids(self) -> list[str]:
        return sorted(self._patterns)
