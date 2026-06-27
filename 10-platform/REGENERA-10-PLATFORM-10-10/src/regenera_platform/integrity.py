from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
from .errors import PlatformControlError


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return sha256(canonical(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class AuditRecord:
    sequence: int
    event: str
    payload_hash: str
    previous_hash: str
    record_hash: str


class AuditChain:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    @property
    def records(self) -> tuple[AuditRecord, ...]:
        return tuple(self._records)

    def append(self, event: str, payload: object) -> AuditRecord:
        if not event.strip():
            raise PlatformControlError("AUDIT_EVENT_REQUIRED")
        previous = self._records[-1].record_hash if self._records else "0" * 64
        sequence = len(self._records) + 1
        payload_hash = digest(payload)
        record_hash = digest({"sequence": sequence, "event": event, "payload_hash": payload_hash, "previous_hash": previous})
        record = AuditRecord(sequence, event, payload_hash, previous, record_hash)
        self._records.append(record)
        return record

    def verify(self) -> bool:
        previous = "0" * 64
        for expected_sequence, record in enumerate(self._records, start=1):
            expected = digest({"sequence": expected_sequence, "event": record.event, "payload_hash": record.payload_hash, "previous_hash": previous})
            if not hmac.compare_digest(record.record_hash, expected):
                return False
            if record.sequence != expected_sequence or record.previous_hash != previous:
                return False
            previous = record.record_hash
        return True
