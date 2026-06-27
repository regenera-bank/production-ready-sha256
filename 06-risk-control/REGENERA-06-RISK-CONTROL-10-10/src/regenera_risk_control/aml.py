from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from .money import Money


class AmlAction(str, Enum):
    CLEAR = 'CLEAR'
    REVIEW = 'REVIEW'
    BLOCK = 'BLOCK'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True, slots=True)
class AmlTransaction:
    transaction_id: str
    customer_id: str
    amount: Money
    occurred_at: datetime
    counterparty_id: str
    cross_border: bool = False
    new_counterparty: bool = False


@dataclass(frozen=True, slots=True)
class AmlAssessment:
    action: AmlAction
    score: int
    reasons: tuple[str, ...]


class AmlEngine:
    def __init__(self, high_value_cents: int = 5_000_000,
                 structuring_cents: int = 1_000_000) -> None:
        self.high_value_cents = high_value_cents
        self.structuring_cents = structuring_cents

    def assess(self, transaction: AmlTransaction,
               history: tuple[AmlTransaction, ...], *, sanctions_hit: bool = False,
               screening_available: bool = True) -> AmlAssessment:
        if not screening_available:
            return AmlAssessment(AmlAction.UNKNOWN, 0, ('SCREENING_UNAVAILABLE',))
        if sanctions_hit:
            return AmlAssessment(AmlAction.BLOCK, 100, ('SANCTIONS_HIT',))
        if not transaction.amount.positive():
            raise ValueError('transação AML precisa de valor positivo')

        score = 0
        reasons: list[str] = []
        if transaction.amount.cents >= self.high_value_cents:
            score += 45; reasons.append('HIGH_VALUE')
        if transaction.cross_border:
            score += 20; reasons.append('CROSS_BORDER')
        if transaction.new_counterparty:
            score += 15; reasons.append('NEW_COUNTERPARTY')

        window_start = transaction.occurred_at - timedelta(hours=24)
        relevant = [item for item in history
                    if item.customer_id == transaction.customer_id
                    and window_start <= item.occurred_at <= transaction.occurred_at
                    and item.amount.cents < self.structuring_cents]
        total = transaction.amount.cents + sum(item.amount.cents for item in relevant)
        if transaction.amount.cents < self.structuring_cents and total >= self.structuring_cents:
            score += 45; reasons.append('POSSIBLE_STRUCTURING')

        if score >= 70:
            return AmlAssessment(AmlAction.BLOCK, score, tuple(reasons))
        if score >= 35:
            return AmlAssessment(AmlAction.REVIEW, score, tuple(reasons))
        return AmlAssessment(AmlAction.CLEAR, score, tuple(reasons))
