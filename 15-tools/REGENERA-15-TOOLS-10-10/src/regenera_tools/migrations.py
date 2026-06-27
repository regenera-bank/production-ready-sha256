from __future__ import annotations
from dataclasses import dataclass
import re
from .canonical import sha256_bytes
from .errors import ValidationError

NAME = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
DESTRUCTIVE = ("DROP TABLE", "DROP COLUMN", "TRUNCATE ", "ALTER TYPE")

@dataclass(frozen=True, slots=True)
class Migration:
    filename: str
    sql: str

    @property
    def version(self) -> int:
        match = NAME.fullmatch(self.filename)
        if not match:
            raise ValidationError("nome de migration inválido")
        return int(match.group("version"))

    @property
    def checksum(self) -> str:
        return sha256_bytes(self.sql.replace("\r\n", "\n").encode())

def validate_migrations(items: list[Migration]) -> list[str]:
    errors: list[str] = []
    versions: list[int] = []
    for item in items:
        try:
            version = item.version
        except ValidationError as exc:
            errors.append(f"{item.filename}:{exc}")
            continue
        versions.append(version)
        upper = item.sql.upper()
        if "BEGIN;" in upper or "COMMIT;" in upper:
            errors.append(f"{item.filename}:transação manual proibida")
        if any(term in upper for term in DESTRUCTIVE) and "regenera: destructive-approved=" not in item.sql.lower():
            errors.append(f"{item.filename}:operação destrutiva sem aprovação")
    if len(versions) != len(set(versions)):
        errors.append("versão duplicada")
    if versions and sorted(versions) != list(range(min(versions), max(versions) + 1)):
        errors.append("sequência de versões possui lacuna")
    return errors

def verify_published(items: list[Migration], published: dict[str, str]) -> list[str]:
    return [
        f"migration publicada alterada:{item.filename}"
        for item in items
        if item.filename in published and published[item.filename] != item.checksum
    ]
