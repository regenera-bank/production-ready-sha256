from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .errors import IntegrityError, ValidationError
from .utils import digest, require_aware

@dataclass(frozen=True, slots=True)
class AuditEntry:
    index: int
    occurred_at: str
    actor_id: str
    action: str
    payload_hash: str
    previous_hash: str
    entry_hash: str

class AuditChain:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    def append(self, occurred_at: datetime, actor_id: str, action: str, payload: object) -> AuditEntry:
        require_aware(occurred_at, "occurred_at")
        if not actor_id.strip() or not action.strip():
            raise ValidationError("ator e ação são obrigatórios")
        previous = self._entries[-1].entry_hash if self._entries else "0" * 64
        body = {
            "index": len(self._entries),
            "occurred_at": occurred_at.isoformat(),
            "actor_id": actor_id,
            "action": action,
            "payload_hash": digest(payload),
            "previous_hash": previous,
        }
        entry = AuditEntry(**body, entry_hash=digest(body))
        self._entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous = "0" * 64
        for position, entry in enumerate(self._entries):
            body = {
                "index": entry.index,
                "occurred_at": entry.occurred_at,
                "actor_id": entry.actor_id,
                "action": entry.action,
                "payload_hash": entry.payload_hash,
                "previous_hash": entry.previous_hash,
            }
            if entry.index != position or entry.previous_hash != previous or digest(body) != entry.entry_hash:
                raise IntegrityError("cadeia de auditoria adulterada")
            previous = entry.entry_hash
        return True
