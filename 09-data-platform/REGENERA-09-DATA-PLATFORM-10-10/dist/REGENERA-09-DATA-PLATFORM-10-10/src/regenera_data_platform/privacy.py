from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import hmac
import re


class DataClass(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class PrivacyError(PermissionError):
    pass


@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    allowed_purposes: frozenset[str]
    role_ceiling: dict[str, DataClass]

    def authorize(self, role: str, purpose: str, classification: DataClass) -> None:
        if purpose not in self.allowed_purposes:
            raise PrivacyError("finalidade não autorizada")
        ceiling = self.role_ceiling.get(role)
        if ceiling is None:
            raise PrivacyError("papel sem autorização")
        order = list(DataClass)
        if order.index(classification) > order.index(ceiling):
            raise PrivacyError("classificação acima do papel")


def mask_email(value: str) -> str:
    match = re.fullmatch(r"([^@]+)@([^@]+)", value.strip())
    if not match:
        raise ValueError("e-mail inválido")
    user, domain = match.groups()
    return f"{user[:2]}***@{domain}"


def mask_document(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) < 6:
        raise ValueError("documento inválido")
    return f"{digits[:3]}***{digits[-2:]}"


def tokenize(value: str, secret: bytes) -> str:
    if len(secret) < 32:
        raise ValueError("segredo fraco")
    return hmac.new(secret, value.encode(), sha256).hexdigest()
