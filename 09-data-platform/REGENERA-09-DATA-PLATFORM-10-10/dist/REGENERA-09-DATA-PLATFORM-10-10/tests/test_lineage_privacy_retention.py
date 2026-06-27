import unittest
from datetime import datetime, timedelta, timezone
from regenera_data_platform.lineage import LineageChain
from regenera_data_platform.privacy import DataClass, PrivacyPolicy, PrivacyError, mask_email, mask_document, tokenize
from regenera_data_platform.retention import RetentionPolicy, RetentionRecord, RetentionError


class LineageTests(unittest.TestCase):
    def test_empty_chain_valid(self): self.assertTrue(LineageChain().verify())
    def test_chain_valid(self):
        c=LineageChain(); c.append("a","INGEST",(),"a"*64); c.append("b","TRANSFORM",("a"*64,),"b"*64); self.assertTrue(c.verify())
    def test_tamper_detected(self):
        c=LineageChain(); c.append("a","INGEST",(),"a"*64); c.tamper_for_test(0,"b"*64); self.assertFalse(c.verify())


class PrivacyTests(unittest.TestCase):
    def setUp(self): self.policy=PrivacyPolicy(frozenset({"FRAUD"}),{"analyst":DataClass.CONFIDENTIAL})
    def test_authorized(self): self.policy.authorize("analyst","FRAUD",DataClass.CONFIDENTIAL)
    def test_wrong_purpose(self):
        with self.assertRaises(PrivacyError): self.policy.authorize("analyst","MARKETING",DataClass.INTERNAL)
    def test_class_above_role(self):
        with self.assertRaises(PrivacyError): self.policy.authorize("analyst","FRAUD",DataClass.RESTRICTED)
    def test_mask_email(self): self.assertEqual(mask_email("paulo@example.com"),"pa***@example.com")
    def test_mask_document(self): self.assertEqual(mask_document("123.456.789-00"),"123***00")
    def test_weak_secret_rejected(self):
        with self.assertRaises(ValueError): tokenize("x",b"short")
    def test_token_stable(self): self.assertEqual(tokenize("x",b"a"*32),tokenize("x",b"a"*32))


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,6,26,tzinfo=timezone.utc)
        self.policy=RetentionPolicy("FIN",30,"legal","CRYPTO_ERASURE")
    def test_early_disposal_blocked(self):
        r=RetentionRecord("1",self.now,self.policy)
        with self.assertRaises(RetentionError): r.dispose(self.now+timedelta(days=29),"a"*64)
    def test_legal_hold_blocks(self):
        r=RetentionRecord("1",self.now-timedelta(days=40),self.policy,legal_hold=True)
        with self.assertRaises(RetentionError): r.dispose(self.now,"a"*64)
    def test_evidence_required(self):
        r=RetentionRecord("1",self.now-timedelta(days=40),self.policy)
        with self.assertRaises(RetentionError): r.dispose(self.now,"bad")
    def test_disposal_recorded(self):
        r=RetentionRecord("1",self.now-timedelta(days=40),self.policy); r.dispose(self.now,"a"*64); self.assertEqual(r.evidence_hash,"a"*64)
    def test_second_disposal_blocked(self):
        r=RetentionRecord("1",self.now-timedelta(days=40),self.policy); r.dispose(self.now,"a"*64)
        with self.assertRaises(RetentionError): r.dispose(self.now,"a"*64)

if __name__ == '__main__': unittest.main()
