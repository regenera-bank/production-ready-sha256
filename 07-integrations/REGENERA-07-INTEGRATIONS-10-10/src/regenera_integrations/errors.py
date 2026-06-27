class IntegrationError(Exception):
    code = "INTEGRATION_ERROR"


class ValidationError(IntegrationError):
    code = "VALIDATION_ERROR"


class IdempotencyConflict(IntegrationError):
    code = "IDEMPOTENCY_CONFLICT"


class UnsafeRetryBlocked(IntegrationError):
    code = "UNSAFE_RETRY_BLOCKED"


class CircuitOpen(IntegrationError):
    code = "CIRCUIT_OPEN"


class AuthenticationError(IntegrationError):
    code = "AUTHENTICATION_ERROR"
