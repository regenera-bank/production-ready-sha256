import unittest
from regenera_operations.reconciliation import ReconciliationEngine,ReconciliationRecord,ReconciliationState
from regenera_operations.money import Money
from regenera_operations.errors import ValidationError,StateTransitionError,AuthorizationError
from common import D

class ReconciliationTests(unittest.TestCase):
    def r(self,ref="1",minor=100,currency="BRL",status="SETTLED"): return ReconciliationRecord(ref,Money(minor,currency),status)
    def test_match(self): self.assertEqual(ReconciliationEngine.reconcile([self.r()],[self.r()]).state,ReconciliationState.MATCHED)
    def test_external_unavailable(self): self.assertEqual(ReconciliationEngine.reconcile([self.r()],None).state,ReconciliationState.UNKNOWN)
    def test_missing_external(self): self.assertIn("ausente-externo:1",ReconciliationEngine.reconcile([self.r()],[]).differences)
    def test_missing_internal(self): self.assertIn("ausente-interno:1",ReconciliationEngine.reconcile([],[self.r()]).differences)
    def test_amount(self): self.assertIn("valor:1",ReconciliationEngine.reconcile([self.r()],[self.r(minor=101)]).differences)
    def test_currency(self): self.assertIn("moeda:1",ReconciliationEngine.reconcile([self.r()],[self.r(currency="USD")]).differences)
    def test_status(self): self.assertIn("status:1",ReconciliationEngine.reconcile([self.r()],[self.r(status="FAILED")]).differences)
    def test_duplicate(self):
        with self.assertRaises(ValidationError): ReconciliationEngine.reconcile([self.r(),self.r()],[])
    def test_unknown_not_closed(self):
        result=ReconciliationEngine.reconcile([],None)
        with self.assertRaises(StateTransitionError): ReconciliationEngine.close(result,D,"a","b")
    def test_self_close_denied(self):
        result=ReconciliationEngine.reconcile([],[])
        with self.assertRaises(AuthorizationError): ReconciliationEngine.close(result,D,"a","a")
    def test_close(self):
        result=ReconciliationEngine.reconcile([],[]); ReconciliationEngine.close(result,D,"a","b"); self.assertEqual(result.state,ReconciliationState.CLOSED)
