import unittest
from regenera_regulatory.submissions import SubmissionRequest,SubmissionGateway
from regenera_regulatory.canonical import sha256_hex
from regenera_regulatory.errors import ValidationError,ConflictError,ExternalDependencyError

R='a'*64; E='b'*64

def request(key='IDEM-001',approval=None):
    approval=approval or sha256_hex({'report_digest':R,'evidence_digest':E,'obligation_id':'AML-BASELINE'})
    return SubmissionRequest('SUB-001','AML-BASELINE',R,E,approval,key,'CHANNEL-001')

class SubmissionTests(unittest.TestCase):
    def test_approval_must_cover_payload(self):
        with self.assertRaises(ValidationError): request(approval='c'*64)
    def test_channel_must_be_homologated(self):
        with self.assertRaises(ExternalDependencyError): SubmissionGateway({'CHANNEL-001':'BLOCKED'}).submit(request(),lambda _: {})
    def test_ack_requires_protocol(self):
        with self.assertRaises(ValidationError): SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'ACKNOWLEDGED'})
    def test_local_protocol_is_blocked(self):
        with self.assertRaises(ValidationError): SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'ACKNOWLEDGED','protocol':'LOCAL-123'})
    def test_test_protocol_is_blocked(self):
        with self.assertRaises(ValidationError): SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'ACKNOWLEDGED','protocol':'TEST-123'})
    def test_acknowledged_submission(self): self.assertEqual(SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'ACKNOWLEDGED','protocol':'EXT-2026-0001'}).state,'SUBMITTED')
    def test_rejection_requires_reason(self):
        with self.assertRaises(ValidationError): SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'REJECTED'})
    def test_rejection_is_persisted(self): self.assertEqual(SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'REJECTED','reason':'schema'}).state,'REJECTED')
    def test_timeout_becomes_unknown(self): self.assertEqual(SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'TIMEOUT'}).state,'UNKNOWN')
    def test_unavailable_becomes_unknown(self): self.assertEqual(SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'UNAVAILABLE'}).state,'UNKNOWN')
    def test_invalid_status_is_blocked(self):
        with self.assertRaises(ValidationError): SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}).submit(request(),lambda _:{'status':'OK'})
    def test_replay_does_not_call_transport_twice(self):
        calls=[]; g=SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}); r=request(); t=lambda _:(calls.append(1) or {'status':'TIMEOUT'})
        self.assertEqual(g.submit(r,t),g.submit(r,t)); self.assertEqual(len(calls),1)
    def test_key_collision_is_blocked(self):
        g=SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}); g.submit(request(),lambda _:{'status':'TIMEOUT'})
        other=SubmissionRequest('SUB-002','AML-BASELINE',R,E,sha256_hex({'report_digest':R,'evidence_digest':E,'obligation_id':'AML-BASELINE'}),'IDEM-001','CHANNEL-001')
        with self.assertRaises(ConflictError): g.submit(other,lambda _:{'status':'TIMEOUT'})
    def test_unknown_reconciles_to_submitted(self):
        g=SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}); g.submit(request(),lambda _:{'status':'TIMEOUT'})
        self.assertEqual(g.reconcile('IDEM-001',lambda _:{'status':'ACKNOWLEDGED','protocol':'EXT-2026-0002'}).state,'SUBMITTED')
    def test_unknown_reconciles_to_rejected(self):
        g=SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}); g.submit(request(),lambda _:{'status':'TIMEOUT'})
        self.assertEqual(g.reconcile('IDEM-001',lambda _:{'status':'REJECTED','reason':'duplicate'}).state,'REJECTED')
    def test_unknown_remains_when_lookup_is_ambiguous(self):
        g=SubmissionGateway({'CHANNEL-001':'ACTIVE_HOMOLOGATED'}); g.submit(request(),lambda _:{'status':'TIMEOUT'})
        self.assertEqual(g.reconcile('IDEM-001',lambda _:{'status':'UNAVAILABLE'}).state,'UNKNOWN')
