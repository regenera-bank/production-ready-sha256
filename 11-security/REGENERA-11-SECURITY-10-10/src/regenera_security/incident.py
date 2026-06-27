from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone

from .errors import InvalidTransition, SecurityControlError


_ALLOWED = {
    "DECLARED": {"TRIAGED"},
    "TRIAGED": {"CONTAINED"},
    "CONTAINED": {"ERADICATED"},
    "ERADICATED": {"RECOVERED"},
    "RECOVERED": {"CLOSED"},
    "CLOSED": set(),
}


@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    owner_id: str
    severity: str
    state: str
    declared_at: datetime
    evidence_ids: tuple[str, ...] = ()
    root_cause: str = ""
    containment: str = ""
    recovery_validation: str = ""
    closure_approver_id: str = ""

    @classmethod
    def declare(cls, incident_id: str, owner_id: str, severity: str, *, now: datetime | None = None) -> "Incident":
        if severity not in {"SEV1", "SEV2", "SEV3", "SEV4"}:
            raise SecurityControlError("severidade de incidente inválida")
        if not incident_id.strip() or not owner_id.strip():
            raise SecurityControlError("incidente sem id ou owner")
        return cls(incident_id, owner_id, severity, "DECLARED", now or datetime.now(timezone.utc))

    def add_evidence(self, evidence_id: str) -> "Incident":
        if not evidence_id.strip():
            raise SecurityControlError("evidência vazia")
        if evidence_id in self.evidence_ids:
            return self
        return replace(self, evidence_ids=self.evidence_ids+(evidence_id,))

    def transition(self, new_state: str, **fields: str) -> "Incident":
        if new_state not in _ALLOWED.get(self.state, set()):
            raise InvalidTransition(f"transição inválida: {self.state}->{new_state}")
        candidate=replace(self,state=new_state,**fields)
        if new_state == "CONTAINED" and not candidate.containment.strip():
            raise InvalidTransition("contenção obrigatória")
        if new_state == "ERADICATED" and not candidate.root_cause.strip():
            raise InvalidTransition("causa raiz obrigatória")
        if new_state == "RECOVERED" and not candidate.recovery_validation.strip():
            raise InvalidTransition("validação de recuperação obrigatória")
        if new_state == "CLOSED":
            if not candidate.evidence_ids:
                raise InvalidTransition("evidência obrigatória para encerrar")
            if not candidate.closure_approver_id.strip() or candidate.closure_approver_id == candidate.owner_id:
                raise InvalidTransition("aprovação independente obrigatória")
            if not candidate.root_cause.strip() or not candidate.containment.strip() or not candidate.recovery_validation.strip():
                raise InvalidTransition("incidente sem causa, contenção ou recuperação")
        return candidate
