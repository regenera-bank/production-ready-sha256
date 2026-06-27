import unittest
from regenera_operations.money import Money
from regenera_operations.errors import ValidationError

class MoneyTests(unittest.TestCase):
    def test_accepts_integer_minor(self): self.assertEqual(Money(10,"BRL").minor,10)
    def test_rejects_float(self):
        with self.assertRaises(ValidationError): Money(1.2,"BRL")
    def test_rejects_bool(self):
        with self.assertRaises(ValidationError): Money(True,"BRL")
    def test_rejects_currency(self):
        with self.assertRaises(ValidationError): Money(1,"brl")
    def test_add(self): self.assertEqual((Money(2,"BRL")+Money(3,"BRL")).minor,5)
    def test_subtract(self): self.assertEqual((Money(5,"BRL")-Money(3,"BRL")).minor,2)
    def test_currency_mismatch(self):
        with self.assertRaises(ValidationError): Money(1,"BRL")+Money(1,"USD")
    def test_positive(self): self.assertIsInstance(Money(1,"BRL").positive(),Money)
    def test_non_positive(self):
        with self.assertRaises(ValidationError): Money(0,"BRL").positive()
    def test_overflow(self):
        with self.assertRaises(ValidationError): Money(2**63,"BRL")
