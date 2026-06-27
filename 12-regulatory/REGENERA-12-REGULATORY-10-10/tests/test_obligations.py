import unittest
from datetime import date
from regenera_regulatory.obligations import ObligationDefinition,ObligationInstance
from regenera_regulatory.errors import ValidationError,ExternalDependencyError,StateTransitionError

H='a'*64; E='b'*64

def definition(**overrides):
    data={'obligation_id':'AML-BASELINE','domain':'AML','owner_id':'USR-001','legal_source_digest':H,'due_date_confirmed':True,'layout_approved':True,'channel_homologated':True}
    data.update(overrides); return ObligationDefinition(**data)

def instance(defn=None): return ObligationInstance('OBI-001',defn or definition(),'2026-01',date(2026,2,10))

class ObligationTests(unittest.TestCase):
    def test_definition_requires_valid_source_hash(self):
        with self.assertRaises(ValidationError): definition(legal_source_digest='bad')
    def test_activation_ready(self): self.assertTrue(definition().activation_ready)
    def test_missing_source_blocks_activation(self): self.assertFalse(definition(legal_source_digest=None).activation_ready)
    def test_unconfirmed_due_date_blocks_activation(self): self.assertFalse(definition(due_date_confirmed=False).activation_ready)
    def test_unapproved_layout_blocks_activation(self): self.assertFalse(definition(layout_approved=False).activation_ready)
    def test_unhomologated_channel_blocks_activation(self): self.assertFalse(definition(channel_homologated=False).activation_ready)
    def test_bind_payload_creates_digest(self): self.assertEqual(len(instance().bind_payload(H,E)),64)
    def test_ready_requires_payload(self):
        with self.assertRaises(ValidationError): instance().mark_ready()
    def test_ready_requires_external_configuration(self):
        i=instance(definition(channel_homologated=False)); i.bind_payload(H,E)
        with self.assertRaises(ExternalDependencyError): i.mark_ready()
    def test_ready_transition(self):
        i=instance(); i.bind_payload(H,E); i.mark_ready(); self.assertEqual(i.state,'READY')
    def test_approval_must_match_payload(self):
        i=instance(); i.bind_payload(H,E); i.mark_ready()
        with self.assertRaises(ValidationError): i.approve('c'*64)
    def test_approval_transition(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); self.assertEqual(i.state,'APPROVED')
    def test_submitted_requires_protocol(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d)
        with self.assertRaises(ValidationError): i.record_submission('SUBMITTED')
    def test_local_protocol_is_blocked(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d)
        with self.assertRaises(ValidationError): i.record_submission('SUBMITTED','LOCAL-1')
    def test_unknown_submission(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('UNKNOWN'); self.assertEqual(i.state,'UNKNOWN')
    def test_unknown_reconciles_to_submitted(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('UNKNOWN'); i.reconcile('SUBMITTED','EXT-1'); self.assertEqual(i.state,'SUBMITTED')
    def test_unknown_reconciliation_requires_protocol(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('UNKNOWN')
        with self.assertRaises(ValidationError): i.reconcile('ACCEPTED')
    def test_accepted_requires_protocol(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('REJECTED')
        with self.assertRaises(ValidationError): i.mark_accepted()
    def test_submitted_can_be_accepted(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('SUBMITTED','EXT-1'); i.mark_accepted(); self.assertEqual(i.state,'ACCEPTED')
    def test_payload_cannot_change_after_ready(self):
        i=instance(); i.bind_payload(H,E); i.mark_ready()
        with self.assertRaises(StateTransitionError): i.bind_payload(H,E)
    def test_overdue_transition(self):
        i=instance(); self.assertEqual(i.evaluate_deadline(date(2026,2,11)),'OVERDUE')
    def test_accepted_does_not_become_overdue(self):
        i=instance(); d=i.bind_payload(H,E); i.mark_ready(); i.approve(d); i.record_submission('SUBMITTED','EXT-1'); i.mark_accepted(); self.assertEqual(i.evaluate_deadline(date(2026,2,11)),'ACCEPTED')
