from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import time
from urllib.parse import urlparse

from .errors import AuthenticationError, ValidationError


@dataclass(frozen=True)
class EndpointPolicy:
    allowed_hosts: frozenset[str]

    def validate(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValidationError("integração externa exige HTTPS")
        if parsed.username or parsed.password:
            raise ValidationError("credencial não entra na URL")
        if parsed.hostname not in self.allowed_hosts:
            raise ValidationError("host fora da allowlist")


def validate_mtls_peer(*, fingerprint: str, allowed_fingerprints: set[str]) -> None:
    normalized = fingerprint.lower().replace(":", "")
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise AuthenticationError("fingerprint mTLS inválida")
    if normalized not in {item.lower().replace(":", "") for item in allowed_fingerprints}:
        raise AuthenticationError("certificado não autorizado")


def verify_webhook_hmac(
    *,
    body: bytes,
    timestamp: int,
    signature_hex: str,
    secret: bytes,
    now: int | None = None,
    tolerance_seconds: int = 300,
) -> None:
    current = int(time.time()) if now is None else now
    if abs(current - timestamp) > tolerance_seconds:
        raise AuthenticationError("webhook fora da janela temporal")
    signed = str(timestamp).encode("ascii") + b"." + body
    expected = hmac.new(secret, signed, sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_hex.lower()):
        raise AuthenticationError("assinatura do webhook inválida")


def redact_payload(payload: dict[str, object], allowed: set[str]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if key in allowed}
