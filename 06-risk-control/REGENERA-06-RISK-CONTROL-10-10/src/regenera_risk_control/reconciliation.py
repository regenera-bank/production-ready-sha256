from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .money import Money


class MatchStatus(str, Enum):
    MATCHED = 'MATCHED'
    MISSING_INTERNAL = 'MISSING_INTERNAL'
    MISSING_EXTERNAL = 'MISSING_EXTERNAL'
    AMOUNT_MISMATCH = 'AMOUNT_MISMATCH'
    CURRENCY_MISMATCH = 'CURRENCY_MISMATCH'


@dataclass(frozen=True, slots=True)
class SettlementRecord:
    reference_id: str
    amount: Money


@dataclass(frozen=True, slots=True)
class ReconciliationItem:
    reference_id: str
    status: MatchStatus
    internal: SettlementRecord | None
    external: SettlementRecord | None


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    items: tuple[ReconciliationItem, ...]

    @property
    def breaks(self) -> tuple[ReconciliationItem, ...]:
        return tuple(item for item in self.items if item.status != MatchStatus.MATCHED)


class ReconciliationEngine:
    def reconcile(self, internal: tuple[SettlementRecord, ...],
                  external: tuple[SettlementRecord, ...]) -> ReconciliationResult:
        left = {item.reference_id: item for item in internal}
        right = {item.reference_id: item for item in external}
        if len(left) != len(internal) or len(right) != len(external):
            raise ValueError('referência duplicada invalida a conciliação')
        items: list[ReconciliationItem] = []
        for reference in sorted(set(left) | set(right)):
            a, b = left.get(reference), right.get(reference)
            if a is None:
                status = MatchStatus.MISSING_INTERNAL
            elif b is None:
                status = MatchStatus.MISSING_EXTERNAL
            elif a.amount.currency != b.amount.currency:
                status = MatchStatus.CURRENCY_MISMATCH
            elif a.amount.cents != b.amount.cents:
                status = MatchStatus.AMOUNT_MISMATCH
            else:
                status = MatchStatus.MATCHED
            items.append(ReconciliationItem(reference, status, a, b))
        return ReconciliationResult(tuple(items))
