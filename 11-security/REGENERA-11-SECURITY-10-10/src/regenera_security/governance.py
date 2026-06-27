from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .errors import SecurityControlError


@dataclass(frozen=True, slots=True)
class ControlAssessment:
    control_id: str
    owner: str
    evidence_id: str
    reviewed_on: date
    next_review_on: date
    result: str

    def effective(self, today: date) -> bool:
        return bool(
            self.control_id.strip()
            and self.owner.strip()
            and self.evidence_id.strip()
            and self.result == "EFFECTIVE"
            and self.reviewed_on <= today < self.next_review_on
        )


@dataclass(frozen=True, slots=True)
class SecurityException:
    exception_id: str
    requester_id: str
    approver_id: str
    owner: str
    expires_on: date
    risk: str
    compensating_control: str

    def validate(self, today: date) -> None:
        if not all(value.strip() for value in (self.exception_id,self.requester_id,self.approver_id,self.owner,self.risk,self.compensating_control)):
            raise SecurityControlError("exceção incompleta")
        if self.requester_id == self.approver_id:
            raise SecurityControlError("autoaprovação proibida")
        if today >= self.expires_on:
            raise SecurityControlError("exceção vencida")
