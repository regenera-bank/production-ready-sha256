from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError


@dataclass(frozen=True)
class ReconciliationResult:
    original_message_id: str
    status_message_id: str
    status: str
    action: str


def reconcile_payment_status(original: dict, status: dict) -> ReconciliationResult:
    original_id = str(original.get("message_id", ""))
    referenced = str(status.get("original_message_id", ""))
    if not original_id or original_id != referenced:
        raise ValidationError("RECONCILIATION_REFERENCE_MISMATCH", "Status não referencia a mensagem original")
    tx_original = set(original.get("transaction_ids", []))
    tx_status = set(status.get("transaction_ids", []))
    if tx_status and not tx_status.issubset(tx_original):
        raise ValidationError("RECONCILIATION_TRANSACTION_MISMATCH", "Status contém transação desconhecida")
    group_status = str(status.get("status", ""))
    actions = {
        "ACCP": "WAIT_SETTLEMENT",
        "ACSC": "CLOSE_AS_SETTLED",
        "PDNG": "KEEP_PENDING",
        "RJCT": "CLOSE_AS_REJECTED",
    }
    if group_status not in actions:
        raise ValidationError("RECONCILIATION_STATUS_INVALID", "Status não reconciliável")
    return ReconciliationResult(original_id, str(status.get("message_id", "")), group_status, actions[group_status])
