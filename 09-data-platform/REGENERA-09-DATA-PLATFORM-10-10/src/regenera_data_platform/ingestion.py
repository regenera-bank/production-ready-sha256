from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from .contracts import DataContract


class IngestionError(RuntimeError):
    pass


class IngestionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    COMMITTED = "COMMITTED"
    QUARANTINED = "QUARANTINED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_FINAL = "FAILED_FINAL"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class IngestionRecord:
    source: str
    event_id: str
    payload_hash: str
    status: IngestionStatus
    result: dict[str, Any] | None = None
    errors: tuple[str, ...] = ()


class IngestionRegistry:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], IngestionRecord] = {}

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return sha256(encoded).hexdigest()

    def begin(self, source: str, event_id: str, payload: dict[str, Any], contract: DataContract) -> IngestionRecord:
        if not source or not event_id:
            raise IngestionError("origem e event_id são obrigatórios")
        key = (source, event_id)
        payload_hash = self._hash(payload)
        existing = self._records.get(key)
        if existing:
            if existing.payload_hash != payload_hash:
                raise IngestionError("event_id reutilizado com payload diferente")
            if existing.status == IngestionStatus.UNKNOWN:
                raise IngestionError("estado UNKNOWN exige reconciliação")
            return existing
        errors = tuple(contract.validate_record(payload))
        status = IngestionStatus.QUARANTINED if errors else IngestionStatus.PROCESSING
        record = IngestionRecord(source, event_id, payload_hash, status, errors=errors)
        self._records[key] = record
        return record

    def commit(self, source: str, event_id: str, result: dict[str, Any]) -> IngestionRecord:
        record = self._required(source, event_id)
        if record.status != IngestionStatus.PROCESSING:
            raise IngestionError("somente PROCESSING pode confirmar")
        record.status = IngestionStatus.COMMITTED
        record.result = dict(result)
        return record

    def mark_unknown(self, source: str, event_id: str) -> None:
        record = self._required(source, event_id)
        if record.status != IngestionStatus.PROCESSING:
            raise IngestionError("estado inválido para UNKNOWN")
        record.status = IngestionStatus.UNKNOWN

    def reconcile(self, source: str, event_id: str, committed: bool, result: dict[str, Any] | None = None) -> None:
        record = self._required(source, event_id)
        if record.status != IngestionStatus.UNKNOWN:
            raise IngestionError("somente UNKNOWN entra em reconciliação")
        record.status = IngestionStatus.COMMITTED if committed else IngestionStatus.FAILED_FINAL
        record.result = dict(result or {}) if committed else None

    def _required(self, source: str, event_id: str) -> IngestionRecord:
        try:
            return self._records[(source, event_id)]
        except KeyError as exc:
            raise IngestionError("ingestão não encontrada") from exc
