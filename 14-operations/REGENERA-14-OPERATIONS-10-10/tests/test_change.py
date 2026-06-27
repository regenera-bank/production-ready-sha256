import unittest
from datetime import timedelta
from regenera_operations.change import ChangeRequest,ChangeRisk,ChangeState
from regenera_operations.access import Approval
from regenera_operations.errors import StateTransitionError,AuthorizationError
from common import NOW,LATER,D

class ChangeTests(unittest.TestCase):
    def make(self,emergency=False): return ChangeRequest("CHG-1","req","alterar rota",ChangeRisk.HIGH,"restaurar rota",emergency=emergency)
    def approved(self,emergency=False):
        c=self.make(emergency); a=Approval("req","approver",c.payload_digest(),LATER,True); c.approve(a,NOW); return c
    def test_approve(self): self.assertEqual(self.approved().state,ChangeState.APPROVED)
    def test_wrong_requester(self):
        c=self.make(); a=Approval("other","approver",c.payload_digest(),LATER,True)
        with self.assertRaises(AuthorizationError): c.approve(a,NOW)
    def test_schedule(self):
        c=self.approved(); c.schedule(LATER); self.assertEqual(c.state,ChangeState.SCHEDULED)
    def test_blackout(self):
        c=self.approved()
        with self.assertRaises(StateTransitionError): c.schedule(LATER,blackout=True)
    def test_emergency_blackout(self):
        c=self.approved(True); c.schedule(LATER,blackout=True); self.assertEqual(c.state,ChangeState.SCHEDULED)
    def test_approver_cannot_execute(self):
        c=self.approved(); c.schedule(LATER)
        with self.assertRaises(AuthorizationError): c.start("approver")
    def test_verify_requires_reconciliation(self):
        c=self.approved(); c.schedule(LATER); c.start("executor")
        with self.assertRaises(StateTransitionError): c.verify(D,False)
    def test_close_requires_independence(self):
        c=self.approved(); c.schedule(LATER); c.start("executor"); c.verify(D,True)
        with self.assertRaises(AuthorizationError): c.close("req")
    def test_executor_cannot_close(self):
        c=self.approved(); c.schedule(LATER); c.start("executor"); c.verify(D,True)
        with self.assertRaises(AuthorizationError): c.close("executor")
    def test_full_flow(self):
        c=self.approved(); c.schedule(LATER); c.start("executor"); c.verify(D,True); c.close("reviewer"); self.assertEqual(c.state,ChangeState.CLOSED)
    def test_emergency_requires_retrospective(self):
        c=self.approved(True); c.schedule(LATER); c.start("executor"); c.verify(D,True)
        with self.assertRaises(StateTransitionError): c.close("reviewer")
    def test_emergency_with_retrospective(self):
        c=self.approved(True); c.schedule(LATER); c.start("executor"); c.verify(D,True); c.retrospective_digest=D; c.close("reviewer"); self.assertEqual(c.state,ChangeState.CLOSED)
    def test_rollback(self):
        c=self.approved(); c.schedule(LATER); c.start("executor"); c.rollback(D); self.assertEqual(c.state,ChangeState.ROLLED_BACK)
