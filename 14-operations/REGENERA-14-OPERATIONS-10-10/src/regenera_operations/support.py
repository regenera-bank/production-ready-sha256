from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from .money import Money
from .errors import ValidationError, AuthorizationError, StateTransitionError
from .utils import require_sha256

_ALLOWED_FIELDS={"customer_id","channel","category","summary","correlation_id"}

class CaseState(str, Enum):
    OPEN="OPEN"
    INVESTIGATING="INVESTIGATING"
    RESOLVED="RESOLVED"
    CLOSED="CLOSED"

@dataclass(slots=True)
class SupportCase:
    case_id: str
    owner_id: str
    data: dict[str,object]
    state: CaseState=CaseState.OPEN
    evidence: list[str]=field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.case_id.strip() or not self.owner_id.strip():
            raise ValidationError("caso inválido")
        forbidden=set(self.data)-_ALLOWED_FIELDS
        if forbidden:
            raise ValidationError("dados fora da allowlist")

    def investigate(self) -> None:
        if self.state != CaseState.OPEN:
            raise StateTransitionError("caso não está aberto")
        self.state=CaseState.INVESTIGATING

    def resolve(self, evidence_digest: str) -> None:
        if self.state != CaseState.INVESTIGATING:
            raise StateTransitionError("caso não está em investigação")
        require_sha256(evidence_digest, "evidence_digest")
        self.evidence.append(evidence_digest)
        self.state=CaseState.RESOLVED

    def close(self, reviewer_id: str) -> None:
        if self.state != CaseState.RESOLVED:
            raise StateTransitionError("caso não está resolvido")
        if reviewer_id == self.owner_id:
            raise AuthorizationError("fechamento exige revisão independente")
        self.state=CaseState.CLOSED

@dataclass(frozen=True, slots=True)
class RefundRequest:
    request_id: str
    requester_id: str
    approver_id: str
    amount: Money
    evidence_digest: str

    def validate(self, limit_minor: int) -> None:
        self.amount.positive()
        require_sha256(self.evidence_digest, "evidence_digest")
        if self.requester_id == self.approver_id:
            raise AuthorizationError("reembolso não permite autoaprovação")
        if self.amount.minor > limit_minor:
            raise AuthorizationError("reembolso acima da alçada")
