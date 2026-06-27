import unittest
from datetime import date
from regenera_regulatory.privacy import AccessGrant,RetentionRecord,DataSubjectRequest
from regenera_regulatory.errors import AuthorizationError,ValidationError,StateTransitionError

class PrivacyTests(unittest.TestCase):
    def grant(self): return AccessGrant('GRT-001','SUB-001','AUDIT','CONFIDENTIAL','2026-12-31T23:59:59Z','USR-002','USR-001')
    def test_self_approved_grant_is_blocked(self):
        with self.assertRaises(AuthorizationError): AccessGrant('GRT-001','SUB-001','AUDIT','CONFIDENTIAL','2026-12-31T23:59:59Z','USR-001','USR-001')
    def test_purpose_is_required(self):
        with self.assertRaises(ValidationError): AccessGrant('GRT-001','SUB-001','','CONFIDENTIAL','2026-12-31T23:59:59Z','USR-002','USR-001')

    def test_naive_grant_expiration_is_blocked(self):
        with self.assertRaises(ValidationError): AccessGrant('GRT-001','SUB-001','AUDIT','CONFIDENTIAL','2026-12-31T23:59:59','USR-002','USR-001')
    def test_invalid_retention_date_is_blocked(self):
        with self.assertRaises(ValueError): RetentionRecord('REC-001','not-a-date')
    def test_matching_purpose_is_allowed(self): self.assertTrue(self.grant().allows('AUDIT','INTERNAL','2026-01-01T00:00:00Z'))
    def test_other_purpose_is_blocked(self): self.assertFalse(self.grant().allows('MARKETING','INTERNAL','2026-01-01T00:00:00Z'))
    def test_higher_classification_is_blocked(self): self.assertFalse(self.grant().allows('AUDIT','RESTRICTED','2026-01-01T00:00:00Z'))
    def test_expired_grant_is_blocked(self): self.assertFalse(self.grant().allows('AUDIT','INTERNAL','2027-01-01T00:00:00Z'))
    def test_retention_blocks_early_disposal(self): self.assertFalse(RetentionRecord('REC-001','2027-01-01').can_dispose(date(2026,1,1)))
    def test_retention_allows_due_disposal(self): self.assertTrue(RetentionRecord('REC-001','2026-01-01').can_dispose(date(2026,1,1)))
    def test_legal_hold_blocks_disposal(self): self.assertFalse(RetentionRecord('REC-001','2020-01-01',True).can_dispose(date(2026,1,1)))
    def test_invalid_request_type(self):
        with self.assertRaises(ValidationError): DataSubjectRequest('DSR-001','SUB-001','UNKNOWN','2026-02-01')
    def test_complete_before_identity_is_blocked(self):
        with self.assertRaises(StateTransitionError): DataSubjectRequest('DSR-001','SUB-001','ACCESS','2026-02-01').complete({'x':1},'USR-002','USR-001')
    def test_independent_review_is_required(self):
        r=DataSubjectRequest('DSR-001','SUB-001','ACCESS','2026-02-01'); r.verify_identity()
        with self.assertRaises(AuthorizationError): r.complete({'x':1},'USR-001','USR-001')
    def test_evidence_is_required(self):
        r=DataSubjectRequest('DSR-001','SUB-001','ACCESS','2026-02-01'); r.verify_identity()
        with self.assertRaises(ValidationError): r.complete({},'USR-002','USR-001')
    def test_request_completes_with_digest(self):
        r=DataSubjectRequest('DSR-001','SUB-001','ACCESS','2026-02-01'); r.verify_identity(); self.assertEqual(len(r.complete({'export':'a'*64},'USR-002','USR-001')),64)
