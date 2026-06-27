import unittest
from regenera_quality.money import Money, MAX_MINOR

class MoneyTests(unittest.TestCase):
    def test_integer_minor_units(self): self.assertEqual(Money(100).minor, 100)
    def test_bool_rejected(self): self.assertRaises(TypeError, Money, True)
    def test_float_rejected(self): self.assertRaises(TypeError, Money, 1.2)
    def test_overflow_positive(self): self.assertRaises(OverflowError, Money, MAX_MINOR + 1)
    def test_overflow_negative(self): self.assertRaises(OverflowError, Money, -MAX_MINOR - 1)
    def test_currency_rejected(self): self.assertRaises(ValueError, Money, 1, "XXX")
    def test_add(self): self.assertEqual(Money(10).add(Money(20)), Money(30))
    def test_subtract(self): self.assertEqual(Money(30).subtract(Money(20)), Money(10))
    def test_currency_mismatch(self): self.assertRaises(ValueError, Money(1).add, Money(1, "USD"))
    def test_positive_required(self): self.assertRaises(ValueError, Money(0).require_positive)
