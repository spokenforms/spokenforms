from __future__ import annotations

from spokenforms.models import EntitySpec


def build_value_generation_prompt(entity: EntitySpec, count: int) -> str:
    return f"Generate {count} values for {entity.field_name}: {entity.field_description}"
