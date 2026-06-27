from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .errors import AuthorizationError, ValidationError
from .utils import require_aware, require_sha256

@dataclass(frozen=True, slots=True)
class Control:
    control_id: str
    owner_id: str
    evidence_digest: str
    review_due: datetime
    enabled: bool=True

    def effective(self, now: datetime) -> bool:
        require_aware(now,"now")
        require_aware(self.review_due,"review_due")
        require_sha256(self.evidence_digest,"evidence_digest")
        return bool(self.control_id.strip() and self.owner_id.strip() and self.enabled and self.review_due>now)

@dataclass(frozen=True, slots=True)
class ControlException:
    exception_id: str
    owner_id: str
    approver_id: str
    reason: str
    expires_at: datetime
    evidence_digest: str

    def valid(self, now: datetime) -> bool:
        require_aware(now,"now")
        require_aware(self.expires_at,"expires_at")
        require_sha256(self.evidence_digest,"evidence_digest")
        if self.owner_id == self.approver_id:
            raise AuthorizationError("exceção não permite autoaprovação")
        if not self.reason.strip():
            raise ValidationError("exceção sem justificativa")
        return self.expires_at > now
