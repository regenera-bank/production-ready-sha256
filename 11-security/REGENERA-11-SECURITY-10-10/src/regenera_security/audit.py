from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json

from .errors import IntegrityViolation


def _canonical(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class AuditEntry:
    sequence: int
    event_type: str
    subject: str
    occurred_at: str
    payload_digest: str
    previous_hash: str
    entry_hash: str


class AuditChain:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    def append(self, event_type: str, subject: str, payload: dict, occurred_at: datetime | None = None) -> AuditEntry:
        if not event_type.strip() or not subject.strip():
            raise IntegrityViolation("evento e sujeito são obrigatórios")
        occurred = occurred_at or datetime.now(timezone.utc)
        if occurred.tzinfo is None:
            raise IntegrityViolation("data de auditoria precisa de timezone")
        previous = self._entries[-1].entry_hash if self._entries else "0" * 64
        payload_digest = hashlib.sha256(_canonical(payload)).hexdigest()
        material = {
            "sequence": len(self._entries) + 1,
            "event_type": event_type,
            "subject": subject,
            "occurred_at": occurred.astimezone(timezone.utc).isoformat(),
            "payload_digest": payload_digest,
            "previous_hash": previous,
        }
        entry_hash = hashlib.sha256(_canonical(material)).hexdigest()
        entry = AuditEntry(entry_hash=entry_hash, **material)
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous = "0" * 64
        for expected_sequence, entry in enumerate(self._entries, start=1):
            material = {
                "sequence": entry.sequence,
                "event_type": entry.event_type,
                "subject": entry.subject,
                "occurred_at": entry.occurred_at,
                "payload_digest": entry.payload_digest,
                "previous_hash": entry.previous_hash,
            }
            expected_hash = hashlib.sha256(_canonical(material)).hexdigest()
            if entry.sequence != expected_sequence or entry.previous_hash != previous or entry.entry_hash != expected_hash:
                return False
            previous = entry.entry_hash
        return True

    def assert_valid(self) -> None:
        if not self.verify():
            raise IntegrityViolation("cadeia de auditoria adulterada")
