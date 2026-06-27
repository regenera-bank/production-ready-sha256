from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
import hashlib
import unittest

from regenera_security.audit import AuditChain
from regenera_security.identity import AccessController, Principal
from regenera_security.secrets import SecretMetadata, KeyMetadata
from regenera_security.appsec import (
    Vulnerability, RiskWaiver, ScanResult, ReleaseApproval, ReleaseCandidate
)
from regenera_security.detection import DetectionEngine, DetectionRule, SecurityEvent
from regenera_security.incident import Incident
from regenera_security.governance import ControlAssessment, SecurityException
from regenera_security.errors import (
    AuthorizationDenied, IntegrityViolation, InvalidTransition, ReleaseBlocked, SecurityControlError
)

UTC=timezone.utc
NOW=datetime(2026,6,26,12,0,tzinfo=UTC)
TODAY=date(2026,6,26)
DIGEST="a"*64


class AuditChainTests(unittest.TestCase):
    def test_empty_chain_is_valid(self):
        self.assertTrue(AuditChain().verify())

    def test_append_creates_sequence(self):
        chain=AuditChain(); one=chain.append("login","user-1",{"result":"ok"},NOW); two=chain.append("grant","user-1",{"role":"ops"},NOW)
        self.assertEqual((one.sequence,two.sequence),(1,2))

    def test_hashes_are_chained(self):
        chain=AuditChain(); one=chain.append("a","u",{},NOW); two=chain.append("b","u",{},NOW)
        self.assertEqual(two.previous_hash,one.entry_hash)

    def test_payload_order_is_canonical(self):
        a=AuditChain().append("event","u",{"a":1,"b":2},NOW)
        b=AuditChain().append("event","u",{"b":2,"a":1},NOW)
        self.assertEqual(a.payload_digest,b.payload_digest)

    def test_payload_change_changes_digest(self):
        a=AuditChain().append("event","u",{"a":1},NOW)
        b=AuditChain().append("event","u",{"a":2},NOW)
        self.assertNotEqual(a.payload_digest,b.payload_digest)

    def test_missing_subject_is_rejected(self):
        with self.assertRaises(IntegrityViolation): AuditChain().append("event","",{},NOW)

    def test_naive_datetime_is_rejected(self):
        with self.assertRaises(IntegrityViolation): AuditChain().append("event","u",{},datetime(2026,1,1))

    def test_tampering_is_detected(self):
        chain=AuditChain(); chain.append("event","u",{"a":1},NOW)
        chain._entries[0]=replace(chain._entries[0],payload_digest="0"*64)
        self.assertFalse(chain.verify())
        with self.assertRaises(IntegrityViolation): chain.assert_valid()


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.ctrl=AccessController({"read":{"reader","admin"},"admin":{"admin"}},{"admin"})
        self.admin=Principal("alice",frozenset({"admin"}),True,True,NOW-timedelta(minutes=5))

    def test_allowed_role(self):
        self.ctrl.authorize(Principal("r",frozenset({"reader"})),"read",now=NOW)

    def test_inactive_identity_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(Principal("r",frozenset({"reader"}),False),"read",now=NOW)

    def test_unknown_action_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(self.admin,"delete-all",now=NOW)

    def test_insufficient_role_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(Principal("r",frozenset({"reader"})),"admin",now=NOW)

    def test_mfa_required_for_privileged_action(self):
        p=Principal("a",frozenset({"admin"}),True,False,NOW)
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(p,"admin",now=NOW)

    def test_strong_session_required(self):
        p=Principal("a",frozenset({"admin"}),True,True,None)
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(p,"admin",now=NOW)

    def test_stale_session_is_denied(self):
        p=Principal("a",frozenset({"admin"}),True,True,NOW-timedelta(minutes=16))
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(p,"admin",now=NOW)

    def test_future_session_is_denied(self):
        p=Principal("a",frozenset({"admin"}),True,True,NOW+timedelta(minutes=1))
        with self.assertRaises(AuthorizationDenied): self.ctrl.authorize(p,"admin",now=NOW)

    def test_jit_grant_is_issued(self):
        grant=self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","CHG-1","bob",30,now=NOW)
        self.assertTrue(grant.is_valid(NOW+timedelta(minutes=10)))

    def test_jit_grant_expires(self):
        grant=self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","CHG-1","bob",30,now=NOW)
        self.assertFalse(grant.is_valid(NOW+timedelta(minutes=30)))

    def test_self_approval_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","CHG-1","alice",30,now=NOW)

    def test_missing_ticket_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","","bob",30,now=NOW)

    def test_zero_duration_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","CHG-1","bob",0,now=NOW)

    def test_duration_above_limit_is_denied(self):
        with self.assertRaises(AuthorizationDenied): self.ctrl.issue_jit_grant(self.admin,"admin","db/prod","CHG-1","bob",61,now=NOW)


class SecretAndKeyTests(unittest.TestCase):
    def secret(self, **changes):
        data=dict(name="db-password",owner="security",storage_ref="vault://prod/db",created_at=NOW-timedelta(days=30),last_rotated_at=NOW-timedelta(days=5),rotation_days=30,evidence_id="ROT-1",expires_at=NOW+timedelta(days=20))
        data.update(changes); return SecretMetadata(**data)

    def key(self, **changes):
        data=dict(key_id="key-1",owner="security",location="hsm://cluster/key-1",usages=frozenset({"SIGN","VERIFY"}),state="ACTIVE",created_at=NOW-timedelta(days=100),expires_at=NOW+timedelta(days=100),rotation_evidence="CEREMONY-1")
        data.update(changes); return KeyMetadata(**data)

    def test_valid_secret_metadata(self): self.secret().validate(NOW)
    def test_secret_requires_owner(self):
        with self.assertRaises(SecurityControlError): self.secret(owner="").validate(NOW)
    def test_secret_requires_approved_vault(self):
        with self.assertRaises(SecurityControlError): self.secret(storage_ref="file:///tmp/secret").validate(NOW)
    def test_rotation_window_must_be_positive(self):
        with self.assertRaises(SecurityControlError): self.secret(rotation_days=0).validate(NOW)
    def test_rotation_evidence_required(self):
        with self.assertRaises(SecurityControlError): self.secret(evidence_id="").validate(NOW)
    def test_rotation_cannot_precede_creation(self):
        with self.assertRaises(SecurityControlError): self.secret(last_rotated_at=NOW-timedelta(days=31)).validate(NOW)
    def test_stale_rotation_is_denied(self):
        with self.assertRaises(SecurityControlError):
            self.secret(created_at=NOW-timedelta(days=100),last_rotated_at=NOW-timedelta(days=31)).validate(NOW)
    def test_expired_secret_is_denied(self):
        with self.assertRaises(SecurityControlError): self.secret(expires_at=NOW).validate(NOW)
    def test_valid_key_metadata(self): self.key().validate(NOW,"SIGN")
    def test_inactive_key_is_denied(self):
        with self.assertRaises(SecurityControlError): self.key(state="SUSPENDED").validate(NOW)
    def test_key_outside_hsm_or_kms_is_denied(self):
        with self.assertRaises(SecurityControlError): self.key(location="file://key").validate(NOW)
    def test_expired_key_is_denied(self):
        with self.assertRaises(SecurityControlError): self.key(expires_at=NOW).validate(NOW)
    def test_invalid_usage_is_denied(self):
        with self.assertRaises(SecurityControlError): self.key(usages=frozenset({"EXPORT"})).validate(NOW)
    def test_required_usage_is_enforced(self):
        with self.assertRaises(SecurityControlError): self.key().validate(NOW,"DECRYPT")


class AppSecTests(unittest.TestCase):
    def vulnerability(self, **changes):
        data=dict(vulnerability_id="CVE-1",severity="HIGH",discovered_on=TODAY-timedelta(days=2),status="OPEN")
        data.update(changes); return Vulnerability(**data)

    def candidate(self, **changes):
        approval=ReleaseApproval("reviewer","builder",DIGEST,"CHG-1")
        data=dict(artifact_digest=DIGEST,commit_digest="b"*64,sbom_digest="c"*64,provenance_digest="d"*64,scans=(ScanResult("sast","PASS"),ScanResult("secrets","PASS")),vulnerabilities=(),requester_id="builder",approval=approval,commit_signed=True,external_signature_present=False)
        data.update(changes); return ReleaseCandidate(**data)

    def test_vulnerability_due_date(self): self.assertEqual(self.vulnerability().due_on(),TODAY+timedelta(days=5))
    def test_invalid_severity_is_rejected(self):
        with self.assertRaises(SecurityControlError): self.vulnerability(severity="URGENT").due_on()
    def test_fixed_vulnerability_is_not_overdue(self): self.assertFalse(self.vulnerability(discovered_on=TODAY-timedelta(days=100),status="FIXED").is_overdue(TODAY))
    def test_open_critical_becomes_overdue(self): self.assertTrue(self.vulnerability(severity="CRITICAL",discovered_on=TODAY-timedelta(days=2)).is_overdue(TODAY))
    def test_valid_waiver(self): RiskWaiver("W-1","a","b",TODAY+timedelta(days=1),"WAF rule","exposure accepted").validate(TODAY)
    def test_self_approved_waiver_is_rejected(self):
        with self.assertRaises(SecurityControlError): RiskWaiver("W-1","a","a",TODAY+timedelta(days=1),"WAF","risk").validate(TODAY)
    def test_expired_waiver_is_rejected(self):
        with self.assertRaises(SecurityControlError): RiskWaiver("W-1","a","b",TODAY,"WAF","risk").validate(TODAY)
    def test_waiver_requires_compensation(self):
        with self.assertRaises(SecurityControlError): RiskWaiver("W-1","a","b",TODAY+timedelta(days=1),"","risk").validate(TODAY)
    def test_scan_must_pass(self):
        with self.assertRaises(ReleaseBlocked): ScanResult("sast","FAIL").validate()
    def test_critical_finding_blocks(self):
        with self.assertRaises(ReleaseBlocked): ScanResult("sast","PASS",1,0).validate()
    def test_negative_finding_count_is_rejected(self):
        with self.assertRaises(ReleaseBlocked): ScanResult("sast","PASS",-1,0).validate()
    def test_technical_gate_passes(self): self.candidate().validate_technical_gate(TODAY)
    def test_invalid_digest_blocks(self):
        with self.assertRaises(ReleaseBlocked): self.candidate(artifact_digest="latest").validate_technical_gate(TODAY)
    def test_missing_scans_blocks(self):
        with self.assertRaises(ReleaseBlocked): self.candidate(scans=()).validate_technical_gate(TODAY)
    def test_unsigned_commit_blocks(self):
        with self.assertRaises(ReleaseBlocked): self.candidate(commit_signed=False).validate_technical_gate(TODAY)
    def test_missing_approval_blocks(self):
        with self.assertRaises(ReleaseBlocked): self.candidate(approval=None).validate_technical_gate(TODAY)
    def test_self_approval_blocks(self):
        approval=ReleaseApproval("builder","builder",DIGEST,"CHG-1")
        with self.assertRaises(ReleaseBlocked): self.candidate(approval=approval).validate_technical_gate(TODAY)
    def test_approval_for_other_digest_blocks(self):
        approval=ReleaseApproval("reviewer","builder","e"*64,"CHG-1")
        with self.assertRaises(ReleaseBlocked): self.candidate(approval=approval).validate_technical_gate(TODAY)
    def test_overdue_vulnerability_blocks(self):
        vuln=self.vulnerability(severity="CRITICAL",discovered_on=TODAY-timedelta(days=3))
        with self.assertRaises(ReleaseBlocked): self.candidate(vulnerabilities=(vuln,)).validate_technical_gate(TODAY)
    def test_valid_waiver_allows_overdue_vulnerability(self):
        vuln=self.vulnerability(severity="CRITICAL",discovered_on=TODAY-timedelta(days=3))
        waiver=RiskWaiver("W-1","builder","risk",TODAY+timedelta(days=1),"isolation","temporary exposure")
        self.candidate(vulnerabilities=(vuln,)).validate_technical_gate(TODAY,{"CVE-1":waiver})
    def test_unsigned_external_state_is_explicit(self): self.assertEqual(self.candidate().institutional_state(),"UNSIGNED_PENDING_EXTERNAL_APPROVAL")
    def test_signed_external_state_is_explicit(self): self.assertEqual(self.candidate(external_signature_present=True).institutional_state(),"APPROVED_SIGNED")


class DetectionTests(unittest.TestCase):
    def setUp(self):
        self.engine=DetectionEngine((DetectionRule("R-1","denied", "HIGH",2,5),DetectionRule("R-2","signature_invalid","CRITICAL",1,5)))
    def event(self, event_id="e1", event_type="denied", principal="u", at=NOW, payload=None):
        return SecurityEvent(event_id,event_type,principal,at,payload or {"action":"login","password":"must-not-log"})

    def test_first_event_below_threshold_does_not_alert(self): self.assertEqual(self.engine.ingest(self.event(),NOW),())
    def test_threshold_raises_alert(self):
        self.engine.ingest(self.event("e1"),NOW); alerts=self.engine.ingest(self.event("e2"),NOW)
        self.assertEqual(len(alerts),1)
    def test_alert_is_deduplicated(self):
        self.engine.ingest(self.event("e1"),NOW); self.engine.ingest(self.event("e2"),NOW); self.engine.ingest(self.event("e3"),NOW)
        self.assertEqual(len(self.engine.alerts),1)
        self.assertEqual(self.engine.alerts[0].count,3)
    def test_different_principal_has_different_alert(self):
        self.engine.ingest(self.event("e1",principal="u1"),NOW); self.engine.ingest(self.event("e2",principal="u1"),NOW)
        self.engine.ingest(self.event("e3",principal="u2"),NOW); self.engine.ingest(self.event("e4",principal="u2"),NOW)
        self.assertEqual(len(self.engine.alerts),2)
    def test_critical_rule_alerts_on_first_event(self): self.assertEqual(len(self.engine.ingest(self.event(event_type="signature_invalid"),NOW)),1)
    def test_sensitive_payload_field_is_removed(self):
        self.engine.ingest(self.event(),NOW)
        self.assertEqual(self.engine._events[0].payload,{"action":"login"})
    def test_identical_event_replay_is_idempotent(self):
        self.engine.ingest(self.event("same"),NOW)
        self.assertEqual(self.engine.ingest(self.event("same"),NOW),())
        self.assertEqual(len(self.engine._events),1)
    def test_event_id_collision_is_rejected(self):
        self.engine.ingest(self.event("same",payload={"action":"login"}),NOW)
        with self.assertRaises(SecurityControlError):
            self.engine.ingest(self.event("same",payload={"action":"delete"}),NOW)
    def test_empty_event_id_is_rejected(self):
        with self.assertRaises(SecurityControlError): self.engine.ingest(self.event(""),NOW)
    def test_telemetry_unavailable_becomes_unknown(self):
        self.engine.set_telemetry_state("UNAVAILABLE")
        with self.assertRaisesRegex(SecurityControlError,"UNKNOWN"): self.engine.ingest(self.event(),NOW)
    def test_degraded_telemetry_still_processes(self):
        self.engine.set_telemetry_state("DEGRADED"); self.engine.ingest(self.event(),NOW)
    def test_invalid_telemetry_state_is_rejected(self):
        with self.assertRaises(SecurityControlError): self.engine.set_telemetry_state("OK")
    def test_naive_event_time_is_rejected(self):
        with self.assertRaises(SecurityControlError): self.engine.ingest(self.event(at=datetime(2026,1,1)),NOW)
    def test_future_event_is_rejected(self):
        with self.assertRaises(SecurityControlError): self.engine.ingest(self.event(at=NOW+timedelta(minutes=2)),NOW)
    def test_old_event_outside_window_does_not_count(self):
        self.engine.ingest(self.event("old",at=NOW-timedelta(minutes=10)),NOW); alerts=self.engine.ingest(self.event("new",at=NOW),NOW)
        self.assertEqual(alerts,())


class IncidentTests(unittest.TestCase):
    def test_invalid_severity_is_rejected(self):
        with self.assertRaises(SecurityControlError): Incident.declare("I-1","owner","CRITICAL",now=NOW)
    def test_missing_owner_is_rejected(self):
        with self.assertRaises(SecurityControlError): Incident.declare("I-1","","SEV1",now=NOW)
    def test_declaration_state(self): self.assertEqual(Incident.declare("I-1","owner","SEV1",now=NOW).state,"DECLARED")
    def test_duplicate_evidence_is_idempotent(self):
        i=Incident.declare("I-1","owner","SEV1",now=NOW).add_evidence("E-1").add_evidence("E-1")
        self.assertEqual(i.evidence_ids,("E-1",))
    def test_empty_evidence_is_rejected(self):
        with self.assertRaises(SecurityControlError): Incident.declare("I-1","owner","SEV1",now=NOW).add_evidence("")
    def test_invalid_jump_is_rejected(self):
        with self.assertRaises(InvalidTransition): Incident.declare("I-1","owner","SEV1",now=NOW).transition("CONTAINED",containment="blocked")
    def test_containment_is_required(self):
        i=Incident.declare("I-1","owner","SEV1",now=NOW).transition("TRIAGED")
        with self.assertRaises(InvalidTransition): i.transition("CONTAINED")
    def test_root_cause_is_required(self):
        i=Incident.declare("I-1","owner","SEV1",now=NOW).transition("TRIAGED").transition("CONTAINED",containment="isolated")
        with self.assertRaises(InvalidTransition): i.transition("ERADICATED")
    def test_recovery_validation_is_required(self):
        i=Incident.declare("I-1","owner","SEV1",now=NOW).transition("TRIAGED").transition("CONTAINED",containment="isolated").transition("ERADICATED",root_cause="credential")
        with self.assertRaises(InvalidTransition): i.transition("RECOVERED")
    def recovered(self):
        return Incident.declare("I-1","owner","SEV1",now=NOW).add_evidence("E-1").transition("TRIAGED").transition("CONTAINED",containment="isolated").transition("ERADICATED",root_cause="credential").transition("RECOVERED",recovery_validation="reconciled")
    def test_self_closure_is_rejected(self):
        with self.assertRaises(InvalidTransition): self.recovered().transition("CLOSED",closure_approver_id="owner")
    def test_closure_requires_evidence(self):
        i=Incident.declare("I-1","owner","SEV1",now=NOW).transition("TRIAGED").transition("CONTAINED",containment="isolated").transition("ERADICATED",root_cause="credential").transition("RECOVERED",recovery_validation="ok")
        with self.assertRaises(InvalidTransition): i.transition("CLOSED",closure_approver_id="reviewer")
    def test_independent_closure_passes(self): self.assertEqual(self.recovered().transition("CLOSED",closure_approver_id="reviewer").state,"CLOSED")
    def test_closed_incident_cannot_reopen(self):
        closed=self.recovered().transition("CLOSED",closure_approver_id="reviewer")
        with self.assertRaises(InvalidTransition): closed.transition("TRIAGED")


class GovernanceTests(unittest.TestCase):
    def test_effective_control(self):
        c=ControlAssessment("C-1","owner","E-1",TODAY-timedelta(days=1),TODAY+timedelta(days=1),"EFFECTIVE")
        self.assertTrue(c.effective(TODAY))
    def test_control_without_owner_is_ineffective(self):
        c=ControlAssessment("C-1","","E-1",TODAY-timedelta(days=1),TODAY+timedelta(days=1),"EFFECTIVE")
        self.assertFalse(c.effective(TODAY))
    def test_control_without_evidence_is_ineffective(self):
        c=ControlAssessment("C-1","owner","",TODAY-timedelta(days=1),TODAY+timedelta(days=1),"EFFECTIVE")
        self.assertFalse(c.effective(TODAY))
    def test_expired_review_is_ineffective(self):
        c=ControlAssessment("C-1","owner","E-1",TODAY-timedelta(days=2),TODAY,"EFFECTIVE")
        self.assertFalse(c.effective(TODAY))
    def test_failed_result_is_ineffective(self):
        c=ControlAssessment("C-1","owner","E-1",TODAY-timedelta(days=1),TODAY+timedelta(days=1),"INEFFECTIVE")
        self.assertFalse(c.effective(TODAY))
    def test_valid_exception(self):
        SecurityException("X-1","requester","approver","owner",TODAY+timedelta(days=1),"risk","network isolation").validate(TODAY)
    def test_expired_exception_is_rejected(self):
        with self.assertRaises(SecurityControlError): SecurityException("X-1","requester","approver","owner",TODAY,"risk","control").validate(TODAY)
    def test_self_approved_exception_is_rejected(self):
        with self.assertRaises(SecurityControlError): SecurityException("X-1","requester","requester","owner",TODAY+timedelta(days=1),"risk","control").validate(TODAY)
    def test_incomplete_exception_is_rejected(self):
        with self.assertRaises(SecurityControlError): SecurityException("X-1","requester","approver","",TODAY+timedelta(days=1),"risk","control").validate(TODAY)


if __name__ == "__main__":
    unittest.main()
