import unittest
from regenera_operations.incident import Incident,IncidentState,Severity
from regenera_operations.errors import StateTransitionError,AuthorizationError,ValidationError
from common import NOW,D,D2

class IncidentTests(unittest.TestCase):
    def make(self,severity=Severity.P2): return Incident("INC-1",severity,"falha","owner",NOW)
    def test_initial(self): self.assertEqual(self.make().state,IncidentState.DECLARED)
    def test_full_flow(self):
        i=self.make(); i.advance(IncidentState.ASSESSING,"a",D); i.advance(IncidentState.CONTAINED,"a",D); i.advance(IncidentState.RECOVERING,"a",D); i.reconciliation_complete=True; i.advance(IncidentState.RESOLVED,"a",D); i.advance(IncidentState.CLOSED,"a",D,independent_reviewer="reviewer"); self.assertEqual(i.state,IncidentState.CLOSED)
    def test_skip_state(self):
        with self.assertRaises(StateTransitionError): self.make().advance(IncidentState.CONTAINED,"a",D)
    def test_bad_digest(self):
        with self.assertRaises(ValidationError): self.make().advance(IncidentState.ASSESSING,"a","x")
    def test_resolve_requires_reconciliation(self):
        i=self.make(); i.advance(IncidentState.ASSESSING,"a",D); i.advance(IncidentState.CONTAINED,"a",D); i.advance(IncidentState.RECOVERING,"a",D)
        with self.assertRaises(StateTransitionError): i.advance(IncidentState.RESOLVED,"a",D)
    def test_close_requires_reviewer(self):
        i=self.make(); i.advance(IncidentState.ASSESSING,"a",D); i.advance(IncidentState.CONTAINED,"a",D); i.advance(IncidentState.RECOVERING,"a",D); i.reconciliation_complete=True; i.advance(IncidentState.RESOLVED,"a",D)
        with self.assertRaises(AuthorizationError): i.advance(IncidentState.CLOSED,"a",D,independent_reviewer="owner")
    def test_p1_requires_postmortem(self):
        i=self.make(Severity.P1); i.advance(IncidentState.ASSESSING,"a",D); i.advance(IncidentState.CONTAINED,"a",D); i.advance(IncidentState.RECOVERING,"a",D); i.reconciliation_complete=True; i.advance(IncidentState.RESOLVED,"a",D)
        with self.assertRaises(StateTransitionError): i.advance(IncidentState.CLOSED,"a",D,independent_reviewer="reviewer")
    def test_p1_closes_with_postmortem(self):
        i=self.make(Severity.P1); i.advance(IncidentState.ASSESSING,"a",D); i.advance(IncidentState.CONTAINED,"a",D); i.advance(IncidentState.RECOVERING,"a",D); i.reconciliation_complete=True; i.advance(IncidentState.RESOLVED,"a",D); i.postmortem_digest=D2; i.advance(IncidentState.CLOSED,"a",D,independent_reviewer="reviewer"); self.assertEqual(i.state,IncidentState.CLOSED)
    def test_missing_summary(self):
        with self.assertRaises(ValidationError): Incident("INC",Severity.P2,"","owner",NOW)
