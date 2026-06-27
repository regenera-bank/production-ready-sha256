from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from .access import Approval, ApprovalPolicy
from .errors import StateTransitionError, ValidationError, AuthorizationError
from .utils import digest, require_aware, require_sha256

class ChangeRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ChangeState(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"
    ROLLED_BACK = "ROLLED_BACK"

@dataclass(slots=True)
class ChangeRequest:
    change_id: str
    requester_id: str
    description: str
    risk: ChangeRisk
    rollback_plan: str
    state: ChangeState = ChangeState.DRAFT
    approval: Approval | None = None
    scheduled_at: datetime | None = None
    evidence: list[str] = field(default_factory=list)
    emergency: bool = False
    retrospective_digest: str | None = None
    executor_id: str | None = None

    def __post_init__(self) -> None:
        if not all(v.strip() for v in (self.change_id, self.requester_id, self.description, self.rollback_plan)):
            raise ValidationError("mudança incompleta")

    def payload_digest(self) -> str:
        return digest({"change_id": self.change_id, "description": self.description, "risk": self.risk.value, "rollback_plan": self.rollback_plan})

    def approve(self, approval: Approval, now: datetime) -> None:
        if self.state != ChangeState.DRAFT:
            raise StateTransitionError("mudança não está em rascunho")
        ApprovalPolicy.validate(approval, self.payload_digest(), now)
        if approval.requester_id != self.requester_id:
            raise AuthorizationError("solicitante da aprovação divergente")
        self.approval = approval
        self.state = ChangeState.APPROVED

    def schedule(self, when: datetime, blackout: bool = False) -> None:
        require_aware(when, "scheduled_at")
        if self.state != ChangeState.APPROVED:
            raise StateTransitionError("mudança não aprovada")
        if blackout and not self.emergency:
            raise StateTransitionError("janela de bloqueio")
        self.scheduled_at = when
        self.state = ChangeState.SCHEDULED

    def start(self, actor_id: str) -> None:
        if self.state != ChangeState.SCHEDULED:
            raise StateTransitionError("mudança não agendada")
        if self.approval and actor_id == self.approval.approver_id:
            raise AuthorizationError("aprovador não executa a mudança")
        self.executor_id = actor_id
        self.state = ChangeState.EXECUTING

    def verify(self, evidence_digest: str, reconciled: bool) -> None:
        if self.state != ChangeState.EXECUTING:
            raise StateTransitionError("mudança não está em execução")
        require_sha256(evidence_digest, "evidence_digest")
        if not reconciled:
            raise StateTransitionError("verificação sem reconciliação")
        self.evidence.append(evidence_digest)
        self.state = ChangeState.VERIFIED

    def close(self, reviewer_id: str) -> None:
        if self.state != ChangeState.VERIFIED:
            raise StateTransitionError("mudança não verificada")
        if reviewer_id in {self.requester_id, self.approval.approver_id if self.approval else None, self.executor_id}:
            raise AuthorizationError("fechamento exige independência")
        if self.emergency:
            if not self.retrospective_digest:
                raise StateTransitionError("mudança emergencial exige retrospectiva")
            require_sha256(self.retrospective_digest, "retrospective_digest")
        self.state = ChangeState.CLOSED

    def rollback(self, evidence_digest: str) -> None:
        if self.state not in {ChangeState.EXECUTING, ChangeState.VERIFIED}:
            raise StateTransitionError("rollback fora de estado")
        require_sha256(evidence_digest, "evidence_digest")
        self.evidence.append(evidence_digest)
        self.state = ChangeState.ROLLED_BACK
