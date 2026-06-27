from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum
from .money import Money


class Direction(str, Enum):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


@dataclass(frozen=True, slots=True)
class PostingLine:
    account_code: str
    direction: Direction
    amount: Money


@dataclass(frozen=True, slots=True)
class JournalEntry:
    entry_id: str
    accounting_date: date
    description: str
    lines: tuple[PostingLine, ...]
    reversal_of: str | None = None


class AccountingBook:
    def __init__(self) -> None:
        self._entries: dict[str, JournalEntry] = {}
        self._closed_through: date | None = None

    def close_period(self, closed_through: date) -> None:
        if self._closed_through and closed_through < self._closed_through:
            raise ValueError('período fechado não reabre por regressão')
        self._closed_through = closed_through

    def post(self, entry: JournalEntry) -> JournalEntry:
        if entry.entry_id in self._entries:
            return self._entries[entry.entry_id]
        if self._closed_through and entry.accounting_date <= self._closed_through:
            raise ValueError('período contábil fechado')
        if len(entry.lines) < 2:
            raise ValueError('lançamento precisa de duas pernas')
        currencies = {line.amount.currency for line in entry.lines}
        if len(currencies) != 1:
            raise ValueError('moedas diferentes no mesmo lançamento')
        if any(not line.amount.positive() for line in entry.lines):
            raise ValueError('linha precisa de valor positivo')
        debit = sum(line.amount.cents for line in entry.lines if line.direction == Direction.DEBIT)
        credit = sum(line.amount.cents for line in entry.lines if line.direction == Direction.CREDIT)
        if debit != credit:
            raise ValueError('lançamento desequilibrado')
        self._entries[entry.entry_id] = entry
        return entry

    def reverse(self, original_id: str, reversal_id: str, accounting_date: date,
                reason: str) -> JournalEntry:
        if not reason.strip():
            raise ValueError('estorno exige motivo')
        original = self._entries.get(original_id)
        if original is None:
            raise KeyError('lançamento original não existe')
        if any(item.reversal_of == original_id for item in self._entries.values()):
            raise ValueError('lançamento já estornado')
        lines = tuple(PostingLine(line.account_code,
                                  Direction.CREDIT if line.direction == Direction.DEBIT else Direction.DEBIT,
                                  line.amount) for line in original.lines)
        return self.post(JournalEntry(reversal_id, accounting_date,
                                      f'REVERSAL:{original_id}:{reason}', lines, original_id))

    def entries(self) -> tuple[JournalEntry, ...]:
        return tuple(self._entries.values())
