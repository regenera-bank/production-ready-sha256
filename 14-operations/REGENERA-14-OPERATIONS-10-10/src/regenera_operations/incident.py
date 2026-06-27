from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from .errors import StateTransitionError, ValidationError, AuthorizationError
from .utils import require_aware, require_sha256

class Severity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class IncidentState(str, Enum):
    DECLARED = "DECLARED"
    ASSESSING = "ASSESSING"
    CONTAINED = "CONTAINED"
    RECOVERING = "RECOVERING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

_ALLOWED = {
    IncidentState.DECLARED: IncidentState.ASSESSING,
    IncidentState.ASSESSING: IncidentState.CONTAINED,
    IncidentState.CONTAINED: IncidentState.RECOVERING,
    IncidentState.RECOVERING: IncidentState.RESOLVED,
    IncidentState.RESOLVED: IncidentState.CLOSED,
}

@dataclass(slots=True)
class Incident:
    incident_id: str
    severity: Severity
    summary: str
    owner_id: str
    declared_at: datetime
    state: IncidentState = IncidentState.DECLARED
    evidence: list[str] = field(default_factory=list)
    postmortem_digest: str | None = None
    reconciliation_complete: bool = False

    def __post_init__(self) -> None:
        require_aware(self.declared_at, "declared_at")
        if not self.incident_id.strip() or not self.summary.strip() or not self.owner_id.strip():
            raise ValidationError("dados obrigatórios do incidente ausentes")

    def advance(self, target: IncidentState, actor_id: str, evidence_digest: str, *, independent_reviewer: str | None = None) -> None:
        if _ALLOWED.get(self.state) != target:
            raise StateTransitionError("transição de incidente inválida")
        require_sha256(evidence_digest, "evidence_digest")
        if not actor_id.strip():
            raise ValidationError("ator obrigatório")
        if target == IncidentState.RESOLVED and not self.reconciliation_complete:
            raise StateTransitionError("reconciliação obrigatória")
        if target == IncidentState.CLOSED:
            if independent_reviewer in {None, "", self.owner_id}:
                raise AuthorizationError("fechamento exige revisão independente")
            if self.severity == Severity.P1:
                if not self.postmortem_digest:
                    raise StateTransitionError("P1 exige postmortem")
                require_sha256(self.postmortem_digest, "postmortem_digest")
        self.evidence.append(evidence_digest)
        self.state = target
