import unittest
from datetime import timedelta
from regenera_operations.queue import OperationalQueue,TaskState
from regenera_operations.errors import ConflictError,StateTransitionError,ValidationError
from common import NOW

class QueueTests(unittest.TestCase):
    def test_submit(self): self.assertEqual(OperationalQueue().submit("k",{}).state,TaskState.READY)
    def test_duplicate_same(self):
        q=OperationalQueue(); a=q.submit("k",{"a":1}); b=q.submit("k",{"a":1}); self.assertIs(a,b)
    def test_duplicate_diff(self):
        q=OperationalQueue(); q.submit("k",{"a":1})
        with self.assertRaises(ConflictError): q.submit("k",{"a":2})
    def test_priority(self):
        q=OperationalQueue(); q.submit("b",{},20); q.submit("a",{},10); self.assertEqual(q.claim("w",NOW).key,"a")
    def test_complete(self):
        q=OperationalQueue(); q.submit("k",{}); q.claim("w",NOW); self.assertEqual(q.complete("k","w",1).state,TaskState.COMPLETED)
    def test_wrong_worker(self):
        q=OperationalQueue(); q.submit("k",{}); q.claim("w",NOW)
        with self.assertRaises(StateTransitionError): q.complete("k","x",1)
    def test_expired_lease_reclaimed(self):
        q=OperationalQueue(); q.submit("k",{}); q.claim("w",NOW,1); self.assertEqual(q.claim("x",NOW+timedelta(seconds=2)).lease_owner,"x")
    def test_retry(self):
        q=OperationalQueue(2); q.submit("k",{}); q.claim("w",NOW); self.assertEqual(q.fail("k","w").state,TaskState.READY)
    def test_dead_letter(self):
        q=OperationalQueue(2); q.submit("k",{}); q.claim("w",NOW); q.fail("k","w"); q.claim("w",NOW); self.assertEqual(q.fail("k","w").state,TaskState.DEAD_LETTER)
    def test_no_task(self): self.assertIsNone(OperationalQueue().claim("w",NOW))
    def test_invalid_attempts(self):
        with self.assertRaises(ValidationError): OperationalQueue(0)
