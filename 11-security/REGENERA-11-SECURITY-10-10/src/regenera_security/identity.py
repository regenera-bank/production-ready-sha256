from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .errors import AuthorizationDenied


@dataclass(frozen=True, slots=True)
class Principal:
    principal_id: str
    roles: frozenset[str]
    active: bool = True
    mfa_verified: bool = False
    session_issued_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class PrivilegedGrant:
    grant_id: str
    principal_id: str
    action: str
    resource: str
    ticket_id: str
    approver_id: str
    issued_at: datetime
    expires_at: datetime

    def is_valid(self, now: datetime) -> bool:
        return self.issued_at <= now < self.expires_at


class AccessController:
    def __init__(self, policies: dict[str, set[str]], privileged_actions: set[str] | None = None) -> None:
        self._policies = {action: frozenset(roles) for action, roles in policies.items()}
        self._privileged = frozenset(privileged_actions or set())

    def authorize(self, principal: Principal, action: str, *, now: datetime | None = None, max_session_age_minutes: int = 15) -> None:
        current = now or datetime.now(timezone.utc)
        if not principal.active:
            raise AuthorizationDenied("identidade inativa")
        required = self._policies.get(action)
        if not required:
            raise AuthorizationDenied("ação sem política explícita")
        if principal.roles.isdisjoint(required):
            raise AuthorizationDenied("papel insuficiente")
        if action in self._privileged:
            if not principal.mfa_verified:
                raise AuthorizationDenied("MFA obrigatório")
            if principal.session_issued_at is None or principal.session_issued_at.tzinfo is None:
                raise AuthorizationDenied("sessão forte obrigatória")
            age = current - principal.session_issued_at
            if age < timedelta(0) or age > timedelta(minutes=max_session_age_minutes):
                raise AuthorizationDenied("sessão privilegiada vencida")

    def issue_jit_grant(
        self,
        principal: Principal,
        action: str,
        resource: str,
        ticket_id: str,
        approver_id: str,
        duration_minutes: int,
        *,
        now: datetime | None = None,
        maximum_minutes: int = 60,
    ) -> PrivilegedGrant:
        current = now or datetime.now(timezone.utc)
        self.authorize(principal, action, now=current)
        if not resource.strip() or not ticket_id.strip():
            raise AuthorizationDenied("recurso e ticket são obrigatórios")
        if not approver_id.strip() or approver_id == principal.principal_id:
            raise AuthorizationDenied("aprovação independente obrigatória")
        if duration_minutes <= 0 or duration_minutes > maximum_minutes:
            raise AuthorizationDenied("prazo de privilégio inválido")
        import hashlib
        raw = f"{principal.principal_id}|{action}|{resource}|{ticket_id}|{current.isoformat()}"
        grant_id = hashlib.sha256(raw.encode()).hexdigest()[:24]
        return PrivilegedGrant(
            grant_id=grant_id,
            principal_id=principal.principal_id,
            action=action,
            resource=resource,
            ticket_id=ticket_id,
            approver_id=approver_id,
            issued_at=current,
            expires_at=current + timedelta(minutes=duration_minutes),
        )
