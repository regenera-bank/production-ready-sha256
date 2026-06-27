from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .money import Money
from .errors import ValidationError, StateTransitionError, AuthorizationError
from .utils import require_sha256

class ReconciliationState(str, Enum):
    MATCHED = "MATCHED"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"
    CLOSED = "CLOSED"

@dataclass(frozen=True, slots=True)
class ReconciliationRecord:
    reference: str
    amount: Money
    status: str

@dataclass(slots=True)
class ReconciliationResult:
    state: ReconciliationState
    differences: tuple[str, ...]
    evidence_digest: str | None = None

class ReconciliationEngine:
    @staticmethod
    def reconcile(internal: list[ReconciliationRecord], external: list[ReconciliationRecord] | None) -> ReconciliationResult:
        if external is None:
            return ReconciliationResult(ReconciliationState.UNKNOWN, ("fonte externa indisponível",))
        left=ReconciliationEngine._index(internal)
        right=ReconciliationEngine._index(external)
        differences=[]
        for reference in sorted(set(left)|set(right)):
            if reference not in left:
                differences.append(f"ausente-interno:{reference}")
                continue
            if reference not in right:
                differences.append(f"ausente-externo:{reference}")
                continue
            a,b=left[reference],right[reference]
            if a.amount.currency != b.amount.currency:
                differences.append(f"moeda:{reference}")
            elif a.amount.minor != b.amount.minor:
                differences.append(f"valor:{reference}")
            if a.status != b.status:
                differences.append(f"status:{reference}")
        return ReconciliationResult(ReconciliationState.MISMATCH if differences else ReconciliationState.MATCHED, tuple(differences))

    @staticmethod
    def close(result: ReconciliationResult, evidence_digest: str, owner_id: str, reviewer_id: str) -> None:
        if result.state == ReconciliationState.UNKNOWN:
            raise StateTransitionError("UNKNOWN não pode ser encerrado")
        if owner_id == reviewer_id:
            raise AuthorizationError("fechamento exige revisão independente")
        require_sha256(evidence_digest, "evidence_digest")
        result.evidence_digest=evidence_digest
        result.state=ReconciliationState.CLOSED

    @staticmethod
    def _index(records: list[ReconciliationRecord]) -> dict[str, ReconciliationRecord]:
        indexed={}
        for record in records:
            if not record.reference.strip():
                raise ValidationError("referência vazia")
            if record.reference in indexed:
                raise ValidationError("referência duplicada")
            indexed[record.reference]=record
        return indexed
