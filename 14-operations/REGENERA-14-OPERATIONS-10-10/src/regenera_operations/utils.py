from __future__ import annotations
import hashlib
import json
from datetime import datetime
from .errors import ValidationError


def require_aware(value: datetime, field: str = "timestamp") -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValidationError(f"{field} precisa conter timezone")
    return value


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def require_sha256(value: str, field: str = "digest") -> str:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise ValidationError(f"{field} inválido")
    return value.lower()
