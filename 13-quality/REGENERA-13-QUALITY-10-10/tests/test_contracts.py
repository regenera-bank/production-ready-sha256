import unittest
from regenera_quality.contracts import Contract, compatibility_breaks, validate_evolution

class ContractTests(unittest.TestCase):
    def c(self, major=1, required=frozenset({"id"}), fields=None):
        return Contract("payment", major, required, fields or {"id":"string","amount":"integer"})
    def test_required_needs_type(self): self.assertRaises(ValueError, Contract, "x", 1, frozenset({"x"}), {})
    def test_identity_required(self): self.assertRaises(ValueError, Contract, "", 1, frozenset(), {})
    def test_removed_field_breaks(self): self.assertTrue(compatibility_breaks(self.c(), self.c(fields={"id":"string"})))
    def test_new_required_breaks(self): self.assertTrue(compatibility_breaks(self.c(), self.c(required=frozenset({"id","amount"}))))
    def test_type_change_breaks(self): self.assertTrue(compatibility_breaks(self.c(), self.c(fields={"id":"string","amount":"number"})))
    def test_break_requires_major(self): self.assertRaises(ValueError, validate_evolution, self.c(), self.c(fields={"id":"string"}))
    def test_break_with_major_allowed(self): validate_evolution(self.c(), self.c(major=2, fields={"id":"string"}))
    def test_add_optional_compatible(self): validate_evolution(self.c(), self.c(fields={"id":"string","amount":"integer","memo":"string"}))
    def test_name_change_rejected(self): self.assertRaises(ValueError, validate_evolution, self.c(), Contract("account",1,frozenset(),{}))
    def test_major_regression(self): self.assertRaises(ValueError, validate_evolution, self.c(2), self.c(1))
