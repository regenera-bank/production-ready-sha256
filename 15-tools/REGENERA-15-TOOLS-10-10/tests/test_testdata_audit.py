import unittest
from dataclasses import replace
from regenera_tools.testdata import SyntheticData
from regenera_tools.audit import AuditChain
class TestDataAuditTest(unittest.TestCase):
 def test_seed_short(self): self.assertRaises(ValueError,SyntheticData,"short")
 def test_customer_deterministic(self): self.assertEqual(SyntheticData("a"*16).customer(1),SyntheticData("a"*16).customer(1))
 def test_customer_diff(self): self.assertNotEqual(SyntheticData("a"*16).customer(1),SyntheticData("a"*16).customer(2))
 def test_invalid_domain(self): self.assertTrue(SyntheticData("a"*16).customer(1)["email"].endswith("@example.invalid"))
 def test_marker(self): self.assertTrue(SyntheticData("a"*16).customer(1)["customer_id"].startswith("SYN-"))
 def test_negative(self): self.assertRaises(ValueError,SyntheticData("a"*16).customer,-1)
 def test_transaction_minor(self): self.assertEqual(SyntheticData("a"*16).transaction(2)["amount_minor"],102)
 def test_transaction_flag(self): self.assertIs(SyntheticData("a"*16).transaction(2)["synthetic"],True)
 def test_chain_empty(self): self.assertTrue(AuditChain().verify())
 def test_chain(self): c=AuditChain();c.append({"x":1});c.append({"x":2});self.assertTrue(c.verify())
 def test_previous(self): c=AuditChain();a=c.append({"x":1});b=c.append({"x":2});self.assertEqual(b.previous_hash,a.hash)
 def test_tamper_payload(self): c=AuditChain();c.append({"x":1});c.entries[0]=replace(c.entries[0],payload={"x":2});self.assertFalse(c.verify())
 def test_tamper_hash(self): c=AuditChain();c.append({"x":1});c.entries[0]=replace(c.entries[0],hash="0"*64);self.assertFalse(c.verify())
