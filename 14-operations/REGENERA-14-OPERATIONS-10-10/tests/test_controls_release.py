import unittest
from datetime import timedelta
from regenera_operations.controls import Control,ControlException
from regenera_operations.release import ReleaseGate
from regenera_operations.access import Approval
from regenera_operations.errors import AuthorizationError,ValidationError,StateTransitionError
from common import NOW,LATER,D

class ControlsReleaseTests(unittest.TestCase):
    def test_control_effective(self): self.assertTrue(Control("C","owner",D,LATER).effective(NOW))
    def test_control_expired(self): self.assertFalse(Control("C","owner",D,NOW).effective(NOW))
    def test_control_disabled(self): self.assertFalse(Control("C","owner",D,LATER,False).effective(NOW))
    def test_exception_valid(self): self.assertTrue(ControlException("E","owner","approver","motivo",LATER,D).valid(NOW))
    def test_exception_self_approved(self):
        with self.assertRaises(AuthorizationError): ControlException("E","owner","owner","motivo",LATER,D).valid(NOW)
    def test_exception_reason(self):
        with self.assertRaises(ValidationError): ControlException("E","owner","approver","",LATER,D).valid(NOW)
    def test_exception_expired(self): self.assertFalse(ControlException("E","owner","approver","motivo",NOW,D).valid(NOW))
    def test_release_gate(self):
        approval=Approval("release-owner","reviewer",D,LATER,True); gate=ReleaseGate(D,True,True,True,True,approval); self.assertEqual(gate.evaluate(NOW),"APPROVED_FOR_LOCAL_TECHNICAL_SCOPE")
    def test_release_missing_test(self):
        approval=Approval("release-owner","reviewer",D,LATER,True); gate=ReleaseGate(D,False,True,True,True,approval)
        with self.assertRaises(StateTransitionError): gate.evaluate(NOW)
    def test_release_wrong_digest(self):
        approval=Approval("release-owner","reviewer","b"*64,LATER,True); gate=ReleaseGate(D,True,True,True,True,approval)
        with self.assertRaises(AuthorizationError): gate.evaluate(NOW)
