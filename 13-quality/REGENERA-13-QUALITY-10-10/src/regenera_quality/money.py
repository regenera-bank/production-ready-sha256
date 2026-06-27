from dataclasses import dataclass

MAX_MINOR = 9_000_000_000_000_000
_ALLOWED = {"BRL", "USD", "EUR"}

@dataclass(frozen=True, slots=True)
class Money:
    minor: int
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if isinstance(self.minor, bool) or not isinstance(self.minor, int):
            raise TypeError("money_requires_integer_minor_units")
        if abs(self.minor) > MAX_MINOR:
            raise OverflowError("money_overflow")
        if self.currency not in _ALLOWED:
            raise ValueError("unsupported_currency")

    def add(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.minor + other.minor, self.currency)

    def subtract(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.minor - other.minor, self.currency)

    def require_positive(self) -> "Money":
        if self.minor <= 0:
            raise ValueError("amount_must_be_positive")
        return self

    def _same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("currency_mismatch")
