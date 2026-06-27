import unittest

from regenera_integrations.errors import CircuitOpen, IdempotencyConflict, ValidationError
from regenera_integrations.kernel import (
    CircuitBreaker,
    FailurePhase,
    IdempotencyRegistry,
    IntegrationGateway,
    Outcome,
    RetryPolicy,
    TransportFailure,
)


class KernelTests(unittest.TestCase):
    def test_success_is_stored_for_replay(self):
        calls = 0
        def transport(payload):
            nonlocal calls
            calls += 1
            return 201, {"ok": True}, "ext-1"
        gateway = IntegrationGateway()
        first = gateway.execute(operation="pix.submit", idempotency_key="k1", payload={"x": 1}, financial_effect=True, transport=transport)
        second = gateway.execute(operation="pix.submit", idempotency_key="k1", payload={"x": 1}, financial_effect=True, transport=transport)
        self.assertEqual(first, second)
        self.assertEqual(calls, 1)

    def test_payload_change_conflicts(self):
        gateway = IntegrationGateway()
        gateway.execute(operation="op", idempotency_key="k", payload={"x": 1}, financial_effect=False, transport=lambda _: (200, {}, None))
        with self.assertRaises(IdempotencyConflict):
            gateway.execute(operation="op", idempotency_key="k", payload={"x": 2}, financial_effect=False, transport=lambda _: (200, {}, None))

    def test_timeout_after_send_becomes_unknown(self):
        gateway = IntegrationGateway()
        result = gateway.execute(
            operation="financial",
            idempotency_key="k",
            payload={"amount": 1},
            financial_effect=True,
            transport=lambda _: (_ for _ in ()).throw(TransportFailure("timeout", retryable=True, phase=FailurePhase.AFTER_SEND)),
        )
        self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(result.attempts, 1)

    def test_unknown_is_replayed_without_second_send(self):
        calls = 0
        def transport(_):
            nonlocal calls
            calls += 1
            raise TransportFailure("timeout", retryable=True, phase=FailurePhase.AFTER_SEND)
        gateway = IntegrationGateway()
        for _ in range(2):
            result = gateway.execute(operation="financial", idempotency_key="k", payload={"x": 1}, financial_effect=True, transport=transport)
            self.assertEqual(result.outcome, Outcome.UNKNOWN)
        self.assertEqual(calls, 1)

    def test_retry_before_send_succeeds(self):
        calls = 0
        def transport(_):
            nonlocal calls
            calls += 1
            if calls < 3:
                raise TransportFailure("connect", retryable=True, phase=FailurePhase.BEFORE_SEND)
            return 200, {"done": True}, "ref"
        gateway = IntegrationGateway(breaker=CircuitBreaker(failure_threshold=5))
        result = gateway.execute(operation="query", idempotency_key="k", payload={"x": 1}, financial_effect=False, transport=transport)
        self.assertEqual(result.outcome, Outcome.SUCCEEDED)
        self.assertEqual(result.attempts, 3)

    def test_non_retryable_failure_is_rejected(self):
        gateway = IntegrationGateway()
        result = gateway.execute(
            operation="query",
            idempotency_key="k",
            payload={"x": 1},
            financial_effect=False,
            transport=lambda _: (_ for _ in ()).throw(TransportFailure("bad request", retryable=False, phase=FailurePhase.BEFORE_SEND)),
        )
        self.assertEqual(result.outcome, Outcome.REJECTED)
        self.assertEqual(result.attempts, 1)

    def test_ambiguous_financial_response_becomes_unknown(self):
        calls = 0
        def transport(_):
            nonlocal calls
            calls += 1
            return 503, {}, None
        gateway = IntegrationGateway()
        first = gateway.execute(operation="pay", idempotency_key="k", payload={"x": 1}, financial_effect=True, transport=transport)
        second = gateway.execute(operation="pay", idempotency_key="k", payload={"x": 1}, financial_effect=True, transport=transport)
        self.assertEqual(first.outcome, Outcome.UNKNOWN)
        self.assertEqual(second, first)
        self.assertEqual(calls, 1)

    def test_non_financial_503_can_retry(self):
        calls = 0
        def transport(_):
            nonlocal calls
            calls += 1
            return (503, {}, None) if calls == 1 else (200, {"ok": True}, None)
        gateway = IntegrationGateway()
        result = gateway.execute(operation="query", idempotency_key="k", payload={"x": 1}, financial_effect=False, transport=transport)
        self.assertEqual(result.outcome, Outcome.SUCCEEDED)
        self.assertEqual(result.attempts, 2)

    def test_circuit_opens(self):
        breaker = CircuitBreaker(failure_threshold=2)
        breaker.failure()
        breaker.failure()
        with self.assertRaises(CircuitOpen):
            breaker.before_call()

    def test_success_resets_circuit(self):
        breaker = CircuitBreaker(failure_threshold=2)
        breaker.failure()
        breaker.success()
        self.assertEqual(breaker.failures, 0)
        self.assertFalse(breaker.open)

    def test_retry_policy_limits_range(self):
        with self.assertRaises(ValidationError):
            RetryPolicy(0)
        with self.assertRaises(ValidationError):
            RetryPolicy(6)

    def test_operation_and_key_are_required(self):
        gateway = IntegrationGateway()
        with self.assertRaises(ValidationError):
            gateway.execute(operation="", idempotency_key="k", payload={}, financial_effect=False, transport=lambda _: (200, {}, None))

    def test_fingerprint_is_order_independent(self):
        registry = IdempotencyRegistry()
        self.assertEqual(registry.fingerprint({"a": 1, "b": 2}), registry.fingerprint({"b": 2, "a": 1}))


if __name__ == "__main__":
    unittest.main()
