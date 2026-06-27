import unittest
from dataclasses import replace
from regenera_quality.gates import Approval, GateInputs, artifact_digest, evaluate_gate

class GateTests(unittest.TestCase):
    def inputs(self): return GateInputs(0,95,90,90,0,200,.001,100,0,0,0,0,True,True)
    def approval(self,digest): return Approval("reviewer","owner",digest,True,200)
    def test_digest(self): self.assertEqual(len(artifact_digest(b"x")),64)
    def test_approved(self):
        d=artifact_digest(b"x"); self.assertEqual(evaluate_gate(self.inputs(),self.approval(d),d,100),[])
    def check(self, field, value, expected):
        d=artifact_digest(b"x"); failures=evaluate_gate(replace(self.inputs(),**{field:value}),self.approval(d),d,100); self.assertIn(expected,failures)
    def test_tests(self): self.check("tests_failed",1,"tests_failed")
    def test_line(self): self.check("coverage_line",89.9,"line_coverage")
    def test_branch(self): self.check("coverage_branch",84.9,"branch_coverage")
    def test_mutation(self): self.check("mutation_score",79.9,"mutation_score")
    def test_critical_mutant(self): self.check("critical_mutants",1,"critical_mutants")
    def test_samples(self): self.check("performance_samples",19,"performance_samples")
    def test_latency(self): self.check("p95_ms",501,"p95_latency")
    def test_error_rate(self): self.check("error_rate",.011,"error_rate")
    def test_security_critical(self): self.check("security_critical",1,"security_findings")
    def test_security_high(self): self.check("security_high",1,"security_findings")
    def test_accessibility_critical(self): self.check("accessibility_critical",1,"accessibility_findings")
    def test_accessibility_serious(self): self.check("accessibility_serious",1,"accessibility_findings")
    def test_recovery(self): self.check("resilience_recovered",False,"resilience_recovery")
    def test_reconciliation(self): self.check("reconciled",False,"reconciliation")
    def test_self_approval(self):
        d=artifact_digest(b"x"); a=replace(self.approval(d),reviewer="owner"); self.assertIn("self_approval",evaluate_gate(self.inputs(),a,d,100))
    def test_digest_mismatch(self):
        d=artifact_digest(b"x"); self.assertIn("approval_digest_mismatch",evaluate_gate(self.inputs(),self.approval("0"*64),d,100))
    def test_unsigned(self):
        d=artifact_digest(b"x"); self.assertIn("unsigned_commit",evaluate_gate(self.inputs(),replace(self.approval(d),signed_commit=False),d,100))
    def test_expired(self):
        d=artifact_digest(b"x"); self.assertIn("approval_expired",evaluate_gate(self.inputs(),self.approval(d),d,200))
