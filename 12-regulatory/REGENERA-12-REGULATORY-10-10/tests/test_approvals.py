import unittest
from regenera_regulatory.approvals import ApprovalRequest
from regenera_regulatory.errors import ValidationError,AuthorizationError,StateTransitionError

H='a'*64
class ApprovalTests(unittest.TestCase):
    def make(self): return ApprovalRequest('APR-001',H,'USR-001','2026-12-31T23:59:59Z')
    def test_invalid_digest(self):
        with self.assertRaises(ValidationError): ApprovalRequest('APR-001','bad','USR-001','2026-12-31T23:59:59Z')
    def test_naive_expiration_is_blocked(self):
        with self.assertRaises(ValidationError): ApprovalRequest('APR-001',H,'USR-001','2026-12-31T23:59:59')
    def test_self_approval_is_blocked(self):
        with self.assertRaises(AuthorizationError): self.make().approve('USR-001',True,'1234567890ABCDEF','2026-01-01T00:00:00Z')
    def test_mfa_is_required(self):
        with self.assertRaises(AuthorizationError): self.make().approve('USR-002',False,'1234567890ABCDEF','2026-01-01T00:00:00Z')
    def test_fingerprint_is_required(self):
        with self.assertRaises(ValidationError): self.make().approve('USR-002',True,'short','2026-01-01T00:00:00Z')
    def test_expired_approval_is_blocked(self):
        a=self.make()
        with self.assertRaises(StateTransitionError): a.approve('USR-002',True,'1234567890ABCDEF','2027-01-01T00:00:00Z')
        self.assertEqual(a.state,'EXPIRED')
    def test_approval_succeeds(self): self.assertEqual(self.make().approve('USR-002',True,'1234567890ABCDEF','2026-01-01T00:00:00Z').payload_digest,H)
    def test_second_decision_is_blocked(self):
        a=self.make(); a.approve('USR-002',True,'1234567890ABCDEF','2026-01-01T00:00:00Z')
        with self.assertRaises(StateTransitionError): a.approve('USR-003',True,'1234567890ABCDEF','2026-01-02T00:00:00Z')
    def test_rejection_requires_reason(self):
        with self.assertRaises(ValidationError): self.make().reject('USR-002','')
    def test_rejection_by_maker_is_blocked(self):
        with self.assertRaises(AuthorizationError): self.make().reject('USR-001','erro')
    def test_rejection_changes_state(self):
        a=self.make(); a.reject('USR-002','dados divergentes'); self.assertEqual(a.state,'REJECTED')
