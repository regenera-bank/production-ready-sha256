from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .canonical import message_digest
from .errors import IdempotencyConflict, ValidationError


class MessageState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


@dataclass
class MessageRecord:
    message_id: str
    digest: str
    state: MessageState
    result: dict | None = None


class MessageRegistry:
    def __init__(self) -> None:
        self._records: dict[str, MessageRecord] = {}

    def register(self, message_id: str, payload: bytes | str) -> tuple[MessageRecord, bool]:
        digest = message_digest(payload)
        existing = self._records.get(message_id)
        if existing is not None:
            if existing.digest != digest:
                raise IdempotencyConflict("MESSAGE_ID_CONFLICT", "MsgId reutilizado com conteúdo diferente")
            return existing, True
        record = MessageRecord(message_id, digest, MessageState.RECEIVED)
        self._records[message_id] = record
        return record, False

    def transition(self, message_id: str, target: MessageState, result: dict | None = None) -> MessageRecord:
        record = self._records.get(message_id)
        if record is None:
            raise ValidationError("MESSAGE_NOT_REGISTERED", "Mensagem não registrada")
        allowed = {
            MessageState.RECEIVED: {MessageState.VALIDATED, MessageState.REJECTED},
            MessageState.VALIDATED: {MessageState.SENT, MessageState.REJECTED},
            MessageState.SENT: {MessageState.ACKNOWLEDGED, MessageState.REJECTED, MessageState.UNKNOWN},
            MessageState.UNKNOWN: {MessageState.ACKNOWLEDGED, MessageState.REJECTED, MessageState.RECONCILIATION_REQUIRED},
            MessageState.RECONCILIATION_REQUIRED: {MessageState.ACKNOWLEDGED, MessageState.REJECTED},
            MessageState.ACKNOWLEDGED: set(),
            MessageState.REJECTED: set(),
        }
        if target not in allowed[record.state]:
            raise ValidationError("MESSAGE_TRANSITION_INVALID", "Transição de estado inválida")
        record.state = target
        record.result = result
        return record

    def assert_resend_allowed(self, message_id: str) -> None:
        record = self._records.get(message_id)
        if record and record.state in {MessageState.SENT, MessageState.UNKNOWN, MessageState.RECONCILIATION_REQUIRED}:
            raise ValidationError("BLIND_RESEND_FORBIDDEN", "Resultado incerto bloqueia reenvio cego")
