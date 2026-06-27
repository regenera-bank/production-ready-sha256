from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable

from .errors import CircuitOpen, IdempotencyConflict, ValidationError


class Outcome(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class FailurePhase(str, Enum):
    BEFORE_SEND = "BEFORE_SEND"
    AFTER_SEND = "AFTER_SEND"


class TransportFailure(RuntimeError):
    def __init__(self, message: str, *, retryable: bool, phase: FailurePhase):
        super().__init__(message)
        self.retryable = retryable
        self.phase = phase


@dataclass(frozen=True)
class OperationResult:
    outcome: Outcome
    provider_reference: str | None
    response: dict[str, Any]
    attempts: int


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1 or self.max_attempts > 5:
            raise ValidationError("max_attempts fora da faixa permitida")


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3):
        if failure_threshold < 1:
            raise ValidationError("failure_threshold inválido")
        self.failure_threshold = failure_threshold
        self.failures = 0
        self.open = False

    def before_call(self) -> None:
        if self.open:
            raise CircuitOpen("circuito aberto")

    def success(self) -> None:
        self.failures = 0
        self.open = False

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open = True


class IdempotencyRegistry:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], tuple[str, OperationResult]] = {}

    @staticmethod
    def fingerprint(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(raw.encode("utf-8")).hexdigest()

    def get(self, operation: str, key: str, payload: dict[str, Any]) -> OperationResult | None:
        record = self._records.get((operation, key))
        if record is None:
            return None
        fingerprint, result = record
        if fingerprint != self.fingerprint(payload):
            raise IdempotencyConflict("chave reutilizada com payload diferente")
        return result

    def put(self, operation: str, key: str, payload: dict[str, Any], result: OperationResult) -> None:
        self._records[(operation, key)] = (self.fingerprint(payload), result)


Transport = Callable[[dict[str, Any]], tuple[int, dict[str, Any], str | None]]


class IntegrationGateway:
    def __init__(
        self,
        registry: IdempotencyRegistry | None = None,
        breaker: CircuitBreaker | None = None,
    ) -> None:
        self.registry = registry or IdempotencyRegistry()
        self.breaker = breaker or CircuitBreaker()

    def execute(
        self,
        *,
        operation: str,
        idempotency_key: str,
        payload: dict[str, Any],
        financial_effect: bool,
        transport: Transport,
        retry_policy: RetryPolicy | None = None,
    ) -> OperationResult:
        if not operation or not idempotency_key:
            raise ValidationError("operation e idempotency_key são obrigatórios")

        previous = self.registry.get(operation, idempotency_key, payload)
        if previous is not None:
            return previous

        policy = retry_policy or RetryPolicy()
        attempts = 0

        while attempts < policy.max_attempts:
            attempts += 1
            self.breaker.before_call()
            try:
                status, response, provider_reference = transport(payload)
            except TransportFailure as exc:
                self.breaker.failure()

                if exc.phase is FailurePhase.AFTER_SEND:
                    result = OperationResult(Outcome.UNKNOWN, None, {}, attempts)
                    self.registry.put(operation, idempotency_key, payload, result)
                    return result

                if not exc.retryable or attempts >= policy.max_attempts:
                    result = OperationResult(Outcome.REJECTED, None, {"reason": str(exc)}, attempts)
                    self.registry.put(operation, idempotency_key, payload, result)
                    return result

                continue

            self.breaker.success()
            if 200 <= status < 300:
                result = OperationResult(Outcome.SUCCEEDED, provider_reference, response, attempts)
            elif status in {408, 425, 429, 500, 502, 503, 504}:
                if financial_effect:
                    result = OperationResult(Outcome.UNKNOWN, provider_reference, response, attempts)
                    self.registry.put(operation, idempotency_key, payload, result)
                    return result
                if attempts < policy.max_attempts:
                    continue
                result = OperationResult(Outcome.REJECTED, provider_reference, response, attempts)
            else:
                result = OperationResult(Outcome.REJECTED, provider_reference, response, attempts)

            self.registry.put(operation, idempotency_key, payload, result)
            return result

        raise RuntimeError("loop de retry terminou sem resultado")
