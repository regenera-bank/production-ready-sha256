from dataclasses import dataclass
from hashlib import sha256

@dataclass(frozen=True, slots=True)
class Approval:
    reviewer: str
    owner: str
    artifact_digest: str
    signed_commit: bool
    expires_at_epoch: int

@dataclass(frozen=True, slots=True)
class GateInputs:
    tests_failed: int
    coverage_line: float
    coverage_branch: float
    mutation_score: float
    critical_mutants: int
    p95_ms: int
    error_rate: float
    performance_samples: int
    security_critical: int
    security_high: int
    accessibility_critical: int
    accessibility_serious: int
    resilience_recovered: bool
    reconciled: bool


def artifact_digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def evaluate_gate(inputs: GateInputs, approval: Approval, expected_digest: str, now_epoch: int) -> list[str]:
    failures: list[str] = []
    if inputs.tests_failed:
        failures.append("tests_failed")
    if inputs.coverage_line < 90:
        failures.append("line_coverage")
    if inputs.coverage_branch < 85:
        failures.append("branch_coverage")
    if inputs.mutation_score < 80:
        failures.append("mutation_score")
    if inputs.critical_mutants:
        failures.append("critical_mutants")
    if inputs.performance_samples < 20:
        failures.append("performance_samples")
    if inputs.p95_ms > 500:
        failures.append("p95_latency")
    if inputs.error_rate > 0.01:
        failures.append("error_rate")
    if inputs.security_critical or inputs.security_high:
        failures.append("security_findings")
    if inputs.accessibility_critical or inputs.accessibility_serious:
        failures.append("accessibility_findings")
    if not inputs.resilience_recovered:
        failures.append("resilience_recovery")
    if not inputs.reconciled:
        failures.append("reconciliation")
    if approval.reviewer == approval.owner:
        failures.append("self_approval")
    if approval.artifact_digest != expected_digest:
        failures.append("approval_digest_mismatch")
    if not approval.signed_commit:
        failures.append("unsigned_commit")
    if approval.expires_at_epoch <= now_epoch:
        failures.append("approval_expired")
    return failures
