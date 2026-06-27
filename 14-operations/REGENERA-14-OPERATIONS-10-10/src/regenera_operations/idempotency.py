from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .errors import ConflictError, StateTransitionError, ValidationError
from .utils import digest

class IdempotencyState(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

@dataclass(slots=True)
class IdempotencyRecord:
    key: str
    fingerprint: str
    state: IdempotencyState
    result: object | None = None

class IdempotencyRegistry:
    def __init__(self) -> None:
        self._records: dict[str, IdempotencyRecord] = {}

    def begin(self, key: str, payload: object) -> IdempotencyRecord:
        if not key.strip() or len(key) > 128:
            raise ValidationError("chave de idempotência inválida")
        fingerprint = digest(payload)
        current = self._records.get(key)
        if current:
            if current.fingerprint != fingerprint:
                raise ConflictError("chave reutilizada com payload divergente")
            return current
        record = IdempotencyRecord(key, fingerprint, IdempotencyState.PROCESSING)
        self._records[key] = record
        return record

    def complete(self, key: str, result: object) -> IdempotencyRecord:
        record = self._require(key)
        if record.state not in {IdempotencyState.PROCESSING, IdempotencyState.UNKNOWN}:
            raise StateTransitionError("estado não permite conclusão")
        record.state = IdempotencyState.COMPLETED
        record.result = result
        return record

    def fail(self, key: str, result: object | None = None) -> IdempotencyRecord:
        record = self._require(key)
        if record.state != IdempotencyState.PROCESSING:
            raise StateTransitionError("estado não permite falha")
        record.state = IdempotencyState.FAILED
        record.result = result
        return record

    def mark_unknown(self, key: str) -> IdempotencyRecord:
        record = self._require(key)
        if record.state != IdempotencyState.PROCESSING:
            raise StateTransitionError("estado não permite UNKNOWN")
        record.state = IdempotencyState.UNKNOWN
        return record

    def assert_retry_allowed(self, key: str) -> None:
        record = self._require(key)
        if record.state in {IdempotencyState.PROCESSING, IdempotencyState.UNKNOWN, IdempotencyState.COMPLETED}:
            raise StateTransitionError("repetição bloqueada")

    def _require(self, key: str) -> IdempotencyRecord:
        if key not in self._records:
            raise ValidationError("registro de idempotência ausente")
        return self._records[key]
