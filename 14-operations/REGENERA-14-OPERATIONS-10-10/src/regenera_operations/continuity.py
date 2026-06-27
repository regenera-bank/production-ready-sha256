from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .errors import ValidationError, StateTransitionError, AuthorizationError
from .utils import require_aware, require_sha256

@dataclass(frozen=True, slots=True)
class ServiceObjective:
    service: str
    rto_minutes: int
    rpo_minutes: int

    def __post_init__(self) -> None:
        if not self.service.strip() or self.rto_minutes <= 0 or self.rpo_minutes < 0:
            raise ValidationError("objetivo de continuidade inválido")

@dataclass(slots=True)
class ContinuityExercise:
    exercise_id: str
    owner_id: str
    objective: ServiceObjective
    started_at: datetime
    recovery_minutes: int | None = None
    data_loss_minutes: int | None = None
    reconciliation_complete: bool = False
    evidence_digest: str | None = None
    reviewer_id: str | None = None

    def __post_init__(self) -> None:
        require_aware(self.started_at, "started_at")
        if not self.exercise_id.strip() or not self.owner_id.strip():
            raise ValidationError("exercício incompleto")

    def conclude(self, recovery_minutes: int, data_loss_minutes: int, reconciled: bool, evidence_digest: str, reviewer_id: str) -> None:
        if recovery_minutes < 0 or data_loss_minutes < 0:
            raise ValidationError("medição inválida")
        if reviewer_id == self.owner_id:
            raise AuthorizationError("revisão independente obrigatória")
        require_sha256(evidence_digest, "evidence_digest")
        self.recovery_minutes=recovery_minutes
        self.data_loss_minutes=data_loss_minutes
        self.reconciliation_complete=reconciled
        self.evidence_digest=evidence_digest
        self.reviewer_id=reviewer_id
        if not reconciled:
            raise StateTransitionError("continuidade sem reconciliação")
        if recovery_minutes > self.objective.rto_minutes:
            raise StateTransitionError("RTO violado")
        if data_loss_minutes > self.objective.rpo_minutes:
            raise StateTransitionError("RPO violado")

    @property
    def passed(self) -> bool:
        return all(v is not None for v in (self.recovery_minutes, self.data_loss_minutes, self.evidence_digest, self.reviewer_id)) and self.reconciliation_complete
