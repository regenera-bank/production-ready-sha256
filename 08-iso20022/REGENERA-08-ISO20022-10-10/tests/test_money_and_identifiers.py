import unittest
from decimal import Decimal

from regenera_iso20022.errors import ValidationError
from regenera_iso20022.model import Money, parse_signed_amount, validate_bic, validate_identifier


class MoneyAndIdentifiersTests(unittest.TestCase):
    def test_money_accepts_brl_cents(self):
        self.assertEqual(Money.parse('10.25', 'BRL').amount, Decimal('10.25'))

    def test_money_rejects_float_scale(self):
        with self.assertRaises(ValidationError):
            Money.parse('10.255', 'BRL')

    def test_money_rejects_zero(self):
        with self.assertRaises(ValidationError):
            Money.parse('0', 'BRL')

    def test_money_rejects_negative(self):
        with self.assertRaises(ValidationError):
            Money.parse('-1.00', 'BRL')

    def test_money_rejects_unknown_currency(self):
        with self.assertRaises(ValidationError):
            Money.parse('1.00', 'ZZZ')

    def test_balance_accepts_zero_and_negative(self):
        self.assertEqual(parse_signed_amount('0.00', 'BRL'), Decimal('0.00'))
        self.assertEqual(parse_signed_amount('-10.25', 'BRL'), Decimal('-10.25'))

    def test_balance_rejects_excessive_scale(self):
        with self.assertRaises(ValidationError):
            parse_signed_amount('-10.251', 'BRL')

    def test_bic_accepts_eight_or_eleven(self):
        self.assertEqual(validate_bic('AAAABRSP'), 'AAAABRSP')
        self.assertEqual(validate_bic('AAAABRSPXXX'), 'AAAABRSPXXX')

    def test_bic_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_bic('BAD')

    def test_identifier_rejects_too_long(self):
        with self.assertRaises(ValidationError):
            validate_identifier('x' * 36)
