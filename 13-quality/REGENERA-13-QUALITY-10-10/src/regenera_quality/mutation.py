from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class MutationResult:
    killed: int
    survived: int
    timed_out: int = 0

    @property
    def score(self) -> float:
        total = self.killed + self.survived + self.timed_out
        if total == 0:
            raise ValueError("mutants_required")
        return (self.killed + self.timed_out) * 100.0 / total

    def validate(self, minimum: float, critical_survived: int = 0) -> None:
        if not 0 <= minimum <= 100:
            raise ValueError("invalid_minimum")
        if critical_survived > 0:
            raise ValueError("critical_mutant_survived")
        if self.score < minimum:
            raise ValueError("mutation_score_below_minimum")
