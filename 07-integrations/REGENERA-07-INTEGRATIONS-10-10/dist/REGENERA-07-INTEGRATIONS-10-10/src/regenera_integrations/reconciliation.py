from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .errors import ValidationError
from .kernel import OperationResult, Outcome


class ReconciliationStatus(str, Enum):
    MATCHED = "MATCHED"
    MISSING_EXTERNAL = "MISSING_EXTERNAL"
    MISSING_INTERNAL = "MISSING_INTERNAL"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"


@dataclass(frozen=True)
class Movement:
    reference: str
    amount_minor: int
    currency: str


@dataclass(frozen=True)
class ReconciliationItem:
    reference: str
    status: ReconciliationStatus
    internal_amount: int | None
    external_amount: int | None


class ReconciliationBook:
    def compare(
        self,
        internal: Iterable[Movement],
        external: Iterable[Movement],
    ) -> list[ReconciliationItem]:
        internal_map = self._index(internal)
        external_map = self._index(external)
        items: list[ReconciliationItem] = []

        for reference in sorted(set(internal_map) | set(external_map)):
            left = internal_map.get(reference)
            right = external_map.get(reference)
            if left is None:
                status = ReconciliationStatus.MISSING_INTERNAL
            elif right is None:
                status = ReconciliationStatus.MISSING_EXTERNAL
            elif left.currency != right.currency or left.amount_minor != right.amount_minor:
                status = ReconciliationStatus.AMOUNT_MISMATCH
            else:
                status = ReconciliationStatus.MATCHED
            items.append(
                ReconciliationItem(
                    reference,
                    status,
                    left.amount_minor if left else None,
                    right.amount_minor if right else None,
                )
            )
        return items

    @staticmethod
    def resolve_unknown(result: OperationResult, external_reference: str) -> OperationResult:
        if result.outcome is not Outcome.UNKNOWN:
            raise ValidationError("somente UNKNOWN pode ser reconciliado")
        if not external_reference:
            raise ValidationError("referência externa obrigatória")
        return OperationResult(Outcome.SUCCEEDED, external_reference, {}, result.attempts)

    @staticmethod
    def _index(movements: Iterable[Movement]) -> dict[str, Movement]:
        indexed: dict[str, Movement] = {}
        for movement in movements:
            if movement.reference in indexed:
                raise ValidationError("referência duplicada na reconciliação")
            indexed[movement.reference] = movement
        return indexed
