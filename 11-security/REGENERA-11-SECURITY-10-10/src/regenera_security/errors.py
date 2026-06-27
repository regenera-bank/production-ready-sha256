class SecurityControlError(ValueError):
    """Falha fechada de um controle de segurança."""


class AuthorizationDenied(SecurityControlError):
    pass


class IntegrityViolation(SecurityControlError):
    pass


class InvalidTransition(SecurityControlError):
    pass


class ReleaseBlocked(SecurityControlError):
    pass
