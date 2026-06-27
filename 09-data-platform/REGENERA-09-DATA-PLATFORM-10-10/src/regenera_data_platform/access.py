from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


class AccessError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class AccessGrant:
    subject: str
    dataset: str
    purposes: frozenset[str]
    expires_at: datetime
    owner_approval: str


class AccessPolicy:
    def authorize(self, grant: AccessGrant, dataset: str, purpose: str, now: datetime) -> None:
        if grant.dataset != dataset:
            raise AccessError("dataset fora do grant")
        if purpose not in grant.purposes:
            raise AccessError("finalidade fora do grant")
        if now.astimezone(timezone.utc) >= grant.expires_at.astimezone(timezone.utc):
            raise AccessError("grant vencido")
        if not grant.owner_approval:
            raise AccessError("aprovação do owner ausente")

    def approve_break_glass(
        self,
        requester: str,
        approvers: tuple[str, str],
        ticket: str,
        expires_at: datetime,
        now: datetime,
    ) -> None:
        if requester in approvers or approvers[0] == approvers[1]:
            raise AccessError("segregação de função violada")
        if not ticket:
            raise AccessError("ticket obrigatório")
        if expires_at <= now or expires_at - now > timedelta(hours=4):
            raise AccessError("janela break-glass inválida")
