import unittest
from datetime import date, datetime, timedelta, timezone
from regenera_data_platform.money import Money
from regenera_data_platform.finance import FinancialRow, reconcile_financial_rows, aggregate_by_currency
from regenera_data_platform.models import ModelVersion, ModelRegistry, ModelGovernanceError
from regenera_data_platform.governance import Control, ApprovalRecord


class FinanceTests(unittest.TestCase):
    def row(self,ref,cents,currency="BRL"): return FinancialRow(ref,Money.from_cents(cents,currency))
    def test_equal_has_no_break(self): self.assertEqual(reconcile_financial_rows([self.row("1",10)],[self.row("1",10)]),[])
    def test_missing(self): self.assertEqual(reconcile_financial_rows([self.row("1",10)],[])[0].kind,"MISSING")
    def test_unexpected(self): self.assertEqual(reconcile_financial_rows([],[self.row("1",10)])[0].kind,"UNEXPECTED")
    def test_amount_break(self): self.assertEqual(reconcile_financial_rows([self.row("1",10)],[self.row("1",11)])[0].kind,"AMOUNT")
    def test_currency_break(self): self.assertEqual(reconcile_financial_rows([self.row("1",10)],[self.row("1",10,"USD")])[0].kind,"CURRENCY")
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): reconcile_financial_rows([self.row("1",10),self.row("1",10)],[])
    def test_aggregate_by_currency(self): self.assertEqual(aggregate_by_currency([self.row("1",10),self.row("2",20)])["BRL"].amount_cents,30)


class ModelTests(unittest.TestCase):
    def version(self,**kw):
        base=dict(model_id="fraud",version="1",artifact_hash="a"*64,dataset_fingerprint="b"*64,owner_group="model-risk",metric_name="recall",metric_value=.9,minimum_metric=.8,approved_by="reviewer",approved_at=datetime.now(timezone.utc)-timedelta(minutes=1))
        base.update(kw); return ModelVersion(**base)
    def test_register_and_activate(self): r=ModelRegistry(); r.register(self.version()); self.assertEqual(r.activate("fraud","1","author").version,"1")
    def test_metric_below_limit(self):
        r=ModelRegistry(); r.register(self.version(metric_value=.5))
        with self.assertRaises(ModelGovernanceError): r.activate("fraud","1","author")
    def test_self_approval_blocked(self):
        r=ModelRegistry(); r.register(self.version(approved_by="author"))
        with self.assertRaises(ModelGovernanceError): r.activate("fraud","1","author")
    def test_hash_required(self):
        r=ModelRegistry()
        with self.assertRaises(ModelGovernanceError): r.register(self.version(artifact_hash="bad"))


class GovernanceTests(unittest.TestCase):
    def test_control_effective(self): self.assertTrue(Control("C","owner",("e",),date(2026,12,1),True).effective(date(2026,6,26)))
    def test_owner_missing(self): self.assertFalse(Control("C","",("e",),date(2026,12,1),True).effective(date(2026,6,26)))
    def test_evidence_missing(self): self.assertFalse(Control("C","owner",(),date(2026,12,1),True).effective(date(2026,6,26)))
    def test_review_expired(self): self.assertFalse(Control("C","owner",("e",),date(2026,1,1),True).effective(date(2026,6,26)))
    def approval(self,**kw):
        base=dict(artifact_hash="a"*64,author="author",approver="reviewer",signature_fingerprint="F"*40,approved_at=datetime.now(timezone.utc)-timedelta(minutes=1)); base.update(kw); return ApprovalRecord(**base)
    def test_approval_valid(self): self.approval().validate()
    def test_self_approval_blocked(self):
        with self.assertRaises(ValueError): self.approval(approver="author").validate()
    def test_signature_required(self):
        with self.assertRaises(ValueError): self.approval(signature_fingerprint="").validate()

if __name__ == '__main__': unittest.main()
