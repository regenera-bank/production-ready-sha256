import unittest
from regenera_regulatory.reporting import ReportBuilder,reconcile_report
from regenera_regulatory.errors import ValidationError,ConflictError

class ReportingTests(unittest.TestCase):
    def make(self): return ReportBuilder('RPT-001','AML-BASELINE','2026-01','BRL',{'reference','amount_minor'},{'reference','amount_minor'})
    def test_invalid_currency(self):
        with self.assertRaises(ValidationError): ReportBuilder('RPT-001','AML-BASELINE','2026','brl',{'x'},{'x'})
    def test_required_must_be_allowed(self):
        with self.assertRaises(ValidationError): ReportBuilder('RPT-001','AML-BASELINE','2026','BRL',{'x'},{'y'})
    def test_row_must_be_dict(self):
        with self.assertRaises(ValidationError): self.make().add_row([])
    def test_extra_field_is_blocked(self):
        with self.assertRaises(ValidationError): self.make().add_row({'reference':'A','amount_minor':1,'secret':'x'})
    def test_missing_field_is_blocked(self):
        with self.assertRaises(ValidationError): self.make().add_row({'reference':'A'})
    def test_float_money_is_blocked(self):
        with self.assertRaises(ValidationError): self.make().add_row({'reference':'A','amount_minor':1.5})
    def test_negative_balance_is_supported(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':-100}); self.assertEqual(b.finalize(1,-100).control_amount_minor,-100)

    def test_duplicate_reference_is_blocked(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':100})
        with self.assertRaises(ConflictError): b.add_row({'reference':'A','amount_minor':200})
    def test_count_mismatch_is_blocked(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':100})
        with self.assertRaises(ValidationError): b.finalize(2,100)
    def test_amount_mismatch_is_blocked(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':100})
        with self.assertRaises(ValidationError): b.finalize(1,101)
    def test_finalize_is_deterministic(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':100}); a=b.finalize(1,100); self.assertIs(a,b.finalize(1,100))
    def test_final_report_is_immutable(self):
        b=self.make(); b.add_row({'reference':'A','amount_minor':100}); b.finalize(1,100)
        with self.assertRaises(ConflictError): b.add_row({'reference':'B','amount_minor':1})
    def test_reconciliation_matches(self): self.assertEqual(reconcile_report({'count':1,'amount_minor':1,'currency':'BRL','period':'2026'},{'count':1,'amount_minor':1,'currency':'BRL','period':'2026'}).state,'MATCHED')
    def test_reconciliation_detects_amount(self): self.assertIn('amount_minor',reconcile_report({'count':1,'amount_minor':1,'currency':'BRL','period':'2026'},{'count':1,'amount_minor':2,'currency':'BRL','period':'2026'}).differences)
    def test_reconciliation_detects_currency(self): self.assertIn('currency',reconcile_report({'count':1,'amount_minor':1,'currency':'BRL','period':'2026'},{'count':1,'amount_minor':1,'currency':'USD','period':'2026'}).differences)
    def test_reconciliation_unknown(self): self.assertEqual(reconcile_report(None,{}).state,'UNKNOWN')
