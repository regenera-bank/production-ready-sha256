from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class WarehouseError(RuntimeError):
    pass


@dataclass(slots=True)
class DimensionRow:
    business_key: str
    valid_from: datetime
    valid_to: datetime | None
    values: dict[str, Any]


class SCD2Table:
    def __init__(self) -> None:
        self._rows: list[DimensionRow] = []

    @property
    def rows(self) -> tuple[DimensionRow, ...]:
        return tuple(self._rows)

    def upsert(self, business_key: str, effective_at: datetime, values: dict[str, Any]) -> DimensionRow:
        if not business_key or not values:
            raise WarehouseError("dimensão incompleta")
        current = [row for row in self._rows if row.business_key == business_key and row.valid_to is None]
        if current:
            active = current[0]
            if effective_at <= active.valid_from:
                raise WarehouseError("vigência retroativa ou sobreposta")
            if active.values == values:
                return active
            active.valid_to = effective_at
        row = DimensionRow(business_key, effective_at, None, dict(values))
        self._rows.append(row)
        return row

    def as_of(self, business_key: str, instant: datetime) -> DimensionRow | None:
        matches = [row for row in self._rows if row.business_key == business_key
                   and row.valid_from <= instant and (row.valid_to is None or instant < row.valid_to)]
        if len(matches) > 1:
            raise WarehouseError("sobreposição temporal detectada")
        return matches[0] if matches else None
