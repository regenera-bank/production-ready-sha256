import unittest
from regenera_quality.mutation import MutationResult

class MutationTests(unittest.TestCase):
    def test_score(self): self.assertEqual(MutationResult(8,2).score,80)
    def test_timeout_counts_detected(self): self.assertEqual(MutationResult(7,2,1).score,80)
    def test_no_mutants(self): self.assertRaises(ValueError,lambda: MutationResult(0,0).score)
    def test_valid(self): MutationResult(9,1).validate(80)
    def test_below_minimum(self): self.assertRaises(ValueError,MutationResult(7,3).validate,80)
    def test_critical_survived(self): self.assertRaises(ValueError,MutationResult(10,0).validate,80,1)
    def test_invalid_minimum(self): self.assertRaises(ValueError,MutationResult(1,0).validate,101)
