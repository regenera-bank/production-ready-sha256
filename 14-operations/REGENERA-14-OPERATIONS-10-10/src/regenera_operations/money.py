from __future__ import annotations
from dataclasses import dataclass
import re
from .errors import ValidationError

_MAX = 2**63 - 1
_CURRENCY = re.compile(r"^[A-Z]{3}$")

@dataclass(frozen=True, slots=True)
class Money:
    minor: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.minor, bool) or not isinstance(self.minor, int):
            raise ValidationError("valor monetário precisa usar unidade mínima inteira")
        if abs(self.minor) > _MAX:
            raise ValidationError("overflow monetário")
        if not _CURRENCY.fullmatch(self.currency):
            raise ValidationError("moeda inválida")

    def positive(self) -> "Money":
        if self.minor <= 0:
            raise ValidationError("valor precisa ser positivo")
        return self

    def _same(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValidationError("moedas divergentes")

    def __add__(self, other: "Money") -> "Money":
        self._same(other)
        return Money(self.minor + other.minor, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._same(other)
        return Money(self.minor - other.minor, self.currency)
