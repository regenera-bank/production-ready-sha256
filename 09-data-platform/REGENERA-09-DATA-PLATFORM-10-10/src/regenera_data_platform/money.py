from __future__ import annotations

from dataclasses import dataclass
import re

_CENTS = re.compile(r"^-?\d{1,19}$")
_MAX = 9_223_372_036_854_775_807
_MIN = -9_223_372_036_854_775_808
_CURRENCY = re.compile(r"^[A-Z]{3}$")


class MoneyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Money:
    amount_cents: int
    currency: str = "BRL"

    @classmethod
    def from_cents(cls, value: int | str, currency: str = "BRL") -> "Money":
        if isinstance(value, bool):
            raise MoneyError("booleano não representa centavos")
        if isinstance(value, str):
            normalized = value.strip()
            if not _CENTS.fullmatch(normalized):
                raise MoneyError("centavos inválidos")
            cents = int(normalized)
        elif isinstance(value, int):
            cents = value
        else:
            raise MoneyError("dinheiro exige inteiro ou string inteira")
        if not _MIN <= cents <= _MAX:
            raise MoneyError("overflow monetário")
        if not _CURRENCY.fullmatch(currency):
            raise MoneyError("moeda inválida")
        return cls(cents, currency)

    def add(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money.from_cents(self.amount_cents + other.amount_cents, self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money.from_cents(self.amount_cents - other.amount_cents, self.currency)

    def _same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise MoneyError("moedas diferentes não fecham")
