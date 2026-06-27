from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class FinancialError(Exception):
    pass

class UnknownStateError(FinancialError):
    pass

class CurrencyMismatch(FinancialError):
    pass

class ImmutableEntry(FinancialError):
    pass

class State(str, Enum):
    RECEIVED = 'RECEIVED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    UNKNOWN = 'UNKNOWN'
    FAILED = 'FAILED'

@dataclass(frozen=True)
class Line:
    account: str
    direction: str
    cents: int
    currency: str = 'BRL'

@dataclass(frozen=True)
class Entry:
    entry_id: str
    lines: tuple[Line, ...]
    reversal_of: str | None = None

class Ledger:
    def __init__(self):
        self._entries: dict[str, Entry] = {}

    def post(self, entry: Entry) -> Entry:
        if entry.entry_id in self._entries:
            return self._entries[entry.entry_id]
        if len({line.currency for line in entry.lines}) != 1:
            raise CurrencyMismatch('currency mismatch')
        signed = sum(line.cents if line.direction == 'DEBIT' else -line.cents for line in entry.lines)
        if signed != 0:
            raise FinancialError('unbalanced posting')
        if any(line.cents <= 0 for line in entry.lines):
            raise FinancialError('non-positive line')
        self._entries[entry.entry_id] = entry
        return entry

    def mutate(self, entry_id: str, _replacement: Entry) -> None:
        if entry_id in self._entries:
            raise ImmutableEntry('posted entry is immutable')
        raise KeyError(entry_id)

    def reverse(self, entry_id: str, reversal_id: str) -> Entry:
        original = self._entries[entry_id]
        lines = tuple(Line(l.account, 'CREDIT' if l.direction == 'DEBIT' else 'DEBIT', l.cents, l.currency) for l in original.lines)
        return self.post(Entry(reversal_id, lines, reversal_of=entry_id))

class IdempotencyStore:
    def __init__(self):
        self._records = {}

    def begin(self, key: str, fingerprint: str):
        record = self._records.get(key)
        if record:
            if record['fingerprint'] != fingerprint:
                raise FinancialError('fingerprint mismatch')
            if record['state'] == State.UNKNOWN:
                raise UnknownStateError('blind retry blocked')
            return record
        record = {'fingerprint': fingerprint, 'state': State.PROCESSING, 'result': None}
        self._records[key] = record
        return record

    def complete(self, key: str, result):
        record = self._records[key]
        record['state'] = State.COMPLETED
        record['result'] = result

    def mark_unknown(self, key: str):
        self._records[key]['state'] = State.UNKNOWN
