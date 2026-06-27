from __future__ import annotations
import csv, importlib.util, json, subprocess, sys, tempfile, unittest, zipfile
from datetime import date, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference-models'))
from financial_model import Ledger, Entry, Line, FinancialError, CurrencyMismatch, ImmutableEntry, IdempotencyStore, UnknownStateError
from governance_model import Approval, ExceptionRecord, ControlEvidence, GovernanceError, validate_approval, validate_exception, evaluate_control
from continuity_model import restore_exercise
spec=importlib.util.spec_from_file_location('gov',ROOT/'scripts'/'governance.py'); gov=importlib.util.module_from_spec(spec); spec.loader.exec_module(gov)

class ReleaseIntegrityTests(unittest.TestCase):
    def test_tree_has_no_system_artifacts(self):
        errors,_=gov.validate_root(ROOT)
        self.assertFalse([e for e in errors if e.startswith('system-artifact:')],errors)
    def test_validator_passes(self): self.assertEqual([],gov.validate_root(ROOT)[0])
    def test_security_passes(self): self.assertEqual(0,gov.security())
    def test_control_matrix_has_depth(self):
        with (ROOT/'CONTROL-MATRIX.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows),30); self.assertEqual(len(rows),len({r['control_id'] for r in rows}))
        self.assertTrue(all(r['expected_evidence'].strip() for r in rows))
    def test_build_and_verify_extracted_release(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td); self.assertEqual(0,gov.build(out)); self.assertEqual(0,gov.verify_release(out))
    def test_zip_has_no_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td); gov.build(out)
            with zipfile.ZipFile(out/'regenera-governance-payload.zip') as z: names=z.namelist()
            self.assertFalse(any('.DS_Store' in n or '__MACOSX' in n or '__pycache__' in n or n.endswith('.pyc') for n in names))

class GovernanceBehaviorTests(unittest.TestCase):
    def test_release_without_signature_fails(self):
        with self.assertRaises(GovernanceError): validate_approval(Approval('Don Paulo Ricardo','Independent Reviewer',False))
    def test_self_approval_fails(self):
        with self.assertRaises(GovernanceError): validate_approval(Approval('Don Paulo Ricardo','Don Paulo Ricardo',True))
    def test_independent_signed_approval_passes(self): validate_approval(Approval('Don Paulo Ricardo','Independent Reviewer',True))
    def test_expired_exception_blocks(self):
        rec=ExceptionRecord('SEC-001','requester','approver',date.today()-timedelta(days=1),'segmentation')
        with self.assertRaises(GovernanceError): validate_exception(rec,date.today())
    def test_self_approved_exception_blocks(self):
        rec=ExceptionRecord('SEC-001','same','same',date.today()+timedelta(days=1),'segmentation')
        with self.assertRaises(GovernanceError): validate_exception(rec,date.today())
    def test_missing_evidence_is_ineffective(self):
        status=evaluate_control(ControlEvidence('SEC-001','security-governance',tuple()),{'security-governance'},date.today())
        self.assertEqual('INEFFECTIVE_EVIDENCE_MISSING',status)
    def test_unknown_owner_is_ineffective(self):
        status=evaluate_control(ControlEvidence('SEC-001','ghost',('evidence.json',)),{'security-governance'},date.today())
        self.assertEqual('INEFFECTIVE_OWNER_MISSING',status)
    def test_expired_control_is_ineffective(self):
        status=evaluate_control(ControlEvidence('SEC-001','security-governance',('evidence.json',),date.today()-timedelta(days=1)),{'security-governance'},date.today())
        self.assertEqual('INEFFECTIVE_EXPIRED',status)

class LedgerRiskTests(unittest.TestCase):
    def setUp(self): self.ledger=Ledger()
    def balanced(self,entry_id='e1'):
        return Entry(entry_id,(Line('cash','DEBIT',100),Line('payable','CREDIT',100)))
    def test_unbalanced_posting_fails(self):
        with self.assertRaises(FinancialError): self.ledger.post(Entry('e1',(Line('a','DEBIT',100),Line('b','CREDIT',99))))
    def test_balanced_sum_closes_zero(self): self.assertEqual('e1',self.ledger.post(self.balanced()).entry_id)
    def test_currency_mismatch_fails(self):
        with self.assertRaises(CurrencyMismatch): self.ledger.post(Entry('e1',(Line('a','DEBIT',100,'BRL'),Line('b','CREDIT',100,'USD'))))
    def test_posted_entry_is_immutable(self):
        self.ledger.post(self.balanced())
        with self.assertRaises(ImmutableEntry): self.ledger.mutate('e1',self.balanced('x'))
    def test_reversal_is_compensating(self):
        self.ledger.post(self.balanced()); rev=self.ledger.reverse('e1','r1')
        self.assertEqual('e1',rev.reversal_of); self.assertEqual('CREDIT',rev.lines[0].direction); self.assertIn('e1',self.ledger._entries)
    def test_duplicate_returns_original(self):
        first=self.ledger.post(self.balanced()); second=self.ledger.post(self.balanced()); self.assertIs(first,second)
    def test_unknown_state_blocks_blind_retry(self):
        store=IdempotencyStore(); store.begin('k','f'); store.mark_unknown('k')
        with self.assertRaises(UnknownStateError): store.begin('k','f')
    def test_completed_duplicate_returns_result(self):
        store=IdempotencyStore(); store.begin('k','f'); store.complete('k',{'id':'1'}); self.assertEqual({'id':'1'},store.begin('k','f')['result'])

class ContinuityTests(unittest.TestCase):
    def test_real_local_restore_matches_hash(self):
        result=restore_exercise(b'ledger-proof\n'*1000); self.assertTrue(result['integrity_match']); self.assertEqual(0,result['financial_breaks']); self.assertEqual(0,result['duplicate_effects'])
    def test_restore_reports_measured_time(self): self.assertGreaterEqual(restore_exercise(b'x')['observed_rto_ms'],0)

if __name__=='__main__': unittest.main(verbosity=2)
