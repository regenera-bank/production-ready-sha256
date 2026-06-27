import hashlib
import json
import re
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from .errors import ValidationError

_HASH=re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER=re.compile(r"^[A-Z0-9][A-Z0-9._:-]{2,127}$")

def canonical_json(value) -> str:
    if is_dataclass(value): value=asdict(value)
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)

def sha256_hex(value) -> str:
    raw=value if isinstance(value,bytes) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def require_sha256(value: str) -> str:
    if not isinstance(value,str) or not _HASH.fullmatch(value):
        raise ValidationError("sha256 inválido")
    return value

def require_identifier(value: str) -> str:
    if not isinstance(value,str) or not _IDENTIFIER.fullmatch(value):
        raise ValidationError("identificador inválido")
    return value

def require_minor_units(value: int) -> int:
    if isinstance(value,bool) or not isinstance(value,int):
        raise ValidationError("valor monetário precisa usar unidade mínima inteira")
    if abs(value)>9_000_000_000_000_000:
        raise ValidationError("valor monetário fora do limite")
    return value
