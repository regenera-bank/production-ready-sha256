import unittest
from regenera_quality.performance import percentile, evaluate

class PerformanceTests(unittest.TestCase):
    def test_empty_rejected(self): self.assertRaises(ValueError, percentile, [], .95)
    def test_invalid_percentile(self): self.assertRaises(ValueError, percentile, [1], 0)
    def test_p95_single(self): self.assertEqual(percentile([10],.95),10)
    def test_p95_order_independent(self): self.assertEqual(percentile([30,10,20,40],.5),20)
    def test_evaluate(self):
        r=evaluate(list(range(1,101)),1); self.assertEqual(r.p95_ms,95); self.assertEqual(r.error_rate,.01)
    def test_invalid_failures_negative(self): self.assertRaises(ValueError,evaluate,[1],-1)
    def test_invalid_failures_above_samples(self): self.assertRaises(ValueError,evaluate,[1],2)
    def test_negative_latency(self): self.assertRaises(ValueError,evaluate,[-1],0)
