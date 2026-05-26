from __future__ import annotations

from spokenforms.models import EntitySpec
from spokenforms.validators.sensitive_policy import enforce_sensitive_policy


def validate_sensitive_entity(entity: EntitySpec) -> None:
    enforce_sensitive_policy(entity.sensitive_policy)
