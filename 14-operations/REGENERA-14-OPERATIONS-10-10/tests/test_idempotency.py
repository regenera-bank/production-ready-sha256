import unittest
from regenera_operations.idempotency import IdempotencyRegistry,IdempotencyState
from regenera_operations.errors import ConflictError,StateTransitionError,ValidationError

class IdempotencyTests(unittest.TestCase):
    def test_begin(self): self.assertEqual(IdempotencyRegistry().begin("k",{"a":1}).state,IdempotencyState.PROCESSING)
    def test_replay_same(self):
        r=IdempotencyRegistry(); a=r.begin("k",{"a":1}); b=r.begin("k",{"a":1}); self.assertIs(a,b)
    def test_replay_diff(self):
        r=IdempotencyRegistry(); r.begin("k",{"a":1})
        with self.assertRaises(ConflictError): r.begin("k",{"a":2})
    def test_complete(self):
        r=IdempotencyRegistry(); r.begin("k",{}); self.assertEqual(r.complete("k",1).state,IdempotencyState.COMPLETED)
    def test_fail(self):
        r=IdempotencyRegistry(); r.begin("k",{}); self.assertEqual(r.fail("k").state,IdempotencyState.FAILED)
    def test_unknown(self):
        r=IdempotencyRegistry(); r.begin("k",{}); self.assertEqual(r.mark_unknown("k").state,IdempotencyState.UNKNOWN)
    def test_unknown_blocks_retry(self):
        r=IdempotencyRegistry(); r.begin("k",{}); r.mark_unknown("k")
        with self.assertRaises(StateTransitionError): r.assert_retry_allowed("k")
    def test_complete_unknown_after_reconciliation(self):
        r=IdempotencyRegistry(); r.begin("k",{}); r.mark_unknown("k"); self.assertEqual(r.complete("k",{"ok":1}).state,IdempotencyState.COMPLETED)
    def test_missing(self):
        with self.assertRaises(ValidationError): IdempotencyRegistry().complete("x",1)
    def test_long_key(self):
        with self.assertRaises(ValidationError): IdempotencyRegistry().begin("x"*129,{})
