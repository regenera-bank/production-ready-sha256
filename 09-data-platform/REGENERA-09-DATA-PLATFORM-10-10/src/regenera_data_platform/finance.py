from __future__ import annotations

from dataclasses import dataclass
from .money import Money


@dataclass(frozen=True, slots=True)
class FinancialRow:
    reference: str
    amount: Money


@dataclass(frozen=True, slots=True)
class ReconciliationBreak:
    reference: str
    kind: str
    detail: str


def reconcile_financial_rows(expected: list[FinancialRow], actual: list[FinancialRow]) -> list[ReconciliationBreak]:
    def index(rows: list[FinancialRow], side: str) -> dict[str, FinancialRow]:
        result: dict[str, FinancialRow] = {}
        for row in rows:
            if row.reference in result:
                raise ValueError(f"referência duplicada em {side}")
            result[row.reference] = row
        return result
    left = index(expected, "expected")
    right = index(actual, "actual")
    breaks: list[ReconciliationBreak] = []
    for reference in sorted(set(left) | set(right)):
        a = left.get(reference)
        b = right.get(reference)
        if a is None:
            breaks.append(ReconciliationBreak(reference, "UNEXPECTED", "ausente na origem"))
        elif b is None:
            breaks.append(ReconciliationBreak(reference, "MISSING", "ausente no destino"))
        elif a.amount.currency != b.amount.currency:
            breaks.append(ReconciliationBreak(reference, "CURRENCY", "moeda divergente"))
        elif a.amount.amount_cents != b.amount.amount_cents:
            breaks.append(ReconciliationBreak(reference, "AMOUNT", "valor divergente"))
    return breaks


def aggregate_by_currency(rows: list[FinancialRow]) -> dict[str, Money]:
    totals: dict[str, Money] = {}
    for row in rows:
        totals[row.amount.currency] = totals.get(row.amount.currency, Money.from_cents(0, row.amount.currency)).add(row.amount)
    return totals
