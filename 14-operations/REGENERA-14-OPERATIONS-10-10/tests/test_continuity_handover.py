import unittest
from regenera_operations.continuity import ServiceObjective,ContinuityExercise
from regenera_operations.handover import ShiftHandover,HandoverItem
from regenera_operations.errors import ValidationError,StateTransitionError,AuthorizationError
from common import NOW,D

class ContinuityHandoverTests(unittest.TestCase):
    def test_objective(self): self.assertEqual(ServiceObjective("ledger",60,5).rto_minutes,60)
    def test_invalid_objective(self):
        with self.assertRaises(ValidationError): ServiceObjective("",0,-1)
    def test_exercise_passes(self):
        e=ContinuityExercise("EX-1","owner",ServiceObjective("ledger",60,5),NOW); e.conclude(50,3,True,D,"reviewer"); self.assertTrue(e.passed)
    def test_rto_violation(self):
        e=ContinuityExercise("EX-1","owner",ServiceObjective("ledger",60,5),NOW)
        with self.assertRaises(StateTransitionError): e.conclude(61,3,True,D,"reviewer")
    def test_rpo_violation(self):
        e=ContinuityExercise("EX-1","owner",ServiceObjective("ledger",60,5),NOW)
        with self.assertRaises(StateTransitionError): e.conclude(50,6,True,D,"reviewer")
    def test_reconciliation_required(self):
        e=ContinuityExercise("EX-1","owner",ServiceObjective("ledger",60,5),NOW)
        with self.assertRaises(StateTransitionError): e.conclude(50,3,False,D,"reviewer")
    def test_independent_review(self):
        e=ContinuityExercise("EX-1","owner",ServiceObjective("ledger",60,5),NOW)
        with self.assertRaises(AuthorizationError): e.conclude(50,3,True,D,"owner")
    def test_handover(self):
        h=ShiftHandover("H-1","out",NOW,(HandoverItem("INC-1","owner","monitorar",True),)); h.acknowledge("in",D); self.assertEqual(h.acknowledged_by,"in")
    def test_self_handover(self):
        h=ShiftHandover("H-1","out",NOW,())
        with self.assertRaises(AuthorizationError): h.acknowledge("out",D)
    def test_incomplete_item(self):
        with self.assertRaises(ValidationError): ShiftHandover("H-1","out",NOW,(HandoverItem("INC-1","owner","",True),))
