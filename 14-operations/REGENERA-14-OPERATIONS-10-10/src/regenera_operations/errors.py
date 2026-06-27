class OperationsError(Exception):
    pass

class ValidationError(OperationsError):
    pass

class AuthorizationError(OperationsError):
    pass

class StateTransitionError(OperationsError):
    pass

class IntegrityError(OperationsError):
    pass

class ConflictError(OperationsError):
    pass

class ExternalEvidenceRequired(OperationsError):
    pass
