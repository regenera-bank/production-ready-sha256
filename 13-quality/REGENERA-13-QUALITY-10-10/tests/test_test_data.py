import unittest
from regenera_quality.test_data import synthetic_customer, contains_real_contact

class TestDataTests(unittest.TestCase):
    def test_short_seed_rejected(self): self.assertRaises(ValueError,synthetic_customer,"short")
    def test_deterministic(self): self.assertEqual(synthetic_customer("stable-seed"),synthetic_customer("stable-seed"))
    def test_different_seed(self): self.assertNotEqual(synthetic_customer("stable-seed"),synthetic_customer("other-seed"))
    def test_invalid_domain(self): self.assertTrue(synthetic_customer("stable-seed").email.endswith(".invalid"))
    def test_token_not_seed(self): self.assertNotIn("stable-seed",synthetic_customer("stable-seed").document_token)
    def test_real_contact_detected(self): self.assertTrue(contains_real_contact("x@gmail.com"))
    def test_synthetic_contact_allowed(self): self.assertFalse(contains_real_contact("x@example.invalid"))
