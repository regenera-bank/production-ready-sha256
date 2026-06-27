from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re

from .errors import ValidationError


CURRENCY_SCALE = {"BRL": 2, "USD": 2, "EUR": 2, "JPY": 0, "GBP": 2}
_IDENTIFIER = re.compile(r"^[A-Za-z0-9/\-?:().,'+ ]{1,35}$")
_BIC = re.compile(r"^[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?$")


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    @classmethod
    def parse(cls, value: str, currency: str) -> "Money":
        if currency not in CURRENCY_SCALE:
            raise ValidationError("CURRENCY_UNSUPPORTED", "Moeda fora do perfil aprovado")
        try:
            amount = Decimal(value)
        except InvalidOperation as exc:
            raise ValidationError("AMOUNT_INVALID", "Valor monetário inválido") from exc
        if not amount.is_finite() or amount <= 0:
            raise ValidationError("AMOUNT_NOT_POSITIVE", "Valor deve ser positivo")
        scale = -amount.as_tuple().exponent
        if scale > CURRENCY_SCALE[currency]:
            raise ValidationError("AMOUNT_SCALE_INVALID", "Escala monetária incompatível")
        if len(amount.as_tuple().digits) > 18:
            raise ValidationError("AMOUNT_OVERFLOW", "Valor excede a precisão aprovada")
        return cls(amount=amount, currency=currency)


def parse_signed_amount(value: str, currency: str) -> Decimal:
    if currency not in CURRENCY_SCALE:
        raise ValidationError("CURRENCY_UNSUPPORTED", "Moeda fora do perfil aprovado")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValidationError("AMOUNT_INVALID", "Valor monetário inválido") from exc
    if not amount.is_finite():
        raise ValidationError("AMOUNT_INVALID", "Valor monetário inválido")
    scale = -amount.as_tuple().exponent
    if scale > CURRENCY_SCALE[currency]:
        raise ValidationError("AMOUNT_SCALE_INVALID", "Escala monetária incompatível")
    if len(amount.as_tuple().digits) > 18:
        raise ValidationError("AMOUNT_OVERFLOW", "Valor excede a precisão aprovada")
    return amount


def validate_identifier(value: str, code: str = "IDENTIFIER_INVALID") -> str:
    if not _IDENTIFIER.fullmatch(value or ""):
        raise ValidationError(code, "Identificador inválido")
    return value


def validate_bic(value: str) -> str:
    if not _BIC.fullmatch(value or ""):
        raise ValidationError("BIC_INVALID", "BIC inválido")
    return value
