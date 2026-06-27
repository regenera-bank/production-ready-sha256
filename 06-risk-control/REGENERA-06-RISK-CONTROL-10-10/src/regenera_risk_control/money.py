from __future__ import annotations
from dataclasses import dataclass

MAX_CENTS = 9_223_372_036_854_775_807


class MoneyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = 'BRL'

    def __post_init__(self) -> None:
        if isinstance(self.cents, bool) or not isinstance(self.cents, int):
            raise MoneyError('centavos precisam ser inteiros')
        if abs(self.cents) > MAX_CENTS:
            raise MoneyError('valor excede BIGINT assinado')
        if len(self.currency) != 3 or not self.currency.isalpha() or not self.currency.isupper():
            raise MoneyError('moeda inválida')

    def _same(self, other: 'Money') -> None:
        if self.currency != other.currency:
            raise MoneyError('moedas diferentes não se misturam')

    def add(self, other: 'Money') -> 'Money':
        self._same(other)
        return Money(self.cents + other.cents, self.currency)

    def subtract(self, other: 'Money') -> 'Money':
        self._same(other)
        return Money(self.cents - other.cents, self.currency)

    def positive(self) -> bool:
        return self.cents > 0
