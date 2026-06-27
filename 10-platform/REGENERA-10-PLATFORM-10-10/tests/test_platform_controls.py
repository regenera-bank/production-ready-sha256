import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from regenera_platform import *
from regenera_platform.errors import PlatformControlError

NOW=datetime(2026,6,26,tzinfo=timezone.utc)
H="a"*64

class PlatformControlTests(unittest.TestCase):
    def assertCode(self, code, fn):
        with self.assertRaises(PlatformControlError) as ctx: fn()
        self.assertEqual(ctx.exception.code, code)

    def test_workload_identity_valid(self):
        WorkloadIdentity("sa:ledger","ledger-api","https://issuer",NOW+timedelta(minutes=5)).validate(NOW)
    def test_static_credential_rejected(self):
        self.assertCode("STATIC_CREDENTIAL_FORBIDDEN", lambda: WorkloadIdentity("a","b","https://i",NOW+timedelta(minutes=1),"x").validate(NOW))
    def test_expired_identity_rejected(self):
        self.assertCode("WORKLOAD_IDENTITY_EXPIRED", lambda: WorkloadIdentity("a","b","https://i",NOW).validate(NOW))
    def test_invalid_issuer_rejected(self):
        self.assertCode("WORKLOAD_IDENTITY_INVALID", lambda: WorkloadIdentity("a","b","http://i",NOW+timedelta(minutes=1)).validate(NOW))
    def test_secret_lease_valid(self):
        SecretLease("s",NOW-timedelta(days=1),NOW+timedelta(days=1),H).validate(NOW)
    def test_plaintext_secret_rejected(self):
        self.assertCode("PLAINTEXT_SECRET_FORBIDDEN", lambda: SecretLease("s",NOW,NOW+timedelta(days=1),H,"secret").validate(NOW))
    def test_stale_secret_rejected(self):
        self.assertCode("SECRET_LEASE_INVALID", lambda: SecretLease("s",NOW-timedelta(days=91),NOW+timedelta(days=1),H).validate(NOW))
    def test_missing_rotation_evidence_rejected(self):
        self.assertCode("SECRET_ROTATION_EVIDENCE_REQUIRED", lambda: SecretLease("s",NOW,NOW+timedelta(days=1),"").validate(NOW))
    def candidate(self, author="author", approver="reviewer", signed=True, approval_hash=H, image="r/x@sha256:"+H):
        return ReleaseCandidate(H,image,"abc123",author,(ReleaseApproval(approver,approval_hash,signed,NOW),),H,H)
    def test_release_valid(self): self.candidate().validate()
    def test_unsigned_release_rejected(self): self.assertCode("INDEPENDENT_SIGNED_APPROVAL_REQUIRED", lambda:self.candidate(signed=False).validate())
    def test_self_approval_rejected(self): self.assertCode("INDEPENDENT_SIGNED_APPROVAL_REQUIRED", lambda:self.candidate(approver="author").validate())
    def test_wrong_artifact_approval_rejected(self): self.assertCode("INDEPENDENT_SIGNED_APPROVAL_REQUIRED", lambda:self.candidate(approval_hash="b"*64).validate())
    def test_mutable_image_rejected(self): self.assertCode("IMAGE_DIGEST_REQUIRED", lambda:self.candidate(image="r/x:latest").validate())
    def test_exception_valid(self): ExceptionGrant("e","owner","approver",NOW+timedelta(hours=1),H).validate(NOW)
    def test_expired_exception_rejected(self): self.assertCode("EXCEPTION_EXPIRED", lambda:ExceptionGrant("e","o","a",NOW,H).validate(NOW))
    def test_exception_self_approval_rejected(self): self.assertCode("SELF_APPROVAL_FORBIDDEN", lambda:ExceptionGrant("e","o","o",NOW+timedelta(hours=1),H).validate(NOW))
    def test_public_network_rejected(self): self.assertCode("PUBLIC_NETWORK_RULE_FORBIDDEN", lambda:NetworkRule("0.0.0.0/0","db",5432).validate())
    def test_public_edge_allowed(self): NetworkRule("0.0.0.0/0","waf",443,approved_public_edge=True).validate()
    def test_mtls_required(self): self.assertCode("MTLS_REQUIRED", lambda:NetworkRule("10.0.0.0/8","db",5432,mtls_required=False).validate())
    def k8s(self, **changes):
        data=dict(image="r/x@sha256:"+H,run_as_non_root=True,read_only_root_filesystem=True,seccomp_profile="RuntimeDefault",dropped_capabilities=("ALL",),automount_service_account_token=False,cpu_request="100m",memory_request="128Mi",liveness_probe=True,readiness_probe=True)
        data.update(changes); return KubernetesBaseline(**data)
    def test_kubernetes_baseline_valid(self): self.k8s().validate()
    def test_kubernetes_root_rejected(self): self.assertCode("K8S_HARDENING_REQUIRED", lambda:self.k8s(run_as_non_root=False).validate())
    def test_kubernetes_token_automount_rejected(self): self.assertCode("K8S_TOKEN_AUTOMOUNT_FORBIDDEN", lambda:self.k8s(automount_service_account_token=True).validate())
    def test_kubernetes_latest_rejected(self): self.assertCode("K8S_IMAGE_DIGEST_REQUIRED", lambda:self.k8s(image="r/x:latest").validate())
    def test_control_effective(self): self.assertTrue(ControlEvidence("C","o","a",H,NOW-timedelta(days=1),NOW+timedelta(days=1)).effective(NOW))
    def test_control_owner_missing(self): self.assertFalse(ControlEvidence("C","","a",H,NOW-timedelta(days=1),NOW+timedelta(days=1)).effective(NOW))
    def test_control_evidence_missing(self): self.assertFalse(ControlEvidence("C","o","a","",NOW-timedelta(days=1),NOW+timedelta(days=1)).effective(NOW))
    def test_control_expired(self): self.assertFalse(ControlEvidence("C","o","a",H,NOW-timedelta(days=2),NOW).effective(NOW))
    def test_idempotent_replay(self):
        r=IdempotencyRegistry(); calls=[]
        a=r.execute("k",{"x":1},lambda:(calls.append(1) or {"id":1})); b=r.execute("k",{"x":1},lambda:{"id":2})
        self.assertEqual(a,b); self.assertEqual(len(calls),1)
    def test_idempotency_conflict(self):
        r=IdempotencyRegistry(); r.execute("k",{"x":1},lambda:1)
        self.assertCode("IDEMPOTENCY_CONFLICT", lambda:r.execute("k",{"x":2},lambda:2))

class RecoveryTests(unittest.TestCase):
    def assertCode(self, code, fn):
        with self.assertRaises(PlatformControlError) as ctx: fn()
        self.assertEqual(ctx.exception.code, code)
    def backup(self, **changes):
        data=dict(backup_id="b",created_at=NOW,payload_sha256=H,encrypted=True,immutable=True,cross_region=True); data.update(changes); return BackupRecord(**data)
    def exercise(self, **changes):
        data=dict(backup=self.backup(),restored_sha256=H,started_at=NOW,completed_at=NOW+timedelta(minutes=30),data_loss_minutes=2,financial_breaks=0); data.update(changes); return RestoreExercise(**data)
    def test_restore_valid(self): self.exercise().validate(60,5)
    def test_restore_hash_mismatch(self): self.assertCode("RESTORE_HASH_MISMATCH", lambda:self.exercise(restored_sha256="b"*64).validate(60,5))
    def test_rto_breach(self): self.assertCode("RTO_BREACHED", lambda:self.exercise(completed_at=NOW+timedelta(minutes=61)).validate(60,5))
    def test_rpo_breach(self): self.assertCode("RPO_BREACHED", lambda:self.exercise(data_loss_minutes=6).validate(60,5))
    def test_financial_break_blocks_restore(self): self.assertCode("RESTORE_FINANCIAL_BREAK", lambda:self.exercise(financial_breaks=1).validate(60,5))
    def test_unencrypted_backup_rejected(self): self.assertCode("BACKUP_PROTECTION_REQUIRED", lambda:self.exercise(backup=self.backup(encrypted=False)).validate(60,5))
    def test_failover_authorized(self): self.assertEqual(FailoverDecision("CONFIRMED_DOWN",2,True,True).decide(10),"FAILOVER_AUTHORIZED")
    def test_unknown_blocks_failover(self): self.assertEqual(FailoverDecision("UNKNOWN",0,True,True).decide(10),"BLOCKED_UNKNOWN")
    def test_lag_blocks_failover(self): self.assertEqual(FailoverDecision("CONFIRMED_DOWN",11,True,True).decide(10),"BLOCKED_NOT_READY")
    def test_reconciliation_blocks_failover(self): self.assertEqual(FailoverDecision("CONFIRMED_DOWN",2,True,False).decide(10),"BLOCKED_NOT_READY")
    def test_healthy_primary_no_failover(self): self.assertEqual(FailoverDecision("CONFIRMED_HEALTHY",0,True,True).decide(10),"NO_FAILOVER")
    def test_slo_healthy(self): self.assertEqual(SLOWindow(99.99,99.995,60).status(),"HEALTHY")
    def test_slo_breached(self): self.assertEqual(SLOWindow(99.99,99.9,60).status(),"BREACHED")

class AuditTests(unittest.TestCase):
    def test_chain_verifies(self):
        c=AuditChain(); c.append("release",{"id":1}); c.append("approve",{"id":1}); self.assertTrue(c.verify())
    def test_tampering_detected(self):
        c=AuditChain(); c.append("release",{"id":1}); r=c._records[0]; c._records[0]=type(r)(r.sequence,r.event,r.payload_hash,r.previous_hash,"0"*64); self.assertFalse(c.verify())

if __name__ == "__main__": unittest.main()
