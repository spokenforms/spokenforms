from __future__ import annotations

from spokenforms.entities.builtins import built_in_entities
from spokenforms.models import EntitySpec


class EntityRegistry:
    def __init__(self, entities: list[EntitySpec] | None = None) -> None:
        self._entities = {entity.entity_id: entity for entity in entities or built_in_entities()}

    def get(self, entity_id: str) -> EntitySpec:
        return self._entities[entity_id]

    def all(self) -> list[EntitySpec]:
        return list(self._entities.values())

    def ids(self) -> list[str]:
        return sorted(self._entities)
