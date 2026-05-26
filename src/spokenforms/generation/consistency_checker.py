from __future__ import annotations

from spokenforms.models import ConsistencyResult, EntitySpec, TranscriptCandidate
from spokenforms.normalizers import normalizer_for


def check_consistency(entity: EntitySpec, candidate: TranscriptCandidate) -> ConsistencyResult:
    normalize = normalizer_for(entity.entity_id, entity.output_type)
    extracted = normalize(candidate.transcript)
    expected = candidate.normalized_ground_truth
    passed = expected == extracted or expected in extracted
    return ConsistencyResult(
        passed=passed,
        method="deterministic",
        reason="normalized transcript contains the expected value" if passed else "value mismatch",
        extracted_value=candidate.transcript,
        normalized_extracted_value=extracted,
        confidence=1.0 if passed else 0.0,
    )
