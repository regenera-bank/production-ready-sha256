from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .errors import SecurityControlError


_ALLOWED_REFS = ("vault://", "kms://", "hsm://", "secret-manager://")
_ALLOWED_KEY_STATES = {"ACTIVE", "SUSPENDED", "REVOKED", "DESTROYED"}
_ALLOWED_USAGES = {"ENCRYPT", "DECRYPT", "SIGN", "VERIFY", "WRAP", "UNWRAP"}


@dataclass(frozen=True, slots=True)
class SecretMetadata:
    name: str
    owner: str
    storage_ref: str
    created_at: datetime
    last_rotated_at: datetime
    rotation_days: int
    evidence_id: str
    expires_at: datetime | None = None

    def validate(self, now: datetime) -> None:
        if not self.name.strip() or not self.owner.strip():
            raise SecurityControlError("segredo sem nome ou owner")
        if not self.storage_ref.startswith(_ALLOWED_REFS):
            raise SecurityControlError("segredo fora de cofre aprovado")
        if self.rotation_days <= 0 or self.rotation_days > 365:
            raise SecurityControlError("janela de rotação inválida")
        if not self.evidence_id.strip():
            raise SecurityControlError("rotação sem evidência")
        if self.last_rotated_at < self.created_at:
            raise SecurityControlError("rotação anterior à criação")
        if now - self.last_rotated_at > timedelta(days=self.rotation_days):
            raise SecurityControlError("segredo com rotação vencida")
        if self.expires_at is not None and now >= self.expires_at:
            raise SecurityControlError("segredo expirado")


@dataclass(frozen=True, slots=True)
class KeyMetadata:
    key_id: str
    owner: str
    location: str
    usages: frozenset[str]
    state: str
    created_at: datetime
    expires_at: datetime
    rotation_evidence: str

    def validate(self, now: datetime, required_usage: str | None = None) -> None:
        if self.state not in _ALLOWED_KEY_STATES:
            raise SecurityControlError("estado de chave inválido")
        if self.state != "ACTIVE":
            raise SecurityControlError("chave não está ativa")
        if not self.location.startswith(("hsm://", "kms://")):
            raise SecurityControlError("chave fora de HSM ou KMS")
        if not self.owner.strip() or not self.rotation_evidence.strip():
            raise SecurityControlError("metadado de chave incompleto")
        if self.expires_at <= self.created_at or now >= self.expires_at:
            raise SecurityControlError("chave vencida")
        if not self.usages or not self.usages.issubset(_ALLOWED_USAGES):
            raise SecurityControlError("uso de chave inválido")
        if required_usage and required_usage not in self.usages:
            raise SecurityControlError("uso de chave não autorizado")
