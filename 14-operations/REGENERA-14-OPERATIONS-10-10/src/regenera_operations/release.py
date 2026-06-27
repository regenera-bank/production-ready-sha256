from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .access import Approval, ApprovalPolicy
from .errors import StateTransitionError
from .utils import require_sha256

@dataclass(frozen=True, slots=True)
class ReleaseGate:
    artifact_digest: str
    tests_passed: bool
    validation_passed: bool
    security_passed: bool
    integrity_passed: bool
    approval: Approval

    def evaluate(self, now: datetime) -> str:
        require_sha256(self.artifact_digest,"artifact_digest")
        ApprovalPolicy.validate(self.approval,self.artifact_digest,now)
        if not all((self.tests_passed,self.validation_passed,self.security_passed,self.integrity_passed)):
            raise StateTransitionError("gate técnico incompleto")
        return "APPROVED_FOR_LOCAL_TECHNICAL_SCOPE"
