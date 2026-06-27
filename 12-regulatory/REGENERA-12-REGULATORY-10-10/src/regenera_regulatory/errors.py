class RegulatoryError(Exception):
    """Base error for a controlled regulatory failure."""

class ValidationError(RegulatoryError): pass
class ConflictError(RegulatoryError): pass
class AuthorizationError(RegulatoryError): pass
class StateTransitionError(RegulatoryError): pass
class EvidenceError(RegulatoryError): pass
class ExternalDependencyError(RegulatoryError): pass
class UnknownSubmissionError(RegulatoryError): pass
