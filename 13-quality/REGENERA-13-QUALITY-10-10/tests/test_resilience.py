import unittest
from regenera_quality.resilience import CircuitBreaker, State, Experiment

class ResilienceTests(unittest.TestCase):
    def test_invalid_threshold(self): self.assertRaises(ValueError,CircuitBreaker,0)
    def test_closed_allows(self): self.assertTrue(CircuitBreaker().allow())
    def test_opens(self):
        c=CircuitBreaker(2); c.failure(); c.failure(); self.assertEqual(c.state,State.OPEN); self.assertFalse(c.allow())
    def test_success_resets(self):
        c=CircuitBreaker(1); c.failure(); c.probe(); c.success(); self.assertEqual(c.state,State.CLOSED)
    def test_probe_requires_open(self): self.assertRaises(ValueError,CircuitBreaker().probe)
    def exp(self, **kw):
        data=dict(name="broker-loss",owner="ops",environment="staging",abort_condition="error_rate>1%",reconciliation_required=True,approved_by="risk")
        data.update(kw); return Experiment(**data)
    def test_experiment_valid(self): self.exp().validate()
    def test_production_blocked(self): self.assertRaises(ValueError,self.exp(environment="production").validate)
    def test_self_approval_blocked(self): self.assertRaises(ValueError,self.exp(approved_by="ops").validate)
    def test_reconciliation_required(self): self.assertRaises(ValueError,self.exp(reconciliation_required=False).validate)
    def test_evidence_required(self): self.assertRaises(ValueError,self.exp(abort_condition="").validate)
