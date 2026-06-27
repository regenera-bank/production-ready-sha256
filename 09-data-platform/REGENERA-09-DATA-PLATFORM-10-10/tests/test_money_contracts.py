import unittest
from regenera_data_platform.money import Money, MoneyError
from regenera_data_platform.contracts import DataContract, DataField, ContractRegistry, ContractError


def contract(version="1.0.0", fields=None):
    return DataContract("transactions", version, "finance", ("id",), tuple(fields or [
        DataField("id", "string", True, "INTERNAL"),
        DataField("amount_cents", "integer", True, "CONFIDENTIAL"),
    ]))


class MoneyTests(unittest.TestCase):
    def test_integer_cents(self): self.assertEqual(Money.from_cents("123").amount_cents, 123)
    def test_float_rejected(self):
        with self.assertRaises(MoneyError): Money.from_cents(1.2)
    def test_bool_rejected(self):
        with self.assertRaises(MoneyError): Money.from_cents(True)
    def test_currency_rejected(self):
        with self.assertRaises(MoneyError): Money.from_cents(1, "brl")
    def test_overflow_rejected(self):
        with self.assertRaises(MoneyError): Money.from_cents(9_223_372_036_854_775_808)
    def test_mixed_currency_rejected(self):
        with self.assertRaises(MoneyError): Money.from_cents(1,"BRL").add(Money.from_cents(1,"USD"))


class ContractTests(unittest.TestCase):
    def test_valid_record(self): self.assertEqual(contract().validate_record({"id":"x","amount_cents":10}), [])
    def test_missing_required(self): self.assertIn("required:id", contract().validate_record({"amount_cents":10}))
    def test_unknown_field(self): self.assertIn("unknown:x", contract().validate_record({"id":"1","amount_cents":1,"x":2}))
    def test_wrong_type(self): self.assertIn("type:amount_cents", contract().validate_record({"id":"1","amount_cents":"1"}))
    def test_duplicate_field_rejected(self):
        with self.assertRaises(ContractError): DataContract("x","1.0.0","o",("id",),(DataField("id","string",True,"INTERNAL"),DataField("id","string",True,"INTERNAL")))
    def test_published_version_immutable(self):
        registry=ContractRegistry(); registry.publish(contract())
        with self.assertRaises(ContractError): registry.publish(DataContract("transactions","1.0.0","finance",("id",),(DataField("id","string",True,"INTERNAL"),)))
    def test_breaking_change_requires_major(self):
        registry=ContractRegistry(); registry.publish(contract())
        with self.assertRaises(ContractError): registry.publish(DataContract("transactions","1.1.0","finance",("id",),(DataField("id","string",True,"INTERNAL"),)))
    def test_optional_field_requires_minor(self):
        registry=ContractRegistry(); registry.publish(contract())
        registry.publish(contract("1.1.0", [DataField("id","string",True,"INTERNAL"),DataField("amount_cents","integer",True,"CONFIDENTIAL"),DataField("memo","string",False,"INTERNAL")]))
        self.assertEqual(registry.get("transactions","1.1.0").version,"1.1.0")

if __name__ == '__main__': unittest.main()
