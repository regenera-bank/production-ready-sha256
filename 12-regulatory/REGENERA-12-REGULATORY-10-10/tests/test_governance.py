import unittest
from datetime import date
from regenera_regulatory.governance import Control,ExceptionRecord,RegulatoryChange
from regenera_regulatory.errors import AuthorizationError,ValidationError

H='a'*64
class GovernanceTests(unittest.TestCase):
    def test_control_with_evidence_is_effective(self): self.assertTrue(Control('REG-001','Owner',H,'2026-12-31').effective(date(2026,1,1)))
    def test_control_without_owner_is_ineffective(self): self.assertFalse(Control('REG-001','',H,'2026-12-31').effective(date(2026,1,1)))
    def test_control_without_evidence_is_ineffective(self): self.assertFalse(Control('REG-001','Owner',None,'2026-12-31').effective(date(2026,1,1)))
    def test_control_with_bad_hash_is_ineffective(self): self.assertFalse(Control('REG-001','Owner','bad','2026-12-31').effective(date(2026,1,1)))
    def test_expired_control_is_ineffective(self): self.assertFalse(Control('REG-001','Owner',H,'2025-12-31').effective(date(2026,1,1)))
    def test_external_dependency_blocks_effectiveness(self): self.assertFalse(Control('REG-001','Owner',H,'2026-12-31',True).effective(date(2026,1,1)))
    def test_exception_self_approval_is_blocked(self):
        with self.assertRaises(AuthorizationError): ExceptionRecord('EXC-001','REG-001','USR-001','USR-001','2026-12-31','reason','control')
    def test_exception_needs_reason(self):
        with self.assertRaises(ValidationError): ExceptionRecord('EXC-001','REG-001','USR-001','USR-002','2026-12-31','','control')
    def test_exception_valid_before_expiration(self): self.assertTrue(ExceptionRecord('EXC-001','REG-001','USR-001','USR-002','2026-12-31','reason','control').valid(date(2026,1,1)))
    def test_exception_invalid_after_expiration(self): self.assertFalse(ExceptionRecord('EXC-001','REG-001','USR-001','USR-002','2025-12-31','reason','control').valid(date(2026,1,1)))
    def test_change_requires_valid_hash(self):
        with self.assertRaises(ValidationError): RegulatoryChange('CHG-001','bad','USR-001')
    def test_change_self_assessment_is_blocked(self):
        with self.assertRaises(AuthorizationError): RegulatoryChange('CHG-001',H,'USR-001').assess('HIGH','USR-001')
    def test_change_impact_is_validated(self):
        with self.assertRaises(ValidationError): RegulatoryChange('CHG-001',H,'USR-001').assess('SEVERE','USR-002')
    def test_change_approval_requires_assessment(self):
        with self.assertRaises(ValidationError): RegulatoryChange('CHG-001',H,'USR-001').approve('USR-002')
    def test_change_can_be_approved_independently(self):
        c=RegulatoryChange('CHG-001',H,'USR-001'); c.assess('HIGH','USR-002'); c.approve('USR-003'); self.assertEqual(c.state,'APPROVED')
