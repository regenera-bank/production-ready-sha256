import unittest
from dataclasses import replace
from regenera_regulatory.audit import AuditChain
from regenera_regulatory.errors import ConflictError,ValidationError

class AuditTests(unittest.TestCase):
    def setUp(self): self.chain=AuditChain()
    def test_empty_chain_is_valid(self): self.assertTrue(self.chain.verify())
    def test_append_creates_record(self): self.assertEqual(self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{'a':1}).event_id,'EVT-001')
    def test_chain_links_records(self):
        a=self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{})
        b=self.chain.append('EVT-002','USR-002','APPROVE','OBJ-001',{})
        self.assertEqual(b.previous_hash,a.record_hash)
    def test_duplicate_event_is_blocked(self):
        self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{})
        with self.assertRaises(ConflictError): self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{})
    def test_non_utc_timestamp_is_blocked(self):
        with self.assertRaises(ValidationError): self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{},'2026-01-01T10:00:00')
    def test_invalid_identifier_is_blocked(self):
        with self.assertRaises(ValidationError): self.chain.append('x','USR-001','CREATE','OBJ-001',{})
    def test_payload_changes_digest(self):
        a=self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{'a':1})
        other=AuditChain().append('EVT-001','USR-001','CREATE','OBJ-001',{'a':2})
        self.assertNotEqual(a.payload_digest,other.payload_digest)
    def test_tampering_is_detected(self):
        self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{})
        self.chain._records[0]=replace(self.chain._records[0],action='DELETE')
        self.assertFalse(self.chain.verify())
    def test_records_are_exposed_as_tuple(self): self.assertIsInstance(self.chain.records,tuple)
    def test_record_is_immutable(self):
        r=self.chain.append('EVT-001','USR-001','CREATE','OBJ-001',{})
        with self.assertRaises(Exception): r.action='DELETE'
