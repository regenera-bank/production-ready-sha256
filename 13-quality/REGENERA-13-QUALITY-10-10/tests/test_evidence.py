import unittest
from dataclasses import replace
from regenera_quality.evidence import EvidenceChain

class EvidenceTests(unittest.TestCase):
    def test_empty_chain_valid(self): self.assertTrue(EvidenceChain().verify())
    def test_append_sequence(self): self.assertEqual(EvidenceChain().append("test",{}).sequence,1)
    def test_payload_is_canonical(self):
        a=EvidenceChain().append("x",{"a":1,"b":2}); b=EvidenceChain().append("x",{"b":2,"a":1}); self.assertEqual(a.digest,b.digest)
    def test_multiple_records_valid(self):
        c=EvidenceChain(); c.append("a",{}); c.append("b",{}); self.assertTrue(c.verify())
    def test_tampered_digest_detected(self):
        c=EvidenceChain(); c.append("a",{}); c.records[0]=replace(c.records[0],digest="0"*64); self.assertFalse(c.verify())
    def test_tampered_previous_detected(self):
        c=EvidenceChain(); c.append("a",{}); c.append("b",{}); c.records[1]=replace(c.records[1],previous_digest="1"*64); self.assertFalse(c.verify())
    def test_tampered_sequence_detected(self):
        c=EvidenceChain(); c.append("a",{}); c.records[0]=replace(c.records[0],sequence=9); self.assertFalse(c.verify())
    def test_event_required(self): self.assertRaises(ValueError, EvidenceChain().append,"",{})
