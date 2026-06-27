from dataclasses import dataclass
from math import ceil

@dataclass(frozen=True, slots=True)
class PerformanceResult:
    p95_ms: int
    error_rate: float
    samples: int


def percentile(values: list[int], p: float) -> int:
    if not values:
        raise ValueError("samples_required")
    if not 0 < p <= 1:
        raise ValueError("invalid_percentile")
    ordered = sorted(values)
    index = max(0, ceil(p * len(ordered)) - 1)
    return ordered[index]


def evaluate(latencies_ms: list[int], failures: int) -> PerformanceResult:
    if failures < 0 or failures > len(latencies_ms):
        raise ValueError("invalid_failure_count")
    if any(v < 0 for v in latencies_ms):
        raise ValueError("negative_latency")
    return PerformanceResult(
        p95_ms=percentile(latencies_ms, 0.95),
        error_rate=failures / len(latencies_ms),
        samples=len(latencies_ms),
    )
