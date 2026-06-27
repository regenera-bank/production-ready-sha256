from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime

class GovernanceError(Exception):
    pass

@dataclass(frozen=True)
class Approval:
    author: str
    approver: str
    signed: bool

@dataclass(frozen=True)
class ExceptionRecord:
    control_id: str
    requester: str
    approver: str
    expires_at: date
    compensating_control: str

@dataclass(frozen=True)
class ControlEvidence:
    control_id: str
    owner_id: str
    evidence_paths: tuple[str, ...]
    expires_at: date | None = None


def validate_approval(approval: Approval) -> None:
    if approval.author == approval.approver:
        raise GovernanceError('self approval')
    if not approval.signed:
        raise GovernanceError('unsigned approval')


def validate_exception(record: ExceptionRecord, today: date) -> None:
    if record.requester == record.approver:
        raise GovernanceError('self approved exception')
    if record.expires_at <= today:
        raise GovernanceError('expired exception')
    if not record.compensating_control.strip():
        raise GovernanceError('missing compensating control')


def evaluate_control(record: ControlEvidence, active_owners: set[str], today: date) -> str:
    if record.owner_id not in active_owners:
        return 'INEFFECTIVE_OWNER_MISSING'
    if not record.evidence_paths:
        return 'INEFFECTIVE_EVIDENCE_MISSING'
    if record.expires_at and record.expires_at < today:
        return 'INEFFECTIVE_EXPIRED'
    return 'EFFECTIVE'
