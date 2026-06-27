import unittest
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256

from regenera_risk_control.money import Money, MoneyError
from regenera_risk_control.audit import AuditChain, AuditEvent
from regenera_risk_control.kyc import KycEngine, KycProfile, KycDecision
from regenera_risk_control.sanctions import SanctionsEntry, SanctionsIndex
from regenera_risk_control.aml import AmlEngine, AmlTransaction, AmlAction
from regenera_risk_control.fraud import FraudEngine, FraudRequest, FraudAction
from regenera_risk_control.credit import CreditPolicy, CreditApplication, CreditAction
from regenera_risk_control.reconciliation import ReconciliationEngine, SettlementRecord, MatchStatus
from regenera_risk_control.accounting import AccountingBook, JournalEntry, PostingLine, Direction
from regenera_risk_control.cases import CaseManager, Case, CaseStatus
from regenera_risk_control.regulatory import RegulatoryReportService
from regenera_risk_control.controls import ControlEvaluator, Control, ControlEvidence, ControlException

H = 'a' * 64
TODAY = date(2026, 6, 26)


class MoneyTests(unittest.TestCase):
    def test_rejects_float(self):
        with self.assertRaises(MoneyError): Money(10.5)  # type: ignore[arg-type]
    def test_rejects_currency_mix(self):
        with self.assertRaises(MoneyError): Money(10, 'BRL').add(Money(10, 'USD'))
    def test_adds_integer_cents(self):
        self.assertEqual(Money(10).add(Money(20)).cents, 30)
    def test_rejects_overflow(self):
        with self.assertRaises(MoneyError): Money(9_223_372_036_854_775_808)


class AuditTests(unittest.TestCase):
    def test_chain_is_valid(self):
        chain=AuditChain(); chain.append('OPEN','a','x',{}); chain.append('CLOSE','b','x',{})
        self.assertTrue(chain.verify())
    def test_tampering_is_detected(self):
        chain=AuditChain(); chain.append('OPEN','a','x',{})
        original=chain._events[0]
        chain._events[0]=AuditEvent(original.sequence, original.event_type, original.actor,
                                    original.subject, {'changed': True}, original.previous_hash, original.event_hash)
        self.assertFalse(chain.verify())
    def test_sequence_is_monotonic(self):
        chain=AuditChain(); self.assertEqual(chain.append('A','x','y',{}).sequence,1); self.assertEqual(chain.append('B','x','y',{}).sequence,2)


class KycTests(unittest.TestCase):
    def profile(self, **changes):
        data=dict(customer_id='c1', full_name='Pessoa Teste', birth_date=date(1990,1,1),
                  document_hash=H, document_expires_at=date(2030,1,1),
                  address_verified=True, biometric_verified=True, pep=False, sanctions_hit=False)
        data.update(changes); return KycProfile(**data)
    def test_approves_complete_profile(self): self.assertEqual(KycEngine().evaluate(self.profile(),TODAY).decision,KycDecision.APPROVED)
    def test_rejects_sanctions(self): self.assertEqual(KycEngine().evaluate(self.profile(sanctions_hit=True),TODAY).decision,KycDecision.REJECTED)
    def test_pep_requires_review(self): self.assertEqual(KycEngine().evaluate(self.profile(pep=True),TODAY).decision,KycDecision.REVIEW)
    def test_expired_document_requires_review(self): self.assertIn('DOCUMENT_EXPIRED',KycEngine().evaluate(self.profile(document_expires_at=date(2020,1,1)),TODAY).reasons)
    def test_missing_biometric_requires_review(self): self.assertIn('BIOMETRIC_NOT_VERIFIED',KycEngine().evaluate(self.profile(biometric_verified=False),TODAY).reasons)


class SanctionsTests(unittest.TestCase):
    def setUp(self):
        self.doc=SanctionsIndex.hash_document('123')
        self.index=SanctionsIndex((SanctionsEntry('LIST-1','José da Silva',('J Silva',),(self.doc,)),))
    def test_normalized_name_match(self): self.assertTrue(self.index.screen('Jose da Silva').matched)
    def test_alias_match(self): self.assertTrue(self.index.screen('J Silva').matched)
    def test_document_match(self): self.assertEqual(self.index.screen('Outro','123').match_basis,('DOCUMENT',))
    def test_no_fuzzy_false_positive(self): self.assertFalse(self.index.screen('Jose Silva Santos').matched)


class AmlTests(unittest.TestCase):
    def tx(self, cents=100_000, **changes):
        data=dict(transaction_id='t1',customer_id='c1',amount=Money(cents),occurred_at=datetime(2026,6,26,tzinfo=timezone.utc),counterparty_id='p1')
        data.update(changes); return AmlTransaction(**data)
    def test_sanctions_blocks(self): self.assertEqual(AmlEngine().assess(self.tx(),(),sanctions_hit=True).action,AmlAction.BLOCK)
    def test_unavailable_is_unknown(self): self.assertEqual(AmlEngine().assess(self.tx(),(),screening_available=False).action,AmlAction.UNKNOWN)
    def test_high_value_requires_review(self): self.assertIn(AmlEngine().assess(self.tx(5_000_000),()).action,{AmlAction.REVIEW,AmlAction.BLOCK})
    def test_structuring_is_detected(self):
        now=self.tx(600_000); old=self.tx(500_000,transaction_id='t0',occurred_at=now.occurred_at-timedelta(hours=2))
        self.assertIn('POSSIBLE_STRUCTURING',AmlEngine().assess(now,(old,)).reasons)
    def test_low_risk_clears(self): self.assertEqual(AmlEngine().assess(self.tx(10_000),()).action,AmlAction.CLEAR)


class FraudTests(unittest.TestCase):
    def request(self, **changes):
        data=dict(transaction_id='t',amount=Money(10_000),trusted_device=True,beneficiary_age_days=30,attempts_10m=1,geo_anomaly=False,credential_reset_24h=False)
        data.update(changes); return FraudRequest(**data)
    def test_low_risk_approves(self): self.assertEqual(FraudEngine().assess(self.request()).action,FraudAction.APPROVE)
    def test_unavailable_is_unknown(self): self.assertEqual(FraudEngine().assess(self.request(signals_available=False)).action,FraudAction.UNKNOWN)
    def test_untrusted_device_challenges(self): self.assertEqual(FraudEngine().assess(self.request(trusted_device=False)).action,FraudAction.CHALLENGE)
    def test_combined_signals_block(self): self.assertEqual(FraudEngine().assess(self.request(trusted_device=False,geo_anomaly=True,credential_reset_24h=True)).action,FraudAction.BLOCK)
    def test_velocity_counts(self): self.assertIn('VELOCITY',FraudEngine().assess(self.request(attempts_10m=5)).reasons)


class CreditTests(unittest.TestCase):
    def app(self, **changes):
        data=dict(application_id='a',requested=Money(100_000),monthly_income=Money(500_000),monthly_debt=Money(100_000),bureau_score=700,kyc_approved=True,aml_clear=True,sanctions_hit=False)
        data.update(changes); return CreditApplication(**data)
    def test_approves_within_policy(self): self.assertEqual(CreditPolicy().decide(self.app()).action,CreditAction.APPROVE)
    def test_sanctions_declines(self): self.assertIn('SANCTIONS_HIT',CreditPolicy().decide(self.app(sanctions_hit=True)).reasons)
    def test_dti_declines(self): self.assertIn('DTI_EXCEEDED',CreditPolicy().decide(self.app(monthly_debt=Money(300_000))).reasons)
    def test_low_score_declines(self): self.assertIn('SCORE_BELOW_POLICY',CreditPolicy().decide(self.app(bureau_score=500)).reasons)
    def test_limit_can_be_reduced(self): self.assertEqual(CreditPolicy().decide(self.app(requested=Money(2_000_000))).action,CreditAction.REVIEW)


class ReconciliationTests(unittest.TestCase):
    def rec(self, ref='r', cents=100, cur='BRL'): return SettlementRecord(ref,Money(cents,cur))
    def test_match(self): self.assertEqual(ReconciliationEngine().reconcile((self.rec(),),(self.rec(),)).breaks,())
    def test_amount_break(self): self.assertEqual(ReconciliationEngine().reconcile((self.rec(),),(self.rec(cents=101),)).items[0].status,MatchStatus.AMOUNT_MISMATCH)
    def test_missing_external(self): self.assertEqual(ReconciliationEngine().reconcile((self.rec(),),()).items[0].status,MatchStatus.MISSING_EXTERNAL)
    def test_currency_break(self): self.assertEqual(ReconciliationEngine().reconcile((self.rec(),),(self.rec(cur='USD'),)).items[0].status,MatchStatus.CURRENCY_MISMATCH)
    def test_duplicate_reference_fails(self):
        with self.assertRaises(ValueError): ReconciliationEngine().reconcile((self.rec(),self.rec()),())


class AccountingTests(unittest.TestCase):
    def entry(self, eid='e1', amount=100, when=date(2026,6,26)):
        return JournalEntry(eid,when,'posting',(PostingLine('1',Direction.DEBIT,Money(amount)),PostingLine('2',Direction.CREDIT,Money(amount))))
    def test_balanced_posts(self): self.assertEqual(AccountingBook().post(self.entry()).entry_id,'e1')
    def test_unbalanced_fails(self):
        bad=JournalEntry('e',date(2026,6,26),'bad',(PostingLine('1',Direction.DEBIT,Money(100)),PostingLine('2',Direction.CREDIT,Money(99))))
        with self.assertRaises(ValueError): AccountingBook().post(bad)
    def test_duplicate_is_idempotent(self):
        book=AccountingBook(); first=book.post(self.entry()); self.assertIs(book.post(self.entry()),first)
    def test_closed_period_blocks(self):
        book=AccountingBook(); book.close_period(date(2026,6,26))
        with self.assertRaises(ValueError): book.post(self.entry())
    def test_reversal_compensates(self):
        book=AccountingBook(); book.post(self.entry()); rev=book.reverse('e1','e2',date(2026,6,27),'erro')
        self.assertEqual(rev.reversal_of,'e1'); self.assertEqual(rev.lines[0].direction,Direction.CREDIT)
    def test_second_reversal_blocks(self):
        book=AccountingBook(); book.post(self.entry()); book.reverse('e1','e2',date(2026,6,27),'erro')
        with self.assertRaises(ValueError): book.reverse('e1','e3',date(2026,6,27),'erro')


class CaseTests(unittest.TestCase):
    def test_case_requires_evidence(self):
        m=CaseManager(); m.open(Case('c','AML','open','analyst'))
        with self.assertRaises(ValueError): m.propose_close('c','analyst','CLEAR')
    def test_self_approval_blocks(self):
        m=CaseManager(); m.open(Case('c','AML','open','analyst')); m.add_evidence('c',H); m.propose_close('c','analyst','CLEAR')
        with self.assertRaises(PermissionError): m.approve_close('c','analyst')
    def test_independent_approval_closes(self):
        m=CaseManager(); m.open(Case('c','AML','open','analyst')); m.add_evidence('c',H); m.propose_close('c','analyst','CLEAR')
        self.assertEqual(m.approve_close('c','supervisor').status,CaseStatus.CLOSED)


class RegulatoryTests(unittest.TestCase):
    def test_report_requires_evidence(self):
        with self.assertRaises(ValueError): RegulatoryReportService().prepare('r','X','2026','a',{},())
    def test_self_approval_blocks(self):
        s=RegulatoryReportService(); r=s.prepare('r','X','2026','a',{},(H,))
        with self.assertRaises(PermissionError): s.approve(r,'a')
    def test_payload_change_blocks_submission(self):
        s=RegulatoryReportService(); r=s.prepare('r','X','2026','a',{'x':1},(H,)); r=s.approve(r,'b')
        with self.assertRaises(ValueError): s.submit(r,{'x':2})
    def test_approved_payload_submits(self):
        s=RegulatoryReportService(); r=s.prepare('r','X','2026','a',{'x':1},(H,)); r=s.approve(r,'b')
        self.assertTrue(s.submit(r,{'x':1}).submitted)


class ControlTests(unittest.TestCase):
    def control(self, **changes):
        data=dict(control_id='C-1',owner='Risk',blocking=True,review_due=date(2026,12,1),evidence=(ControlEvidence('e',H,TODAY),),exception=None)
        data.update(changes); return Control(**data)
    def test_effective_control_passes(self): self.assertTrue(ControlEvaluator().evaluate(self.control(),TODAY).effective)
    def test_missing_owner_fails(self): self.assertIn('OWNER_MISSING',ControlEvaluator().evaluate(self.control(owner=''),TODAY).reasons)
    def test_missing_evidence_fails(self): self.assertIn('EVIDENCE_MISSING',ControlEvaluator().evaluate(self.control(evidence=()),TODAY).reasons)
    def test_expired_review_fails(self): self.assertIn('CONTROL_REVIEW_EXPIRED',ControlEvaluator().evaluate(self.control(review_due=date(2020,1,1)),TODAY).reasons)
    def test_expired_exception_blocks(self):
        exc=ControlException('x','approver',date(2020,1,1))
        result=ControlEvaluator().evaluate(self.control(exception=exc),TODAY)
        self.assertIn('EXCEPTION_EXPIRED',result.reasons); self.assertTrue(result.blocking)


if __name__ == '__main__': unittest.main()
