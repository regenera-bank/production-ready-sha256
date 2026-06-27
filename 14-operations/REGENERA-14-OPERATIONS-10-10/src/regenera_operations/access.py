from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .errors import AuthorizationError, ValidationError
from .utils import require_aware, require_sha256

@dataclass(frozen=True, slots=True)
class Actor:
    actor_id: str
    roles: frozenset[str]
    active: bool = True
    mfa: bool = False

class AccessPolicy:
    @staticmethod
    def authorize(actor: Actor, role: str, privileged: bool = False) -> None:
        if not actor.active:
            raise AuthorizationError("identidade inativa")
        if role not in actor.roles:
            raise AuthorizationError("papel insuficiente")
        if privileged and not actor.mfa:
            raise AuthorizationError("MFA obrigatório")

@dataclass(frozen=True, slots=True)
class Approval:
    requester_id: str
    approver_id: str
    payload_digest: str
    expires_at: datetime
    signed: bool

class ApprovalPolicy:
    @staticmethod
    def validate(approval: Approval, expected_digest: str, now: datetime) -> None:
        require_aware(now, "now")
        require_aware(approval.expires_at, "expires_at")
        require_sha256(approval.payload_digest, "payload_digest")
        require_sha256(expected_digest, "expected_digest")
        if approval.requester_id == approval.approver_id:
            raise AuthorizationError("autoaprovação bloqueada")
        if not approval.signed:
            raise AuthorizationError("aprovação sem assinatura")
        if approval.payload_digest != expected_digest:
            raise AuthorizationError("aprovação vinculada a outro payload")
        if approval.expires_at <= now:
            raise AuthorizationError("aprovação vencida")
