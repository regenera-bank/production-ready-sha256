import unittest
from regenera_regulatory.evidence import EvidenceArtifact,EvidenceBundle
from regenera_regulatory.errors import ValidationError,EvidenceError,AuthorizationError,ConflictError

H='a'*64

def artifact(i='001',typ='SOURCE_APPROVAL'):
    return EvidenceArtifact(f'EVD-{i}',typ,H,'approved-source','2026-01-01T00:00:00Z','CONFIDENTIAL','2031-01-01')

class EvidenceTests(unittest.TestCase):
    def test_valid_artifact(self): self.assertEqual(artifact().sha256,H)
    def test_invalid_hash(self):
        with self.assertRaises(ValidationError): EvidenceArtifact('EVD-001','SOURCE_APPROVAL','bad','src','2026-01-01T00:00:00Z','INTERNAL','2030-01-01')

    def test_naive_collection_time_is_blocked(self):
        with self.assertRaises(ValidationError): EvidenceArtifact('EVD-001','SOURCE_APPROVAL',H,'src','2026-01-01T00:00:00','INTERNAL','2030-01-01')
    def test_invalid_classification(self):
        with self.assertRaises(ValidationError): EvidenceArtifact('EVD-001','SOURCE_APPROVAL',H,'src','2026-01-01T00:00:00Z','SECRET','2030-01-01')
    def test_empty_required_types(self):
        with self.assertRaises(ValidationError): EvidenceBundle('BND-001','USR-001',set())
    def test_add_evidence(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); self.assertEqual(b.add(artifact()).evidence_id,'EVD-001')
    def test_duplicate_identical_is_idempotent(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); a=artifact(); self.assertIs(b.add(a),b.add(a))
    def test_duplicate_different_is_blocked(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); b.add(artifact())
        with self.assertRaises(ConflictError): b.add(EvidenceArtifact('EVD-001','SOURCE_APPROVAL','b'*64,'src','2026-01-01T00:00:00Z','CONFIDENTIAL','2031-01-01'))
    def test_incomplete_bundle_cannot_freeze(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL','DATA_RECONCILIATION'}); b.add(artifact())
        with self.assertRaises(EvidenceError): b.freeze('USR-002',True,'2026-01-02T00:00:00Z')
    def test_self_approval_is_blocked(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); b.add(artifact())
        with self.assertRaises(AuthorizationError): b.freeze('USR-001',True,'2026-01-02T00:00:00Z')
    def test_mfa_is_required(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); b.add(artifact())
        with self.assertRaises(AuthorizationError): b.freeze('USR-002',False,'2026-01-02T00:00:00Z')
    def test_complete_bundle_freezes(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); b.add(artifact()); self.assertEqual(len(b.freeze('USR-002',True,'2026-01-02T00:00:00Z')),64)
    def test_frozen_bundle_is_immutable(self):
        b=EvidenceBundle('BND-001','USR-001',{'SOURCE_APPROVAL'}); b.add(artifact()); b.freeze('USR-002',True,'2026-01-02T00:00:00Z')
        with self.assertRaises(ConflictError): b.add(artifact('002'))
