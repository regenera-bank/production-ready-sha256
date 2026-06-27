import unittest
from regenera_operations.runbooks import Runbook,RunbookRegistry
from regenera_operations.support import SupportCase,CaseState,RefundRequest
from regenera_operations.money import Money
from regenera_operations.errors import ValidationError,ConflictError,AuthorizationError,StateTransitionError
from common import D

class RunbookSupportTests(unittest.TestCase):
    def rb(self,steps=("do",)): return Runbook("RB-1","1.0.0","owner",steps,("undo",))
    def test_publish(self): self.assertEqual(RunbookRegistry().publish(self.rb()).version,"1.0.0")
    def test_invalid_version(self):
        with self.assertRaises(ValidationError): Runbook("RB","v1","owner",("do",),("undo",))
    def test_missing_steps(self):
        with self.assertRaises(ValidationError): Runbook("RB","1.0.0","owner",(),("undo",))
    def test_immutable_version(self):
        r=RunbookRegistry(); r.publish(self.rb())
        with self.assertRaises(ConflictError): r.publish(self.rb(("different",)))
    def test_activate(self):
        r=RunbookRegistry(); rb=r.publish(self.rb()); self.assertEqual(r.activate("RB-1","1.0.0",rb.content_digest,"reviewer"),rb)
    def test_owner_cannot_activate(self):
        r=RunbookRegistry(); rb=r.publish(self.rb())
        with self.assertRaises(AuthorizationError): r.activate("RB-1","1.0.0",rb.content_digest,"owner")
    def test_case_allowlist(self): self.assertEqual(SupportCase("C-1","owner",{"summary":"x"}).state,CaseState.OPEN)
    def test_case_rejects_extra_data(self):
        with self.assertRaises(ValidationError): SupportCase("C-1","owner",{"password":"x"})
    def test_case_flow(self):
        c=SupportCase("C-1","owner",{"summary":"x"}); c.investigate(); c.resolve(D); c.close("reviewer"); self.assertEqual(c.state,CaseState.CLOSED)
    def test_case_self_close(self):
        c=SupportCase("C-1","owner",{"summary":"x"}); c.investigate(); c.resolve(D)
        with self.assertRaises(AuthorizationError): c.close("owner")
    def test_refund(self): RefundRequest("R","a","b",Money(100,"BRL"),D).validate(100)
    def test_refund_self_approval(self):
        with self.assertRaises(AuthorizationError): RefundRequest("R","a","a",Money(100,"BRL"),D).validate(100)
    def test_refund_limit(self):
        with self.assertRaises(AuthorizationError): RefundRequest("R","a","b",Money(101,"BRL"),D).validate(100)
    def test_refund_positive(self):
        with self.assertRaises(ValidationError): RefundRequest("R","a","b",Money(0,"BRL"),D).validate(100)
