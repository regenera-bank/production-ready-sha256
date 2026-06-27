from __future__ import annotations
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ControlEvidence:
    evidence_id: str
    sha256: str
    collected_at: date


@dataclass(frozen=True, slots=True)
class ControlException:
    exception_id: str
    approved_by: str
    expires_at: date


@dataclass(frozen=True, slots=True)
class Control:
    control_id: str
    owner: str
    blocking: bool
    review_due: date
    evidence: tuple[ControlEvidence, ...]
    exception: ControlException | None = None


@dataclass(frozen=True, slots=True)
class ControlResult:
    effective: bool
    blocking: bool
    reasons: tuple[str, ...]


class ControlEvaluator:
    def evaluate(self, control: Control, today: date) -> ControlResult:
        reasons: list[str] = []
        if not control.owner.strip():
            reasons.append('OWNER_MISSING')
        if control.review_due < today:
            reasons.append('CONTROL_REVIEW_EXPIRED')
        if not control.evidence:
            reasons.append('EVIDENCE_MISSING')
        elif any(len(item.sha256) != 64 for item in control.evidence):
            reasons.append('EVIDENCE_HASH_INVALID')
        if control.exception:
            if not control.exception.approved_by.strip():
                reasons.append('EXCEPTION_APPROVER_MISSING')
            if control.exception.expires_at < today:
                reasons.append('EXCEPTION_EXPIRED')
        return ControlResult(not reasons, control.blocking and bool(reasons), tuple(reasons))
