import unittest
from datetime import datetime, timedelta, timezone
from regenera_data_platform.access import AccessGrant, AccessPolicy, AccessError
from regenera_data_platform.streaming import StreamProcessor, StreamError, AmbiguousDelivery
from regenera_data_platform.warehouse import SCD2Table, WarehouseError


class AccessTests(unittest.TestCase):
    def setUp(self): self.now=datetime(2026,6,26,tzinfo=timezone.utc); self.policy=AccessPolicy()
    def grant(self): return AccessGrant("u","transactions",frozenset({"FRAUD"}),self.now+timedelta(hours=1),"owner")
    def test_authorized(self): self.policy.authorize(self.grant(),"transactions","FRAUD",self.now)
    def test_expired(self):
        g=AccessGrant("u","transactions",frozenset({"FRAUD"}),self.now-timedelta(seconds=1),"owner")
        with self.assertRaises(AccessError): self.policy.authorize(g,"transactions","FRAUD",self.now)
    def test_wrong_purpose(self):
        with self.assertRaises(AccessError): self.policy.authorize(self.grant(),"transactions","MARKETING",self.now)
    def test_breakglass_self_approval(self):
        with self.assertRaises(AccessError): self.policy.approve_break_glass("u",("u","v"),"T",self.now+timedelta(hours=1),self.now)
    def test_breakglass_too_long(self):
        with self.assertRaises(AccessError): self.policy.approve_break_glass("u",("a","b"),"T",self.now+timedelta(hours=5),self.now)
    def test_breakglass_valid(self): self.policy.approve_break_glass("u",("a","b"),"T",self.now+timedelta(hours=1),self.now)


class StreamingTests(unittest.TestCase):
    def test_commit_advances_offset(self):
        p=StreamProcessor(); self.assertEqual(p.process(3,"e",{"x":1},lambda x:2),2); self.assertEqual(p.offset,3)
    def test_replay_returns_result(self):
        p=StreamProcessor(); p.process(1,"e",{"x":1},lambda x:2); self.assertEqual(p.process(2,"e",{"x":1},lambda x:99),2)
    def test_payload_mismatch(self):
        p=StreamProcessor(); p.process(1,"e",{"x":1},lambda x:2)
        with self.assertRaises(StreamError): p.process(2,"e",{"x":2},lambda x:3)
    def test_unknown_blocks_retry(self):
        p=StreamProcessor()
        with self.assertRaises(AmbiguousDelivery): p.process(1,"e",{"x":1},lambda x: (_ for _ in ()).throw(AmbiguousDelivery()))
        with self.assertRaises(StreamError): p.process(2,"e",{"x":1},lambda x:2)
    def test_failed_does_not_advance_offset(self):
        p=StreamProcessor()
        with self.assertRaises(RuntimeError): p.process(1,"e",{"x":1},lambda x: (_ for _ in ()).throw(RuntimeError()))
        self.assertEqual(p.offset,-1)


class WarehouseTests(unittest.TestCase):
    def setUp(self): self.t=datetime(2026,1,1,tzinfo=timezone.utc)
    def test_insert(self): self.assertEqual(SCD2Table().upsert("1",self.t,{"name":"A"}).business_key,"1")
    def test_new_version_closes_old(self):
        s=SCD2Table(); a=s.upsert("1",self.t,{"name":"A"}); s.upsert("1",self.t+timedelta(days=1),{"name":"B"}); self.assertIsNotNone(a.valid_to)
    def test_same_value_returns_active(self):
        s=SCD2Table(); a=s.upsert("1",self.t,{"name":"A"}); self.assertIs(a,s.upsert("1",self.t+timedelta(days=1),{"name":"A"}))
    def test_retroactive_rejected(self):
        s=SCD2Table(); s.upsert("1",self.t,{"name":"A"})
        with self.assertRaises(WarehouseError): s.upsert("1",self.t,{"name":"B"})
    def test_as_of(self):
        s=SCD2Table(); s.upsert("1",self.t,{"name":"A"}); s.upsert("1",self.t+timedelta(days=2),{"name":"B"}); self.assertEqual(s.as_of("1",self.t+timedelta(days=1)).values["name"],"A")

if __name__ == '__main__': unittest.main()
