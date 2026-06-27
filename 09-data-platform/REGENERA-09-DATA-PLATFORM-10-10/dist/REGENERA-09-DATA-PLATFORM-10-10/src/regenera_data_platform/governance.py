from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True, slots=True)
class Control:
    control_id: str
    owner_group: str
    evidence: tuple[str, ...]
    review_due: date
    blocking: bool

    def effective(self, today: date) -> bool:
        return bool(self.owner_group and self.evidence and self.review_due >= today)


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    artifact_hash: str
    author: str
    approver: str
    signature_fingerprint: str
    approved_at: datetime

    def validate(self) -> None:
        if self.author == self.approver:
            raise ValueError("autoaprovação bloqueada")
        if len(self.artifact_hash) != 64:
            raise ValueError("hash inválido")
        if len(self.signature_fingerprint.replace(" ", "")) < 40:
            raise ValueError("assinatura ausente")
        if self.approved_at.astimezone(timezone.utc) > datetime.now(timezone.utc):
            raise ValueError("aprovação futura")
