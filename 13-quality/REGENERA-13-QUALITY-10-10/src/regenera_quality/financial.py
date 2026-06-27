from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
from .money import Money

@dataclass(frozen=True, slots=True)
class Posting:
    account: str
    side: str
    amount: Money

@dataclass(frozen=True, slots=True)
class Journal:
    journal_id: str
    postings: tuple[Posting, ...]
    digest: str


def validate_journal(postings: tuple[Posting, ...]) -> None:
    if len(postings) < 2:
        raise ValueError("journal_requires_two_postings")
    currencies = {p.amount.currency for p in postings}
    if len(currencies) != 1:
        raise ValueError("journal_currency_mismatch")
    debit = 0
    credit = 0
    for p in postings:
        p.amount.require_positive()
        if p.side == "DEBIT":
            debit += p.amount.minor
        elif p.side == "CREDIT":
            credit += p.amount.minor
        else:
            raise ValueError("invalid_posting_side")
    if debit != credit:
        raise ValueError("unbalanced_journal")


class JournalRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Journal] = {}
        self._lock = Lock()

    @staticmethod
    def _digest(postings: tuple[Posting, ...]) -> str:
        raw = "|".join(
            f"{p.account}:{p.side}:{p.amount.minor}:{p.amount.currency}"
            for p in postings
        )
        return sha256(raw.encode()).hexdigest()

    def post(self, key: str, journal_id: str, postings: tuple[Posting, ...]) -> Journal:
        validate_journal(postings)
        digest = self._digest(postings)
        with self._lock:
            existing = self._items.get(key)
            if existing:
                if existing.digest != digest:
                    raise ValueError("idempotency_conflict")
                return existing
            journal = Journal(journal_id, postings, digest)
            self._items[key] = journal
            return journal
