import unittest
from dataclasses import replace
from datetime import timedelta
from regenera_operations.audit import AuditChain
from regenera_operations.access import Actor, AccessPolicy, Approval, ApprovalPolicy
from regenera_operations.errors import IntegrityError, AuthorizationError, ValidationError
from common import NOW,LATER,D,D2

class AuditAccessTests(unittest.TestCase):
    def test_chain_verifies(self):
        c=AuditChain(); c.append(NOW,"a","open",{"x":1}); c.append(LATER,"b","close",{"x":2}); self.assertTrue(c.verify())
    def test_chain_detects_tamper(self):
        c=AuditChain(); c.append(NOW,"a","open",{}); c._entries[0]=replace(c._entries[0],action="changed")
        with self.assertRaises(IntegrityError): c.verify()
    def test_naive_timestamp_rejected(self):
        from datetime import datetime
        with self.assertRaises(ValidationError): AuditChain().append(datetime.now(),"a","x",{})
    def test_actor_required(self):
        with self.assertRaises(ValidationError): AuditChain().append(NOW,"","x",{})
    def test_access_allows_role(self): AccessPolicy.authorize(Actor("a",frozenset({"ops"}),True,True),"ops",True)
    def test_inactive_denied(self):
        with self.assertRaises(AuthorizationError): AccessPolicy.authorize(Actor("a",frozenset({"ops"}),False,True),"ops")
    def test_role_denied(self):
        with self.assertRaises(AuthorizationError): AccessPolicy.authorize(Actor("a",frozenset(),True,True),"ops")
    def test_mfa_required(self):
        with self.assertRaises(AuthorizationError): AccessPolicy.authorize(Actor("a",frozenset({"ops"}),True,False),"ops",True)
    def test_approval_valid(self): ApprovalPolicy.validate(Approval("a","b",D,LATER,True),D,NOW)
    def test_autoapproval_denied(self):
        with self.assertRaises(AuthorizationError): ApprovalPolicy.validate(Approval("a","a",D,LATER,True),D,NOW)
    def test_unsigned_denied(self):
        with self.assertRaises(AuthorizationError): ApprovalPolicy.validate(Approval("a","b",D,LATER,False),D,NOW)
    def test_wrong_digest_denied(self):
        with self.assertRaises(AuthorizationError): ApprovalPolicy.validate(Approval("a","b",D,LATER,True),D2,NOW)
    def test_expired_denied(self):
        with self.assertRaises(AuthorizationError): ApprovalPolicy.validate(Approval("a","b",D,NOW,True),D,NOW)
