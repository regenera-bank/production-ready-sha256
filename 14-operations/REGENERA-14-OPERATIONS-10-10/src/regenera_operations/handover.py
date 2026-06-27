from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .errors import ValidationError, AuthorizationError, StateTransitionError
from .utils import require_aware, require_sha256

@dataclass(frozen=True, slots=True)
class HandoverItem:
    reference: str
    owner_id: str
    next_action: str
    critical: bool = False

@dataclass(slots=True)
class ShiftHandover:
    handover_id: str
    outgoing_id: str
    started_at: datetime
    items: tuple[HandoverItem, ...]
    acknowledged_by: str | None = None
    evidence_digest: str | None = None

    def __post_init__(self) -> None:
        require_aware(self.started_at, "started_at")
        if not self.handover_id.strip() or not self.outgoing_id.strip():
            raise ValidationError("handover inválido")
        for item in self.items:
            if not item.reference.strip() or not item.owner_id.strip() or not item.next_action.strip():
                raise ValidationError("item de handover incompleto")

    def acknowledge(self, incoming_id: str, evidence_digest: str) -> None:
        if incoming_id == self.outgoing_id:
            raise AuthorizationError("passagem de turno exige outro operador")
        require_sha256(evidence_digest, "evidence_digest")
        if any(item.critical and not item.next_action.strip() for item in self.items):
            raise StateTransitionError("item crítico sem próxima ação")
        self.acknowledged_by=incoming_id
        self.evidence_digest=evidence_digest
