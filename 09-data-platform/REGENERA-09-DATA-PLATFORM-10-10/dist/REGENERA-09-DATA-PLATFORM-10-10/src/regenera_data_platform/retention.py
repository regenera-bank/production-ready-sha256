from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


class RetentionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RetentionPolicy:
    retention_class: str
    days: int
    legal_basis: str
    disposal_method: str

    def __post_init__(self) -> None:
        if not self.retention_class or self.days <= 0 or not self.legal_basis:
            raise RetentionError("política de retenção incompleta")
        if self.disposal_method not in {"CRYPTO_ERASURE", "SECURE_DELETE", "ANONYMIZE"}:
            raise RetentionError("método de descarte inválido")


@dataclass(slots=True)
class RetentionRecord:
    record_id: str
    created_at: datetime
    policy: RetentionPolicy
    legal_hold: bool = False
    disposed_at: datetime | None = None
    evidence_hash: str | None = None

    def eligible_at(self) -> datetime:
        return self.created_at.astimezone(timezone.utc) + timedelta(days=self.policy.days)

    def dispose(self, now: datetime, evidence_hash: str) -> None:
        if self.legal_hold:
            raise RetentionError("legal hold bloqueia descarte")
        if now.astimezone(timezone.utc) < self.eligible_at():
            raise RetentionError("retenção ainda vigente")
        if len(evidence_hash) != 64:
            raise RetentionError("evidência de descarte inválida")
        if self.disposed_at is not None:
            raise RetentionError("registro já descartado")
        self.disposed_at = now.astimezone(timezone.utc)
        self.evidence_hash = evidence_hash
