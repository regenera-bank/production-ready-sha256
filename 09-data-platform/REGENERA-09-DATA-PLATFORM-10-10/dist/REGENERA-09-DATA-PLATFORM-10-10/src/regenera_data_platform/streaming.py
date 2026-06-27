from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable


class StreamError(RuntimeError):
    pass


class DeliveryState(str, Enum):
    PROCESSING = "PROCESSING"
    COMMITTED = "COMMITTED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"


class AmbiguousDelivery(RuntimeError):
    pass


@dataclass(slots=True)
class StreamRecord:
    event_id: str
    payload_hash: str
    state: DeliveryState
    result: Any = None


class StreamProcessor:
    def __init__(self) -> None:
        self._records: dict[str, StreamRecord] = {}
        self.offset = -1

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def process(self, offset: int, event_id: str, payload: dict[str, Any], handler: Callable[[dict[str, Any]], Any]) -> Any:
        digest = self._hash(payload)
        existing = self._records.get(event_id)
        if existing:
            if existing.payload_hash != digest:
                raise StreamError("event_id reutilizado com payload diferente")
            if existing.state == DeliveryState.COMMITTED:
                return existing.result
            if existing.state == DeliveryState.UNKNOWN:
                raise StreamError("UNKNOWN exige reconciliação")
        record = StreamRecord(event_id, digest, DeliveryState.PROCESSING)
        self._records[event_id] = record
        try:
            result = handler(payload)
        except AmbiguousDelivery:
            record.state = DeliveryState.UNKNOWN
            raise
        except Exception:
            record.state = DeliveryState.FAILED
            raise
        record.state = DeliveryState.COMMITTED
        record.result = result
        self.offset = max(self.offset, offset)
        return result
