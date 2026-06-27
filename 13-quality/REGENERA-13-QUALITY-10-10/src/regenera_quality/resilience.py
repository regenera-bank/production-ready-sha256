from dataclasses import dataclass
from enum import Enum

class State(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, threshold: int = 3) -> None:
        if threshold < 1:
            raise ValueError("invalid_threshold")
        self.threshold = threshold
        self.failures = 0
        self.state = State.CLOSED

    def allow(self) -> bool:
        return self.state != State.OPEN

    def success(self) -> None:
        self.failures = 0
        self.state = State.CLOSED

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.state = State.OPEN

    def probe(self) -> None:
        if self.state != State.OPEN:
            raise ValueError("probe_requires_open_state")
        self.state = State.HALF_OPEN

@dataclass(frozen=True, slots=True)
class Experiment:
    name: str
    owner: str
    environment: str
    abort_condition: str
    reconciliation_required: bool
    approved_by: str

    def validate(self) -> None:
        if self.environment == "production":
            raise ValueError("production_experiment_blocked")
        if not all([self.name, self.owner, self.abort_condition, self.approved_by]):
            raise ValueError("experiment_evidence_missing")
        if self.owner == self.approved_by:
            raise ValueError("self_approval_blocked")
        if not self.reconciliation_required:
            raise ValueError("reconciliation_required")
