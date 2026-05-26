from __future__ import annotations

from spokenforms.exceptions import SensitivePolicyError
from spokenforms.models import SensitiveDataPolicy, SensitiveType


def enforce_sensitive_policy(policy: SensitiveDataPolicy) -> None:
    if policy.sensitive_type is SensitiveType.NONE:
        return
    if policy.allow_potentially_real_values:
        msg = "Unsafe sensitive-value generation is reserved but not implemented for v0.1."
        raise SensitivePolicyError(msg)
    if not policy.synthetic_sensitive_value or not policy.real_world_safe:
        msg = "Sensitive values must be marked synthetic and real-world safe."
        raise SensitivePolicyError(msg)
